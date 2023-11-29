import logging

from connection import connect_to_api, user_login, connect_to_db_tsm_nuevo, call_apis, insert_data_odometer

logging.basicConfig(filename='error_odometer.log', level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)


def main():
    USER_NAME, PASSWORD = user_login()
    server, _, _, context_odometer, _ = call_apis()

    try:
        response = connect_to_api(
            USER_NAME, PASSWORD, server, context_odometer)
        print('HTTP Code: {}'.format(response.getcode()))
        body = response.read().decode('utf-8')
        print("Exito en la conexion a la API Odometros")
    except Exception as e:
        logger.error('Error de conexión a la API Odometros: {}'.format(e))
        return
    finally:
        response.close()

    # Usa 'with' para manejar la conexión y el cursor
    with connect_to_db_tsm_nuevo() as connection:
        with connection.cursor() as cursor:
            if response.getcode() == 200:
                insert_data_odometer(connection, cursor, body)
            else:
                logger.error('HTTP Code: {}'.format(response.getcode()))


if __name__ == "__main__":
    main()
