import requests
import base64
import json
import xml.etree.ElementTree as ET
import datetime
import pandas as pd
import logging
import psycopg2
from psycopg2.extras import Json
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation

from queries import DATA_CLIENT_SB_C, INSERT_FACCT, SELECT_FACCT, SELECT_FACCT_OC, SELECT_FACCT_OC_DETAIL, SELECT_FACCT_OC_DETAIL2

# Configuración del logging
logging.basicConfig(filename='GDE_log.log', level=logging.DEBUG, format='%(message)s')
logger = logging.getLogger(__name__)


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
        print(f"🔄 Estado HTTP: {response.status_code}")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Error HTTP {response.status_code}")
            print("📄 Respuesta:", response.text)
            return None

    except Exception as e:
        print(f"❌ Excepción:", str(e))
        return None

def guardar_xml_desde_data(data_base64, nombre_archivo):
    try:
        xml_bytes = base64.b64decode(data_base64)
        with open(nombre_archivo, 'wb') as f:
            f.write(xml_bytes)
            
    except Exception as e:
        print(f"Error al guardar XML: {str(e)}")

def guardar_xml_desde_json(json_data, output_path):
    if json_data and json_data.get("Data"):
        try:
            xml_content = base64.b64decode(json_data["Data"])
            with open(output_path, "wb") as f:
                f.write(xml_content)
        except Exception as e:
            print(f"Error al guardar el XML: {str(e)}")
    else:
        print("El campo 'Data' está vacío o no contiene información.")
        print("Mensaje:", json_data.get("Description", "Sin descripción") if json_data else "Sin respuesta")

     
def extraer_campos_y_guardar_json(nombre_xml, nombre_json):
    try:
        tree = ET.parse(nombre_xml)
        root = tree.getroot()

        documentos = []

        # Primer recorrido: recolectar notas de crédito por su FolioRef
        for doc in root.findall('.//document'):
            folio_ref = doc.findtext('FolioRef')


        # Segundo recorrido: procesar todos los documentos
        for document in root.findall('.//document'):
            doc_info = {}

            # Campos comunes
            folio = document.find('Folio')
            fch_emis = document.find('TimeStamp')
            fch_venc = document.find('FchVenc')
            rut_emisor = document.find('RUTEmisor')
            folio_ref = document.find('FolioRef')
            neto = document.find('NetoAmount')
            docref = document.find('TpoDocRef')
            met_pago = document.find('FmaPago')
            type_dte = document.find('TipoDTE')
            ref_orden = document.find('FolioRef801')
            n_cliente = document.find('CdgIntRecep')
            item = document.find('NmbItem')
            url = document.find('DownloadCustomerDocumentUrl')
            iva = document.find('Iva')
            amountotal = document.find('TotalAmount')
            received = document.find('Recibido')
            archive = document.find('TieneArchivo')
            

            doc_info['FchEmis'] = fch_emis.text if fch_emis is not None else None
            doc_info['FchVenc'] = fch_venc.text if fch_venc is not None else None
            doc_info['RUTEmisor'] = rut_emisor.text if rut_emisor is not None else None
            doc_info['Folio'] = folio.text if folio is not None else None
            doc_info['FolioRef'] = folio_ref.text if folio_ref is not None else None
            doc_info['NetoAmount'] = neto.text if neto is not None else None
            doc_info['TpoDocRef'] = docref.text if docref is not None else None
            doc_info['FmaPago'] = met_pago.text if met_pago is not None else None
            doc_info['TipoDTE'] = type_dte.text if type_dte is not None else None
            doc_info['FolioRef801'] = ref_orden.text if ref_orden is not None else None
            doc_info['CdgIntRecep'] = n_cliente.text if n_cliente is not None else None
            doc_info['NmbItem'] = item.text if item is not None else None
            doc_info['DownloadCustomerDocumentUrl'] = url.text if url is not None else None
            doc_info['Iva'] = iva.text if iva is not None else None
            doc_info['TotalAmount'] = amountotal.text if amountotal is not None else None
            doc_info['Recibido'] = received.text if received is not None else None
            doc_info['TieneArchivo'] = archive.text if archive is not None else None

            documentos.append(doc_info)

        if documentos:
            print(f"Se extrajeron {len(documentos)} documentos. Guardando en '{nombre_json}'...")
            with open(nombre_json, 'w', encoding='utf-8') as f:
                json.dump(documentos, f, ensure_ascii=False, indent=2)
        else:
            print("No se encontraron documentos con los campos solicitados.")

    except Exception as e:
        print(f"Error al procesar el XML: {str(e)}")



def to_money(x):
    if x is None:
        return Decimal('0.00')
    try:
        d = Decimal(str(x))
    except (InvalidOperation, ValueError, TypeError):
        d = Decimal('0')
    return d.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
