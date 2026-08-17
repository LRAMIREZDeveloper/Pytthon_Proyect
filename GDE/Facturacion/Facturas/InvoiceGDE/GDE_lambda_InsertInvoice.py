import datetime
import requests
import base64
import xml.etree.ElementTree as ET
import datetime
import logging
import psycopg2
from psycopg2.extras import Json
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation

from queries import DATA_CLIENT_SB_C, INSERT_FACCT, SELECT_FACCT, SELECT_FACCT_OC, SELECT_FACCT_OC_DETAIL, SELECT_FACCT_OC_DETAIL2

# Configuración del logging
logging.basicConfig(filename='GDE_log.log', level=logging.DEBUG, format='%(message)s')
logger = logging.getLogger(__name__)

# =============== Conexion BDD ======================================

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


# =============== XML x Factura ======================================

def obtener_xml_desde_json(json_data):
    try:
        # 🔥 Buscar 'Data' o 'data'
        data_base64 = json_data.get("Data") or json_data.get("data")

        if not json_data or not data_base64:
            print("El JSON no contiene el campo 'Data' ni 'data' con contenido base64.")
            return None

        # ← devolvemos bytes, SIN decode
        return base64.b64decode(data_base64)

    except Exception as e:
        print(f"Error al decodificar XML: {str(e)}")
        return None

