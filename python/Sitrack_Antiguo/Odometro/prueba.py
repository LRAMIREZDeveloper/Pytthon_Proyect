import json
import logging
import datetime
from connection import connect_to_api, request_new_session, user_login, connect_to_db_tsm, call_api

# Configura el logging
logging.basicConfig(filename='app.log', filemode='w',
                    format='%(name)s - %(levelname)s - %(message)s', level=logging.INFO)

USER_NAME, PASSWORD = user_login()
server, context = call_api()
sessionId, secretKey = request_new_session(server, USER_NAME, PASSWORD)

try:
    response = connect_to_api(sessionId, secretKey, server, context)
    logging.info('HTTP Code: {}'.format(response.getcode()))
except Exception as e:
    logging.error('Error de conexión a la API: {}'.format(e))

try:
    body = response.read().decode('utf-8')
    logging.info("Exito en la conexion a la API")
except Exception as f:
    logging.error('Error de lectura de la respuesta: {}'.format(f))

# Usa 'with' para manejar la conexión y el cursor
with connect_to_db_tsm() as connection:
    with connection.cursor() as cursor:
        if response.getcode() == 200:
            try:
                odometros = json.loads(body)
            except json.JSONDecodeError as g:
                logging.error(
                    'Error en la lectura de la respuesta: {}'.format(g))
            for odometro in odometros:
                created = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                datos = (odometro.get('assetId'),
                         odometro.get('odometer'), created)
                try:
                    cursor.execute(""" INSERT INTO api.testing_odometro(asset_ppu, odometer_amt, created) VALUES (%s, %s, %s);
                    """, datos)
                    connection.commit()
                except Exception as e:
                    logging.error(
                        'Error en la inserción de datos: {}'.format(e))
                    connection.rollback()
        else:
            logging.error('HTTP Code: {}'.format(response.getcode()))