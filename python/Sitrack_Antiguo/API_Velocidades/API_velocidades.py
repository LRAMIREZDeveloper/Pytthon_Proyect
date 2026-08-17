import json
import datetime
import logging

from conexion import user_login, request_new_session, call_api_stopped, connect_to_api_stopped

logging.basicConfig(filename='error_driverscontrol.log', level=logging.ERROR, format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)


# Credenciales de usuario
USER_NAME, PASSWORD = user_login()
server, context2 = call_api_stopped()

# if sessionId is None:
sessionId, secretKey = request_new_session(server, USER_NAME, PASSWORD)

try:
    response2 = connect_to_api_stopped(sessionId, secretKey, server, context2)
    print('HTTP Code:', response2.getcode())
except Exception as e:
    logger.error(f'Error de conexión a la API: {e}')

try:
    body2 = response2.read().decode('utf-8')
except Exception as f:
    logger.error(f'Error de lectura de la respuesta 2: {f}')


if response2.getcode() == 200:
    body2 = '[' + body2 + ']'
    print(body2)

