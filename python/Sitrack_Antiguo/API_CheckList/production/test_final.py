# Importar las librerías
import logging
from function import clean_rut, connect_to_db_tsm, API_connection

# Configuración del logging
logging.basicConfig(filename='errors.log', level=logging.ERROR, format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)

# Validar la conexión a la API
data = API_connection()

if data is None:
    logger.error("No se pudo conectar a la API.")
    exit(1)

logger.info("Conexión a la API exitosa.")

# Iterar a través de los datos y guardarlos en la base de datos
try:
    conn = connect_to_db_tsm()
except Exception as e:
    logger.error("No se pudo conectar a la base de datos.")
    exit(1)

with conn:
    with conn.cursor() as cur:
        result = data.get('result', {})
        checklist = result.get('checkList', [])
        void = False
        for check in checklist:
            fleet = check.get('fleet', '')
            report_id = check.get('reportId', '')
            report_date = check.get('reportDate', '')
            driver = check.get('driver', {})
            driver_rut = clean_rut(driver.get('document', ''))
            observation = check.get('observation', '')
            domain = check.get('domain', '')
            verificationCode = check.get('verificationCode', '')
            ramp = check.get('ramp', '')
            questions = check.get('question', [])
            for question in questions:
                question_response = question.get('response', '')
                question_id = question.get('id', '')

                try:
                    # Insertar los datos en la base de datos
                    cur.execute(
                        "INSERT INTO i_checklist (report_id, report_date, driver_value, observation, asset_value, m_checklist_question_id, project_name, response, void, ramp) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                        (report_id, report_date, driver_rut, observation, domain, question_id, fleet, question_response, void, ramp))
                    conn.commit()
                except Exception as e:
                    logger.error("Error al insertar en la base de datos:", exc_info=True)
                    conn.rollback()
