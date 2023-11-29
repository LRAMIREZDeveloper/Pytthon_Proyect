import logging

from connection import consume_api_user, connect_to_db_tsm_nuevo, process_api_data

logging.basicConfig(filename='parking_error.log', level=logging.ERROR,
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)

# Función principal


def main():
    try:
        # Realizar la solicitud GET a la API sin verificar el certificado SSL
        api_data = consume_api_user("/person/getPersonList")

        if api_data is not None:
            with connect_to_db_tsm_nuevo() as db_connection:
                db_cursor = db_connection.cursor()
                process_api_data(api_data, db_cursor, db_connection)
                db_connection.commit()
                print("IDs agregados correctamente a la base de datos.")
    except Exception as e:
        logger.error(f'Error: {e}')


if __name__ == "__main__":
    main()
