import logging
import psycopg2
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
import requests
import logging
from datetime import datetime, date
import time

from queries import UPDATE_FACCT_DATA, SELECT_FACCT_OC, SELECT_FACCT_OC_DETAIL, SELECT_FACCT_OC_DETAIL2, DATA_CLIENT_SB_C, SELECT_FACCT_DATA_REC, QUERY_INSERT, QUERY_DATA, SELECT_VALIDATION_FACCT, UPDATE_FACCT_EXIST

# Configuración del logging
logging.basicConfig(filename='GDE_log_reclassification.log', level=logging.DEBUG, format='%(message)s')
logger = logging.getLogger(__name__)

# ================== Utilidades ==================
def to_date(v):
    if isinstance(v, date) and not isinstance(v, datetime):
        return v
    if isinstance(v, datetime):
        return v.date()
    if isinstance(v, str):
        # admite ISO con o sin zona
        return datetime.fromisoformat(v.replace('Z', '+00:00')).date()
    return None  # o lanza excepción

def norm(v):
    if isinstance(v, Decimal):
        try:
            return int(v)  # si es entero
        except Exception:
            return float(v)  # o str(v) si prefieres
    return v

def is_nonzero(x):
    try:
        return Decimal(str(x)) != 0
    except Exception:
        return False

def to_money(x):
    if x is None:
        return Decimal('0')  
    try:
        d = Decimal(str(x))
    except (InvalidOperation, ValueError, TypeError):
        d = Decimal('0')
    return d.quantize(Decimal('1'), rounding=ROUND_HALF_UP)
    
# ================== Conexión DB ==================

# Conexion a BDD
def connect_to_db_tsm():
    try:
        conn = psycopg2.connect(
            host="adempiere.tsm.cl",
            database="tsm",
            user="pg_api",
            password="8YR53mDRavJlfd6d",
            port=5432
        )
        logger.info("Conexion exitosa a la BDD")
        return conn
    except psycopg2.Error as e:
        logger.error(f"Conexion fallida, error: {e}")
        return None


# ================== Extraccion de datos y reclasificar ==================
 
def procesar_json_e_insertar():
    connection = connect_to_db_tsm()
    cursor = connection.cursor()
    cursor.execute(DATA_CLIENT_SB_C)

    rows = cursor.fetchall()

    clientes = [
        {
            "rut": str(r[0]).strip() if r[0] is not None else "",
            "typeclient": str(r[1]).strip() if r[1] is not None else "",
            "status": str(r[2]).strip() if r[2] is not None else "",
        }
        for r in rows
    ]

    # Índice por RUT para lookup O(1). Si hay duplicados, la última fila gana.
    clientes_index = {}
    for c in clientes:
        if c["rut"]:
            clientes_index[c["rut"]] = {"typeclient": c["typeclient"], "status": c["status"]}

    # --- Procesar JSON de facturas ---
    cursor.execute(SELECT_FACCT_DATA_REC)
    rows = cursor.fetchall()
    cols = [c[0] for c in cursor.description]
    documentos = [dict(zip(cols, r)) for r in rows]

    for doc in documentos:
        folio = doc.get('folio')
        oc_ref = doc.get('folioref')
        neto = doc.get('netoamount')
        total_amount = doc.get('totalamount')
        rut_emisor = doc.get('rutemisor')
        rut_emisor_cuerpo = str(rut_emisor).split('-')[0].strip() 

        proveedor_info = clientes_index.get(rut_emisor_cuerpo)

        classification_facct = ''
        clasificacion_oc = None
        estado = 'DR'
        dif = 0

        if proveedor_info:
            typeclient = proveedor_info['typeclient']
            status = proveedor_info['status']
            classification_facct = (
                f'{typeclient} - Pendiente de Gestion, Contabilidad.'
                if status == 'I'
                else f'{typeclient} - Pendiente de Aprobación, Operaciones.'
            )
            clasificacion_oc = None
            logger.info(f"El RUT {rut_emisor} (folio {folio}) se encontró en la BDD.") 
        else:
            if oc_ref:
                cursor.execute(SELECT_FACCT_OC, (oc_ref,))
                row = cursor.fetchone()
                neto_dec = to_money(total_amount if neto == 0 else neto)

                if row:
                    clasificacion_oc = row[0]

                    if clasificacion_oc == 'RM':
                        cursor.execute(SELECT_FACCT_OC_DETAIL, (oc_ref,))
                        rows_rm = cursor.fetchall()

                        if rows_rm:
                            cols = [c[0].lower() for c in cursor.description]
                            rows = [dict(zip(cols, r)) for r in rows_rm]

                            grandtotal = rows[0].get('grandtotal_inout')
                            grand_dec = to_money(grandtotal)
                            dif = abs(neto_dec - grand_dec)
                            margen = Decimal('1000.00')

                            if grand_dec == neto_dec:
                                classification_facct = 'Recepcionar - RM, recepcion completa de RM.'
                            elif dif <= margen:
                                classification_facct = 'Recepcionar - RM, recepcion completa de RM con diferencias.'
                            else:
                                total_poreference = sum(
                                    Decimal(str(r.get('total_inoutline', 0)))
                                    for r in rows if r.get('poreference') == str(folio)
                                )
                                total_po = to_money(total_poreference)

                                if total_po == neto_dec:
                                    classification_facct = 'Recepcionar - RM/PO, recepcion completa de RM '
                                    dif = 0
                                else:
                                    match = next(
                                        (r for r in rows if to_money(r.get('total_inoutline')) == neto_dec),
                                        None
                                    )
                                    if match:
                                        classification_facct = 'Recepcionar - RM, recepcion por linea de RM.'
                                        dif = 0
                                    else:
                                        classification_facct = 'Rechazada - RM, descuadre en los montos.'
                        else:
                            classification_facct = 'Rechazada - Factura sin RM.'
                    else:
                        cursor.execute(SELECT_FACCT_OC_DETAIL2, (oc_ref,))
                        rows_oc = cursor.fetchone()

                        if rows_oc:
                            oc_total = to_money(rows_oc[0])
                            dif = abs(neto_dec - oc_total)
                            margen = Decimal('1000.00')

                            if neto_dec <= oc_total:
                                classification_facct = 'Pendiente - OC, esperando aprobacion.'
                                estado = 'AJ'
                                dif = 0
                            elif dif <= margen:
                                classification_facct = 'Pendiente - OC con diferencias, esperando aprobacion.'
                                estado = 'AJ'
                            else:
                                classification_facct = 'Rechazada - OC, descuadre en los montos.'
                        else:
                            classification_facct = 'Rechazada - No se encontro OC'
                else:
                    classification_facct = 'Rechazada - OC desconocida.'
                    
                cursor.execute(
                    UPDATE_FACCT_DATA,
                    (clasificacion_oc, classification_facct, estado, dif, folio, rut_emisor)
                )
            else:
                print("Documento sin oc_ref; no se realiza el Update", folio)

    connection.commit()
    cursor.close()
    connection.close()