def obtener_dte_pdf(rut, tipo, folio):
    url = f"http://200.6.99.113/api/Core.svc/core/RecoverXML_V2"
    headers = {
        "AuthKey": "e94a9f68-79c1-4157-83ec-312951533703",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    body = {
        "Environment": "P",
        "Group":"R",
        "Rut": rut,
        "DocType": tipo,
        "Folio": folio,
        "IsForDistribution": "true"
    }

    try:
        response = requests.post(url, headers=headers, json=body)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error HTTP {response.status_code}")
            print(f"Respuesta: {response.text}")
    except Exception as e:
        print(f"Excepción al hacer la solicitud: {str(e)}")

def extraer_detalle(xml_string):
    """
    Procesa un XML en memoria (string) y devuelve una lista de diccionarios con los detalles encontrados.
    No guarda nada en disco, solo devuelve la lista.
    """
    try:
        root = ET.fromstring(xml_string)

        ns = {'sii': 'http://www.sii.cl/SiiDte'}
        detalles = root.findall('.//sii:Detalle', ns)

        lista_detalles = []
        for detalle in detalles:
            nmb_item = detalle.find('sii:NmbItem', ns)
            dsc_item = detalle.find('sii:DscItem', ns)
            nro_linea = detalle.find('sii:NroLinDet', ns)
            qty_item = detalle.find('sii:QtyItem', ns)
            prc_item = detalle.find('sii:PrcItem', ns)
            mont_item = detalle.find('sii:MontoItem', ns)
            
            item_dict = {
                'NmbItem': nmb_item.text if nmb_item is not None else '',
                'DscItem': dsc_item.text if dsc_item is not None else '',
                'NroLinDet': nro_linea.text if nro_linea is not None else '',
                'QtyItem' : qty_item.text if qty_item is not None else '',
                'PrcItem': str(round(float(prc_item.text))) if prc_item is not None and prc_item.text else '',
                'MontoItem': mont_item.text if mont_item is not None else ''
            }
            
            lista_detalles.append(item_dict)

        return lista_detalles

    except Exception as e:
        print(f"Error al procesar el XML: {str(e)}")

# =============== XML x Historico ======================================

def obtener_dte():
    now = datetime.datetime.now()
    current_time = now.strftime('%Y-%m-%d')
    days_ago = (now - datetime.timedelta(days=7)).strftime('%Y-%m-%d')
    ip_dtebox = "200.6.99.113"
    environment = "P"
    group = "R"
    page = 1
    page_size = 500
    api_auth = "e94a9f68-79c1-4157-83ec-312951533703"
    query_text = f"(TimeStamp:[1000-01-01 TO {current_time}] AND TimeStamp:{{{days_ago} TO 9999-12-31}} AND (TipoDTE:33 OR TipoDTE:34) AND RUTRecep:79705390-2)"
    query_encoded = base64.b64encode(query_text.encode()).decode()
    url = f"http://{ip_dtebox}/api/Core.svc/core/PaginatedSearch/{environment}/{group}/{query_encoded}/{page}/{page_size}"
    headers = {
        "AuthKey": api_auth,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    try:
        response = requests.get(url, headers=headers)
        print(f"Estado HTTP: {response.status_code}")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error HTTP {response.status_code}")
            print("Respuesta:", response.text)
            return None

    except Exception as e:
        print(f"Excepción:", str(e))
        return None

def obtener_xml_desde_data(data_base64):
    try:
        xml_bytes = base64.b64decode(data_base64)  # contenido del XML en binario
        return xml_bytes         # lo pasas a string (texto XML)
    except Exception as e:
        print(f"Error al decodificar XML: {str(e)}")
        return None

     
def extraer_campos_desde_xml_string(xml_string):
    """
    Lee el XML desde un string y devuelve una lista de dicts con los campos extraídos.
    No crea archivos.
    """
    try:
        root = ET.fromstring(xml_string)

        documentos = []
        notas_credito_map = {}

        # Primer recorrido: recolectar notas de crédito por su FolioRef
        for doc in root.findall('.//document'):
            tpo_doc_ref = doc.findtext('TpoDocRef')
            folio_ref = doc.findtext('FolioRef')
            if (tpo_doc_ref == '33' or tpo_doc_ref == '34') and folio_ref:
                notas_credito_map.setdefault(folio_ref, []).append(doc)

        # Segundo recorrido: procesar todos los documentos
        for document in root.findall('.//document'):
            doc_info = {}

            folio       = document.find('Folio')
            fch_emis    = document.find('TimeStamp')
            fch_venc    = document.find('FchVenc')
            rut_emisor  = document.find('RUTEmisor')
            folio_ref   = document.find('FolioRef')
            neto        = document.find('NetoAmount')
            docref      = document.find('TpoDocRef')
            met_pago    = document.find('FmaPago')
            type_dte    = document.find('TipoDTE')
            ref_orden   = document.find('FolioRef801')
            n_cliente   = document.find('CdgIntRecep')
            item        = document.find('NmbItem')
            url         = document.find('DownloadCustomerDocumentUrl')
            iva         = document.find('Iva')
            amountotal  = document.find('TotalAmount')
            archive = document.find('TieneArchivo')

            doc_info['FchEmis']                     = fch_emis.text if fch_emis is not None else None
            doc_info['FchVenc']                     = fch_venc.text if fch_venc is not None else None
            doc_info['RUTEmisor']                   = rut_emisor.text if rut_emisor is not None else None
            doc_info['Folio']                       = folio.text if folio is not None else None
            doc_info['FolioRef']                    = folio_ref.text if folio_ref is not None else None
            doc_info['NetoAmount']                  = neto.text if neto is not None else None
            doc_info['TpoDocRef']                   = docref.text if docref is not None else None
            doc_info['FmaPago']                     = met_pago.text if met_pago is not None else None
            doc_info['TipoDTE']                     = type_dte.text if type_dte is not None else None
            doc_info['FolioRef801']                 = ref_orden.text if ref_orden is not None else None
            doc_info['CdgIntRecep']                 = n_cliente.text if n_cliente is not None else None
            doc_info['NmbItem']                     = item.text if item is not None else None
            doc_info['DownloadCustomerDocumentUrl'] = url.text if url is not None else None
            doc_info['Iva']                         = iva.text if iva is not None else None
            doc_info['TotalAmount']                 = amountotal.text if amountotal is not None else None
            doc_info['TieneArchivo']                = archive.text if archive is not None else None

            documentos.append(doc_info)      


        return documentos

    except ET.ParseError as e:
        print(f"Error al parsear XML: {str(e)}")
        return []
    except Exception as e:
        print(f"Error al procesar el XML: {str(e)}")
        return []

    
def procesar_documentos_e_insertar(documentos):
    """
    Procesa la lista de documentos (ya en memoria como lista de dicts)
    y realiza las mismas validaciones/inserciones que antes.
    """
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

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
    clientes_index = {c["rut"]: {"typeclient": c["typeclient"], "status": c["status"]}
                      for c in clientes if c["rut"]}

    for doc in documentos:
        try:
            
            # Extrae campos principales de la factura
            folio = doc.get('Folio')
            fch_emis = doc.get('FchEmis')
            fch_venc = doc.get('FchVenc')
            rut_emisor = doc.get('RUTEmisor')
            rut_emisor_cuerpo = str(rut_emisor).split('-')[0].strip()
            folio_ref = doc.get('FolioRef')
            neto = doc.get('NetoAmount')
            iva = doc.get('Iva')
            total_amount = doc.get('TotalAmount')
            doc_ref = doc.get('TpoDocRef')
            forma_pago = doc.get('FmaPago') if doc.get('FmaPago') and str(doc.get('FmaPago')).strip() else 2
            type_dte = doc.get('TipoDTE')
            doc_ref2 = doc.get('FolioRef801')
            oc_ref = doc_ref2 if doc_ref2 else folio_ref
            note_credit = doc.get('NC')
            n_cliente = doc.get('CdgIntRecep')
            item = doc.get('NmbItem')
            url = doc.get('DownloadCustomerDocumentUrl')
            archive = doc.get('TieneArchivo')

            proveedor_info = clientes_index.get(rut_emisor_cuerpo)
            classification_facct = ''
            dif = 0

            if proveedor_info:

                # --- CAMINO 1: Proveedor existe en BDD ---
                if archive == 'False':
                    print(f"El RUT {rut_emisor} (folio {folio}) es consolidado + SB o C, no se realiza insercion en BDD.")
                    continue
                else:
                    typeclient = proveedor_info['typeclient']
                    status = proveedor_info['status']
                    estado = 'DR' if status == 'I' else 'AJ'
                    classification_facct = (
                        f'{typeclient} - Pendiente de Gestion, Contabilidad.'
                        if status == 'I'
                        else f'{typeclient} - Pendiente de Aprobación, Operaciones.'
                    )
                    clasificacion_oc = None

                    json_resultado = obtener_dte_pdf(rut_emisor, type_dte, folio)
                    xml_data = obtener_xml_desde_json(json_resultado)
                    detalles = extraer_detalle(xml_data)

                    logger.info(f"✅ El RUT {rut_emisor} (folio {folio}) se encontró en la BDD. Tipo: {typeclient}, status: {status}")

            else:
                # --- CAMINO 2: Proveedor NO existe en BDD → se trata como OC ---
                typeclient = 'OC'
                status = None
                detalles = []
                estado = 'DR'
                clasificacion_oc = None

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
                                            (r for r in rows if to_money(r.get('total_inoutline')) == neto_dec), None
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
                        logger.info(f"OC sin clasificación, oc_ref={oc_ref}")
                        classification_facct = 'Rechazada - OC desconocida.'
                else:
                    classification_facct = 'Rechazada - Factura sin OC.'
                    logger.info("Documento sin oc_ref; no se consulta clasificación.")

            cursor.execute(SELECT_FACCT, (folio, rut_emisor))
            exists = cursor.fetchone()

            if exists:
                logger.info(f"No se insertó folio {folio} porque ya existe.\n")
            else:
                cursor.execute(
                    INSERT_FACCT,
                    (
                        folio, fch_emis, fch_venc, rut_emisor, oc_ref, neto, doc_ref, forma_pago,
                        type_dte, note_credit, n_cliente, item, estado, current_time, url,
                        typeclient, status, iva, total_amount, Json(detalles),
                        clasificacion_oc, classification_facct, dif, archive
                    )
                )
                logger.info(f"Insertado folio {folio} en i_facctcontrol.\n")

            logger.info(f"Factura {folio} presenta la siguiente clasificacion: {classification_facct}")
        except Exception as e:
            
            # Error SOLO en este documento → se loguea y sigue con el siguiente
            logger.error(f"Error procesando folio {doc.get('Folio')} del emisor {doc.get('RUTEmisor')}: {str(e)}")
            continue  # pasa al siguiente doc

    # Commit de todo el lote procesado
    connection.commit()

    # Cierre seguro de recursos
    try:
        cursor.close()
        connection.close()
    except:
        pass

# =============== Main () ======================================

def to_money(x):
    if x is None:
        return Decimal('0')  
    try:
        d = Decimal(str(x))
    except (InvalidOperation, ValueError, TypeError):
        d = Decimal('0')
    return d.quantize(Decimal('1'), rounding=ROUND_HALF_UP)
    

def main():
    resultado = obtener_dte()

    if not resultado:
        print("No se pudo obtener resultado de la API.")
        return

    data_base64 = resultado.get('Data') or resultado.get('data')
    if not data_base64:
        print("No se encontró el campo 'Data' en el resultado.")
        return

    xml_string = obtener_xml_desde_data(data_base64)
    if not xml_string:
        print("No se pudo decodificar el XML desde 'Data'.")
        return

    documentos = extraer_campos_desde_xml_string(xml_string)
    if not documentos:
        print("No se extrajeron documentos desde el XML.")
        return

    procesar_documentos_e_insertar(documentos)
    print(f"Se extrajeron {len(documentos)} documentos para ingresar en Adempiere.")
    


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
