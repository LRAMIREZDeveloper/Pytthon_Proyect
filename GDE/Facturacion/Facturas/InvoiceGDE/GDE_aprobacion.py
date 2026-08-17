import psycopg2
import requests
import logging
from datetime import datetime, date
from decimal import Decimal

from queries import QUERY_DATA, QUERY_INSERT

# Configuración del logging
logging.basicConfig(filename='GDE_log.log', level=logging.DEBUG, format='%(message)s')
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

# ================== Conexión DB ==================

# Conexión a la BDD
def connect_to_db_tsm():
    try:
        conn = psycopg2.connect(
            host="adempiere.tsm.cl",
            database="tsm",
            user="pg_api",
            password="8YR53mDRavJlfd6d",
            port=5432
        )
        logger.info("Conexión exitosa a la BDD")
        return conn
    except psycopg2.Error as e:
        logger.error(f"Conexión fallida, error: {e}")
        return None

# ================== Llamada a la API ==================

def aprobar_factura(ip, rut, tipo, folio, auth_key):
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
    "ContactName" : "Luis R.", 
    "ContactPhone" : "+56989551020", 
    "ContactEmail" : "lramirez@tsm.cl", 
    "Observations" : "Rechazo realizada a traves de integraciones", 
    "ResponseType" : "A", 
    "Action" : "0" 
} 

    try:
        response = requests.post(url, headers=headers, json=body)
        print(f"🔄 Estado HTTP: {response.status_code}")

        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Error HTTP {response.status_code}")
            print("📄 Respuesta:", response.text)
            return None

    except Exception as e:
        print("❌ Excepción al hacer la solicitud:", str(e))
        return None

# ================== Orquestación ==================

def main():
        # === CONFIGURACIÓN ===
    ip_dtebox = "200.6.99.113"
    api_auth = "e94a9f68-79c1-4157-83ec-312951533703"
    
    connection = connect_to_db_tsm()
    
    if not connection:
        return
    
    cursor = connection.cursor()
    
    try:
        cursor.execute(QUERY_DATA)
        rows = cursor.fetchall()

        for linedata in rows:
            rutemisor, folio, tipodte, movementdate, nmbitem, netoamount, mnttotal, oc, ad_org_id, difference_detected, difference, line = linedata
            
            p_datetrx = to_date(movementdate)
            
            desc = nmbitem or ""
            if is_nonzero(difference):
                desc = f"{nmbitem} (diferencia: {difference})"

            # Parámetros correctos para la función add_invoice
            params = (
                ad_org_id,                # p_org_id
                rutemisor.split('-')[0],  # p_bpartner_value (solo número sin DV)
                str(folio),               # p_documentno
                str(tipodte),             # p_doctype
                'Credito',                # p_paymentterm (valor hardcodeado, cámbialo si es necesario)
                p_datetrx,                # p_datetrx
                desc,                     # p_description
                netoamount,               # p_totallines
                mnttotal,                 # p_grandtotal
                oc,                       # p_order
                difference_detected,      # p_difference_detected
                1000000,                  # Usuario aprobador automatico(SuperUser)
                line                      # p_line (JSON string)
            )
            try:
                cursor.execute(QUERY_INSERT, params)
                result = cursor.fetchone()
                logger.info(f"Factura insertada: {result}")

                json_resultado = aprobar_factura(ip_dtebox, rutemisor, tipodte, folio, api_auth)
                logger.info(f"Aprobación API: {json_resultado}")
            except Exception as e:
                connection.rollback()  # deshace solo esta fila
                logger.error(f"Error en folio {folio}: {e}")
                print(f"❌ Error en folio {folio}: {e}")
                continue  # sigue con la siguiente fila

        connection.commit()
    except Exception as e:
        logger.error(f"Error durante la ejecución: {e}")
        print(f"Error: {e}")
    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    main()
