import logging
import psycopg2
from psycopg2.extras import RealDictCursor
import logging
from typing import Any, Dict

from queries import SELECT_NC, SELECT_FACCT_NC, SELECT_VALIDATION_FACCT, SELECT_DM_NC, ADD_CREDIT_NOTE, ADD_CREDIT_NOTE_DM, UPDATE_CREDITNOTE

# Configuración del logging
logging.basicConfig(filename='GDE_creditnote.log', level=logging.DEBUG, format='%(message)s')
logger = logging.getLogger(__name__)


# Constantes de estado
STATUS_VOID = "VO"
STATUS_COMPLETE = "CO"
STATUS_UPDATE = 'RJ'

#=================== Utilidades =========================

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

# =================== RPA NC  ============

def modificar_e_actualizar_data_NC() -> str:
    connection = connect_to_db_tsm()
    with connection, connection.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(SELECT_NC)
        notas_credito = cursor.fetchall()

        # Verifica si no hay resultados
        if not notas_credito:
            return "→ No se encontraron notas de crédito para procesar."

        # Si hay datos, procesarlos
        for doc in notas_credito:
            procesar_nota_credito(cursor, doc)

    return "→ Proceso finalizado."

# Procesa las notas de crédito (NC) registradas en la base de datos,validando su relación con facturas y devoluciones de materiales.
def procesar_nota_credito(cursor, doc: Dict[str, Any]) -> None:
    """Procesa una nota de crédito individual."""
    nota_credito = doc.get('folio')
    rut_emisor = doc.get('rutemisor')
    folioref = doc.get('folioref')
    nc_ref = int(doc.get('nc_ref') or 1)
    netoamount = doc.get('netoamount', 0)
    datetrx = doc.get('fchemis')

    if nc_ref == 2:
        logger.warning(f"Corrige texto de documento de referencia: Folio {nota_credito}")
        return

    # Validacion si tenemos factura en tabla i_facctcontrol.
    cursor.execute(SELECT_FACCT_NC, (folioref, rut_emisor))
    ref_row = cursor.fetchone()
    if ref_row is None:
        logger.info(f"  → No existe registro en i_facctcontrol para folioref={folioref}, rut={rut_emisor}.")
        status = None
    else:
        status = ref_row.get('status')

    if status == STATUS_COMPLETE or status is None:
        validar_factura_en_adempiere(cursor, folioref, nota_credito, rut_emisor, datetrx, netoamount)
    else:
        procesar_nc(cursor, ref_row, nota_credito, netoamount)

# Valida si la factura asociada a una NC existe en Adempiere.
def validar_factura_en_adempiere(cursor, folioref: int, nota_credito: int, rut_emisor: str, datetrx, netoamount) -> None:
    logger.info(f"  → Factura asociada se encuentra completa por nuestro RPA o status = CO en i_facctcontrol para NC={nota_credito} (folio {folioref}). "
                f"Se valida en Adempiere.")
    classification = ''
    devol_id = None
    folioref = int(folioref or 0)
    status = ''
    product_id = None

    # Consultamos los datos de la factura en Adempiere.
    cursor.execute(SELECT_VALIDATION_FACCT, (folioref, rut_emisor))
    facct = cursor.fetchone()

    # Si no se encuentra Factura, no se realiza nada con la NC
    if facct is None:
        logger.info(f"  → No existe registro en Adempiere para Factura {folioref}. "
                    f"No se realiza nada porque la factura está rechazada.\n")
        classification = 'Pendiente - Factura no esta en Adempiere.'
        status = 'DR'
    else:
        # Se extraen campos para validacion de la NC
        docstatus = facct.get('docstatus')
        documentno = str(facct.get('doc_order'))
        ispaid_raw = facct.get('ispaid')
        ispaid = 'Y' if str(ispaid_raw).upper() == 'Y' else 'N'
        neto_facct = int(facct.get('neto') or 0)
        dif = int(netoamount - neto_facct)
        desc = f"/ (Sin diferencias)" if dif == 0 else f"/ (diferencia: {dif})"

        # Si se Factura, pero esta anulada, no se realiza nada con la NC
        if docstatus == STATUS_VOID:
            logger.info(f"  → Existe registro en Adempiere para Factura {folioref} "
                        f"No se realiza nada porque la factura, a pesar de estar en Adempiere, está se encuentra Anulada.\n")
            classification = 'Rechazada - Factura asociada esta anulada en Adempiere.'
            status = 'VO'
        else:
            if documentno:
                # Asegurarse de pasar la tupla correcta de parámetros (documentno, rut_emisor)
                cursor.execute(SELECT_DM_NC, (documentno, rut_emisor ))
                devolucion = cursor.fetchall()
                if devolucion:
                    devol_id = devolucion[0].get('devolucion')
                    product_id = next((r.get('m_product_id') for r in devolucion if r.get('m_product_id')),None)
                else:
                    devol_id = None
                    product_id = None
            else:
                logger.info(f"  → documentno es None o vacío para la factura {folioref}. Se asume que no hay DM.")

            logger.info(f"  → Existe registro en Adempiere para Factura {folioref}. NC {nota_credito} se valida con la devolución de materiales.")

            if devol_id is None: 
                logger.info(f"  → No existe DM para NC={nota_credito}. "
                            f"Se valida si factura mantiene productos asociados.")
                if product_id is None:
                    logger.info(f"  → Factura no mantiene productos, se ingresa NC igual a la factura.")
                    status = 'CO'
                    classification = 'Aprobada -  Se ingresa NC igual a la factura.' 
                    params = (
                        str(nota_credito),
                        str(folioref),
                        rut_emisor,
                        datetrx,
                        desc          
                    )
                    insertar_nc(cursor, params, devol_id, nota_credito, rut_emisor)
                else:
                    status = 'DR'
                    classification = 'Rechazada - Factura presenta producto sin DM.'
                    logger.info(f"  → Factura mantiene productos, no se ingresa NC a la espera de DM.\n")
            else:
                logger.info(f"  → Existe DM={devol_id} para NC={nota_credito}. ")
                status = 'CO'
                params = (
                    str(nota_credito),
                    str(folioref),
                    rut_emisor,
                    datetrx,
                    desc, 
                    ispaid,
                    devol_id,
                    netoamount
                )
                if ispaid == 'Y':
                    logger.info(f"  → Factura ya se encuentra pagada. Se ingresa NC al cargo 1001.\n")
                    classification = 'Aprobada - Se ingresa NC al cargo 1001.' 
                else:
                    logger.info(f"  → Factura no se encuentra pagada. Se ingresa NC igual a la DM.\n")
                    classification = 'Aprobada - Se ingresa NC igual a la DM.'
                insertar_nc(cursor, params, devol_id, nota_credito, rut_emisor)
    
    cursor.execute(UPDATE_CREDITNOTE, (classification, nota_credito, rut_emisor, status, folioref))
    return
    
