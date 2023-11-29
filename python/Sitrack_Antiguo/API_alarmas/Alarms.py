import json
import logging

from functions2 import clean_rut, connect_to_api, request_new_session, user_login, connect_to_db_tsm, call_api

logging.basicConfig(filename='error_alarms.log', level=logging.ERROR,
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)

# Credenciales de usuario
USER_NAME, PASSWORD = user_login()

# Dirección de servidor y contexto de la API
server, context = call_api()

try:
    # Si no existe una sesión activa, se solicita una nueva
    sessionId, secretKey = request_new_session(server, USER_NAME, PASSWORD)

    # Intentar conectar a la API
    response = connect_to_api(sessionId, secretKey, server, context)
    print('HTTP Code:', response.getcode())

    # Se lee el contenido de la respuesta
    body = response.read().decode('utf-8')
    print("Éxito en la conexión a la API")

    if response.getcode() == 200:
        try:
            if body:
                alarms = json.loads(body)
            else:
                alarms = []
        except Exception as g:
            logger.error(f'Error en la lectura de las respuestas: {g}')

        with connect_to_db_tsm() as connection:
            with connection.cursor() as cursor:
                if alarms:
                    for alarm in alarms:
                        try:
                            id_alarms = alarm.get('id', '')
                            cursor.execute(
                                "SELECT COUNT(*) FROM api.i_alarms WHERE idalarms = %s", (id_alarms,))
                            count = cursor.fetchone()[0]
                            if count == 0:
                                delay_time = int(
                                    float(alarm.get('delayTime', 0)))
                                document = alarm.get('document', '')
                                cleaned_document = clean_rut(
                                    document) if document else ''
                                speed = alarm.get('speed', 0) if alarm.get(
                                    'speed') is not None else 0
                                speedMax = alarm.get('speedMax', 0) if alarm.get(
                                    'speedMax') is not None else 0
                                speedMaxLimit = alarm.get('speedMaxLimit', 0) if alarm.get(
                                    'speedMaxLimit') is not None else 0
                                data = (
                                    alarm.get('holderDomain', ''),
                                    alarm.get('entryDate', ''),
                                    alarm.get('observation', ''),
                                    delay_time,
                                    speed,
                                    alarm.get('latitude', ''),
                                    alarm.get('longitude', ''),
                                    alarm.get('location', ''),
                                    cleaned_document,
                                    alarm.get('driverName', ''),
                                    alarm.get('fleets', [{}])[
                                        0].get('name', ''),
                                    alarm.get('comment', ''),
                                    alarm.get('duration', ''),
                                    speedMax,
                                    alarm.get('overspeedStartDate', ''),
                                    speedMaxLimit,
                                    alarm.get('zoneName', ''),
                                    id_alarms,
                                    alarm.get('positionDate', '')
                                )
                                cursor.execute("""INSERT INTO api.i_alarms (holder_domain, entry_date, observation, delay_time, 
                                        speed, latitude, longitude, location, document, driver_name, fleet_name, comment, duration, speedmax, overspeedstartdate, speedmaxlimit, zonename, idalarms, positiondate
                                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                                    """, data)
                                connection.commit()
                        except Exception as e:
                            logger.error(
                                f'Error en la inserción de datos: {e}')
                            logger.error(f'Datos con error: {data}')
                            connection.rollback()

                else:
                    print('API no mantiene datos que procesar')
        connection.close()
    elif response.getcode() == 401:
        unauthorized = json.loads(body)
        logger.error(unauthorized.get('message', ''))
except Exception as e:
    logger.error(f'Error de conexión a la API: {e}')
