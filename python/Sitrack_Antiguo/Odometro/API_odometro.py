import json
import datetime
import logging
from connection import connect_to_api, request_new_session, user_login, connect_to_db_tsm, call_api

logging.basicConfig(filename='error_odometer.log', level=logging.ERROR,
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)

USER_NAME, PASSWORD = user_login()
server, context = call_api()
sessionId, secretKey = request_new_session(server, USER_NAME, PASSWORD)

try:
    response = connect_to_api(sessionId, secretKey, server, context)
    print('HTTP Code: {}'.format(response.getcode()))
except Exception as e:
    logger.error('Error de conexión a la API: {}'.format(e))

try:
    body = response.read().decode('utf-8')
    print("Exito en la conexion a la API")
except Exception as f:
    logger.error('Error de lectura de la respuesta: {}'.format(f))

# Usa 'with' para manejar la conexión y el cursor
with connect_to_db_tsm() as connection:
    with connection.cursor() as cursor:
        if response.getcode() == 200:
            try:
                odometros = json.loads(body)
            except json.JSONDecodeError as g:
                logger.error(
                    'Error en la lectura de la respuesta: {}'.format(g))

            created = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            for odometro in odometros:
                datos = (odometro.get('assetId'),
                         odometro.get('odometer'), created)
                try:
                    cursor.execute(""" INSERT INTO api.testing_odometro(asset_ppu, odometer_amt, created) VALUES (%s, %s, %s);
                    """, datos)
                    connection.commit()
                except Exception as e:
                    logger.error(
                        'Error en la inserción de datos: {}'.format(e))
                    connection.rollback()
        else:
            logger.error('HTTP Code: {}'.format(response.getcode()))