# ================== Llamada a la API y aprobación de factura ==================

def gte_approver_facct(ip, rut, tipo, folio, auth_key):
    url = f"http://{ip}/api/Core.svc/core/SendComercialResponse"
    headers = {
        "AuthKey": auth_key,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
 
    body = {
    "Environment" : "P", 
    "RutEmisor" : rut, 
    "DTEType" : norm(tipo), 
    "Folio" : norm(folio), 
    "ContactName" : "Valentina Lorca", 
    "ContactPhone" : "+56938697242", 
    "ContactEmail" : "vlorca@tsm.cl", 
    "Observations" : "Aprobacion realizada a traves de integraciones", 
    "ResponseType" : "A", 
    "Action" : "0" 
} 
    response = requests.post(url, headers=headers, json=body)
    print(f"Estado HTTP: {response.status_code}")

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error HTTP {response.status_code}")
        print("Respuesta:", response.text)
        return None


def aprobacion_facturas():
    # === CONFIGURACIÓN ===
    ip_dtebox = "200.6.99.113"
    api_auth = "e94a9f68-79c1-4157-83ec-312951533703"

    connection = connect_to_db_tsm()
    if not connection:
        # Que Lambda lo marque como error real
        raise RuntimeError("No se pudo abrir conexión a la base de datos")

    # with connection: commit si no hay excepciones; rollback si ocurre alguna
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(QUERY_DATA)
            rows = cursor.fetchall()

            for linedata in rows:
                (rutemisor, folio, tipodte, movementdate, nmbitem, netoamount,
                 mnttotal, oc, ad_org_id, difference_detected, difference, line) = linedata

                p_datetrx = to_date(movementdate)

                desc = nmbitem or ""
                if is_nonzero(difference):
                    desc = f"{nmbitem} (diferencia: {difference})"

                # Parámetros correctos para la función add_invoice
                params = (
                    ad_org_id,                   # p_org_id
                    rutemisor.split('-')[0],     # p_bpartner_value (solo número sin DV)
                    str(folio),                  # p_documentno
                    str(tipodte),                # p_doctype
                    'Credito',                   # p_paymentterm
                    p_datetrx,                   # p_datetrx (date)
                    desc,                        # p_description
                    netoamount,                  # p_totallines
                    mnttotal,                    # p_grandtotal
                    oc,                          # p_order
                    difference_detected,         # p_difference_detected
                    100,                     # Usuario aprobador automático (SuperUser)
                    line                         # p_line (JSON string)
                )

                cursor.execute(SELECT_VALIDATION_FACCT, (folio, rutemisor))
                exists = cursor.fetchone()
                
                if exists:
                    print(f"No se insertó folio {folio} porque ya existe.\n")
                    cursor.execute(UPDATE_FACCT_EXIST, (folio,rutemisor))
                else:    
                    # Si falla aquí, saltará excepción -> Lambda marca error
                    cursor.execute(QUERY_INSERT, params)
                    result = cursor.fetchone()
                    print(f"Factura insertada: {result}")

                # Si la API falla, también queremos que explote
                json_resultado = gte_approver_facct(ip_dtebox, rutemisor, tipodte, folio, api_auth)
                logger.info(f"Aprobación API: {json_resultado}")

                # Espera 5s entre iteraciones
                time.sleep(5)

# ================== Orquestación ==================

def main():
    try:
        # Solo corre el segundo si este no falla
        procesar_json_e_insertar()
        aprobacion_facturas()
    except Exception as e:
        logger.error(f"Error en la ejecución: {e}")
        print(f"Se detuvo la ejecución porque procesar_json_e_insertar falló: {e}")
        raise
        
        
def lambda_handler(event, context):
    try:
        # Ejecuta tu main actual (déjalo tal cual)
        main()
        # Respondemos OK aunque main no retorne nada
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
        }
    except Exception as e:
        logger.exception("Error en Lambda")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
        }