# Procesa una factura existente relacionada con una NC.
def procesar_nc(cursor, ref_row: Dict[str, Any], nota_credito: int, neto_nc: float) -> None:
    ref_folio = ref_row.get('folio')
    ref_rut = ref_row.get('rutemisor')
    ref_oc = ref_row.get('folioref')
    ref_neto = ref_row.get('netoamount', 0)
    ref_total = ref_row.get('totalamount', 0)
    ref_status = ref_row.get('status')
    ref_clas = ref_row.get('classification_facct')
    diferencia = int(ref_neto - neto_nc)
    classification = ''
    status = ''

    logger.info(f"  → Factura encontrada para NC={nota_credito} (folio={ref_folio}, "
                f"rut={ref_rut}, neto={ref_neto}, total={ref_total}, status={ref_status}, "
                f"clasificación={ref_clas}, OC={ref_oc}). Diferencia={diferencia}")

    if ref_status == STATUS_VOID:
        logger.info(f"  → Factura {ref_folio} está Rechazada. No se ingresa a Adempiere.\n")
        classification = 'Rechazada - RPA rechazo factura asociada, se rechaza NC.'
        status = 'VO'

    elif ref_status == STATUS_UPDATE:
        logger.info(f"  → Factura {ref_folio} asociada a NC ({nota_credito}) ya está en estado RJ. No se actualiza.\n")
        return
    
    else:
        logger.info(f"  → Factura {ref_folio} asociada a NC ({nota_credito}) está Pendiente.\n")
        classification = f'Rechazada - Factura {ref_folio} asociada.'
        status = 'RJ'

    cursor.execute(UPDATE_CREDITNOTE, (classification, nota_credito, ref_rut, status, ref_folio))

    return

# =================== Insercion de Facturas y Notas de Credito ==================

# Inserta Nota de credito en ADempiere.
def insertar_nc(cursor, params: Dict[str, Any], devol_id, nota_credito, rut_emisor):

    # Consultamos los datos de la NC en Adempiere.
    cursor.execute(SELECT_VALIDATION_FACCT, (nota_credito, rut_emisor))
    nc = cursor.fetchone()

    if nc:
        logger.info(f"  → NC no es insertada porque ya existe en ADempiere.\n")  
    else:
        if devol_id is None:
            logger.info(f"  → Se procede a crear NC en base a los parametros de la factura: {params}. \n")
            cursor.execute(ADD_CREDIT_NOTE, params)
        else:
            logger.info(f"  → Se procede a crear NC en base a la DM: {params}. \n")
            cursor.execute(ADD_CREDIT_NOTE_DM, (params))

# =============== Main () ======================================
def main():
    data_nc = modificar_e_actualizar_data_NC()
    print(data_nc)


if __name__ == "__main__":
    main()