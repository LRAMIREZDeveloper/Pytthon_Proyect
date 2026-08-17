import psycopg2
import requests
import logging
import time
from decimal import Decimal

# Configuración del logging
logging.basicConfig(filename='GDE_log.log', level=logging.DEBUG, format='%(message)s')
logger = logging.getLogger(__name__)

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

def norm(v):
    if isinstance(v, Decimal):
        if v == v.to_integral_value():  # revisa si no tiene parte decimal
            return int(v)
        else:
            return float(v)  # o str(v) si prefieres mantener exactitud
    return v


def rechazar_factura(ip, rut, tipo, folio, auth_key):
    url = f"http://{ip}/api/Core.svc/core/SendComercialResponse"
    headers = {
        "AuthKey": auth_key,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    body = {
        "Environment": "P",
        "RutEmisor": rut,
        "DTEType": norm(tipo),     # si tipo/folio pueden venir como Decimal, usa norm(tipo) / norm(folio)
        "Folio": norm(folio),
        "ContactName": "Valentina Lorca",
        "ContactPhone": "+56938697242",
        "ContactEmail": "vlorca@tsm.cl",
        "Observations": "Rechazo realizada a traves de integraciones",
        "ResponseType": "R",
        "Action": "3",
    }

    response = requests.post(url, headers=headers, json=body, timeout=(5, 30))
    print(f"Estado HTTP: {response.status_code}")
    response.raise_for_status()           # ← lanzará HTTPError si no es 2xx
    return response.json()

def main():
    # === CONFIGURACIÓN ===
    ip_dtebox = "200.6.99.113"
    api_auth = "e94a9f68-79c1-4157-83ec-312951533703"

    connection = connect_to_db_tsm()
    if not connection:
        raise RuntimeError("No se pudo abrir conexión a la base de datos")

    query_data = """
        SELECT  
            fd.rutemisor, 
            fd.folio, 
            fd.tipodte
        FROM api.api_facct_service fd
        WHERE fd.can_days >= 7
        AND fd.estado NOT IN ('Completa', 'Anulada')
        AND fmapago = 2
        AND fd.tipodte IN (33, 34)
        AND fd.classification <> 'Servicio básico'
    """
    
    
    query_refused = """
        SELECT * FROM api.update_facct_refused(%s, %s)
    
    """

    with connection:
        with connection.cursor() as cursor:
            cursor.execute(query_data)
            rows = cursor.fetchall()

            if not rows:
                print("Sin facturas para rechazar")
            else:
                for rutemisor, folio, tipodte in rows:
                    
                    # 1) Rechaza en el servicio externo
                    resp = rechazar_factura(ip_dtebox, rutemisor, tipodte, folio, api_auth)
                    print(f"Respuesta API rechazo para folio {folio}: {resp}")

                    result_api = resp.get("Result")
                    description_api = resp.get("Description")

                    refused_data = (result_api == 1 and "Documento ya rechazado" in description_api)

                    if result_api == 0 or refused_data:

                        # 2) Actualiza estado en la BD
                        cursor.execute(query_refused, (folio, rutemisor))
                        result = cursor.fetchone()
                        print(f"Update refused retornó: {result[0] if result else None}")

                    else:

                        descripcion = resp.get("Description", "Sin descripción")

                        print(
                            f"No se actualiza BD para folio {folio}. "
                            f"Result={result_api} "
                            f"Motivo={descripcion}"
                        )

                    time.sleep(5)

def lambda_handler(event, context):
    try:
        main()
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
        }
    except Exception as e:
        logger.exception("Error en Lambda")
        raise   # ← Obligatorio para que CloudWatch cuente Error=1


if __name__ == "__main__":
    main()
