import logging
from connection import connect_to_db_tsm_nuevo, API_connection, insert_checklist_data

# Configuración del logging
logging.basicConfig(filename='errors_checklist.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)


def main():
    # Validar la conexión a la API
    data = API_connection()
    if data is not None:
        logger.info("Conexión a la API exitosa.")
    else:
        logger.error("No se pudo conectar a la API.")
        exit(1)

    # Conectar a la base de datos con bloque de contexto
    try:
        with connect_to_db_tsm_nuevo() as conn:
            with conn.cursor() as cur:
                insert_checklist_data(cur, data)
                conn.commit()
    except ConnectionError as e:
        logger.error("No se pudo conectar a la base de datos: {}".format(e))
        exit(1)

if __name__ == "__main__":
    main()
