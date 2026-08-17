import logging

from connection import (
    connect_to_api_driverscontrol,
    user_login,
    request_session,
    process_insert_driverscontrol_data,
    call_apis
)

# Configuración del logging
logging.basicConfig(
    filename='app.log',
    level=logging.ERROR,
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    # Credenciales de usuario
    USER_NAME, PASSWORD = user_login()

    # Dirección de servidor y contexto de la API
    SERVER, _, _, _, PATH_STOPPED, _ = call_apis()

    # Solicitud de sesión
    SESSIONID, SECRETKEY = request_session(SERVER, USER_NAME, PASSWORD)

    # Procesar solo DETENCIONES
    try:
        response = connect_to_api_driverscontrol(
            SESSIONID,
            SECRETKEY,
            SERVER,
            PATH_STOPPED
        )

        print('HTTP Code:', response.getcode())

        # 'DE' = Detenciones
        process_insert_driverscontrol_data(response, 'DE')

    except Exception as e:
        logger.error(
            f'Error de conexión a la API Driverscontrol (DETENCIONES): {e}'
        )

if __name__ == "__main__":
    main()
