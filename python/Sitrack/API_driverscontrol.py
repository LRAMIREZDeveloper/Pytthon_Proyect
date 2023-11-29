import logging

from connection import connect_to_api_driverscontrol, user_login, request_session, process_insert_driverscontrol_data, call_apis

# Configuración del logging
logging.basicConfig(filename='app.log', level=logging.ERROR,
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)

def main():
    # Credenciales de usuario
    USER_NAME, PASSWORD = user_login()

    # Dirección de servidor y contexto de las APIs
    SERVER, PATH_SPEED, _, _, PATH_STOPPED = call_apis()

    # Solicitud de sesión
    SESSIONID, SECRETKEY = request_session(SERVER, USER_NAME, PASSWORD)

    # Procesar e insertar datos de la API de velocidad y detenciones
    for context in [PATH_SPEED, PATH_STOPPED]:
        try:
            response = connect_to_api_driverscontrol(
                SESSIONID, SECRETKEY, SERVER, context)
            print('HTTP Code:', response.getcode())
            process_insert_driverscontrol_data(response, 'VE' if context == PATH_SPEED else 'DE')
        except Exception as e:
            logger.error(f'Error de conexión a la API Driverscontrol, tipo: {context} Error:  {e}')

if __name__ == "__main__":
    main()
