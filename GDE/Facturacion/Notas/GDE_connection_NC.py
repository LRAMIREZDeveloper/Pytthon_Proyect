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

from queries_NC import DATA_CLIENT_SB_C, INSERT_FACCT, SELECT_FACCT, SELECT_FACCT_OC, SELECT_FACCT_OC_DETAIL, SELECT_FACCT_OC_DETAIL2

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
    days_ago = (now - datetime.timedelta(days=10)).strftime('%Y-%m-%d')
    ip_dtebox = "200.6.99.113"
    environment = "P"
    group = "R"
    page = 1
    page_size = 500
    api_auth = "e94a9f68-79c1-4157-83ec-312951533703"
    query_text = f"(FchEmis:[1000-01-01 TO {current_time}] AND FchEmis:{{{days_ago} TO 9999-12-31}} AND (TipoDTE:61 OR TipoDTE:56) AND RUTRecep:79705390-2)"
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
          
def extraer_campos_y_guardar_json(nombre_xml, nombre_json):
    try:
        tree = ET.parse(nombre_xml)
        root = tree.getroot()

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

            # Campos comunes
            folio = document.find('Folio')
            fch_emis = document.find('FchEmis')
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
            cod_ref = document.find('CodRef')

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
            doc_info['CodRef'] = cod_ref.text if cod_ref is not None else None

            # Campo nuevo: NC
            if type_dte is not None and type_dte.text in ('33', '34') and folio is not None:
                doc_info['NC'] = 'Sí' if folio.text in notas_credito_map else 'No'

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
       
def procesar_json_e_insertar(nombre_json):
    try:
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        connection = connect_to_db_tsm()
        cursor = connection.cursor()
        cursor.execute(DATA_CLIENT_SB_C)
        
        rows = cursor.fetchall()
        
        # Crear DataFrame con la base de clientes (rut, typeclient, status)
        df_clientes = pd.DataFrame(rows, columns=['rut', 'typeclient', 'status'])
        
        # Normalización básica para comparaciones limpias
        df_clientes['rut'] = df_clientes['rut'].astype(str).str.strip()
        df_clientes['typeclient'] = df_clientes['typeclient'].astype(str).str.strip()
        
        # --- Procesar JSON de facturas ---
        with open(nombre_json, 'r', encoding='utf-8') as f:
            documentos = json.load(f)
            
            for doc in documentos:
                # Extrae campos principales de la factura
                folio = doc.get('Folio')
                fch_emis = doc.get('FchEmis')
                fch_venc = doc.get('FchVenc')
                rut_emisor = doc.get('RUTEmisor')
                rut_emisor_cuerpo = str(rut_emisor).split('-')[0].strip()   # solo la parte numérica del RUT
                folio_ref = doc.get('FolioRef')
                neto = doc.get('NetoAmount')
                iva = doc.get('Iva')
                total_amount = doc.get('TotalAmount') 
                doc_ref = doc.get('TpoDocRef')
                # Si no viene forma de pago válida, se usa 2 por defecto
                forma_pago = doc.get('FmaPago') if doc.get('FmaPago') and str(doc.get('FmaPago')).strip() else 2
                type_dte = doc.get('TipoDTE')
                # oc_ref: usa FolioRef801 si existe; de lo contrario usa FolioRef
                doc_ref2 = doc.get('FolioRef801')
                oc_ref = doc_ref2 if doc_ref2 else folio_ref
                note_credit = doc.get('NC')
                n_cliente = doc.get('CdgIntRecep')
                item = doc.get('NmbItem')
                url = doc.get('DownloadCustomerDocumentUrl')

                # --- Verifica duplicados antes de insertar en i_facctcontrol ---
                cursor.execute(SELECT_FACCT, (folio, rut_emisor))
                exists = cursor.fetchone()

                if exists:
                    # Si ya existe ese (folio, rut_emisor) no inserta de nuevo
                    logger.info(f"⚠️ No se insertó folio {folio} porque ya existe.\n")
                else:
                    logger.info(f"✅ Insertado folio {folio} en i_facctcontrol.\n")
            
            # Commit de todo el lote procesado
            connection.commit()                
    except Exception as e:
        # Error de proceso general
        logger.error(f"Error al procesar JSON: {str(e)}")
    
    finally:
        # Cierre seguro de recursos
        try:
            cursor.close()
            connection.close()
        except:
            pass
