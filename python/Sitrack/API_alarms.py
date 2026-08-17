import json
import logging

from connection import connect_to_api, user_login, connect_to_db_tsm_nuevo, call_apis, insert_alarm_data

logging.basicConfig(filename='error_alarmsexcel.log', level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(name)s %(message)s ')
logger = logging.getLogger(__name__)


def main():
    # Credenciales de usuario
    USER_NAME, PASSWORD = user_login()
    server, _, context_alarms, _, _, _, _ = call_apis()
    try:
        response = connect_to_api(USER_NAME, PASSWORD, server, context_alarms)
        print('HTTP Code:', response.getcode())
        body = response.read().decode('utf-8')
        print("Éxito en la conexión a la API Alarms")
        if response.getcode() == 200:
            try:
                if body:
                    alarms = json.loads(body)
                else:
                    alarms = []
            except Exception as e:
                logger.exception(f'Error en la lectura de las respuestas: {e}')
                alarms = []
            with connect_to_db_tsm_nuevo() as connection:
                with connection.cursor() as cursor:
                    insert_alarm_data(connection, cursor, alarms)
        elif response.getcode() != 200:
            unauthorized = json.loads(body)
            logger.error(unauthorized.get('message', ''))
    except Exception as e:
        logger.exception(f'Error de conexión a la API Alarms: {e}')

if __name__ == "__main__":
    main()
