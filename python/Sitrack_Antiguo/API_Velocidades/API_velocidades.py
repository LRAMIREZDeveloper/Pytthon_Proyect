import json
import datetime
import logging

from conexion import connect_to_api, user_login, connect_to_db_tsm, call_api, request_new_session, call_api_stopped, connect_to_api_stopped

logging.basicConfig(filename='error_driverscontrol.log', level=logging.ERROR, format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)


# Conexión a la base de datos PostgreSQL
try:
    # Intento de conexión a la base de datos
    connection = connect_to_db_tsm()
    cursor = connection.cursor()
    print("La conexión a la base de datos ha sido exitosa.")
except Exception as e:
    logger.error("Error al conectarse a la base de datos: ", e)

# Credenciales de usuario
USER_NAME, PASSWORD = user_login()


# Dirección de servidor y contexto de la API
server, context = call_api()
server, context2 = call_api_stopped()

# if sessionId is None:
sessionId, secretKey = request_new_session(server, USER_NAME, PASSWORD)

# Si la respuesta del servidor es exitosa, se procesan los datos y se agregan a la hoja de excel
try:
    # Intentar conectar a la API
    response = connect_to_api(sessionId, secretKey, server, context)
    print('HTTP Code:', response.getcode())
except Exception as e:
    logger.error(f'Error de conexión a la API: {e}')

try:
    response2 = connect_to_api_stopped(sessionId, secretKey, server, context2)
    print('HTTP Code:', response2.getcode())
except Exception as e:
    logger.error(f'Error de conexión a la API: {e}')

# Se lee el contenido de la respuesta
try:
    body = response.read().decode('utf-8')
except Exception as e:
    logger.error(f'Error de lectura de la respuesta: {e}')

try:
    body2 = response2.read().decode('utf-8')
except Exception as f:
    logger.error(f'Error de lectura de la respuesta 2: {f}')


# Se procesan los datos y se guardan los datos en la base de datos
if response.getcode() == 200:
    body = '[' + body + ']'
    speeds = json.loads(body)
    if speeds:
        for speed in speeds:
            try:
                # Obtener la fecha en formato 'dd-mm-yy'
                date = speed.get('date', '')
                time = speed.get('time', '')
                date_obj = datetime.datetime.strptime(date, '%d-%m-%y')
                time_obj = datetime.datetime.strptime(time, '%H:%M:%S')
                datetime_obj = datetime.datetime.combine(
                    date_obj.date(), time_obj.time())
                datetime_str = datetime_obj.strftime('%Y-%m-%d %H:%M:%S')
                ad_cliente = 1000000
                ad_org_id = 0
                created = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                createdby = 100
                updated = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                updatedby = 100
                isactive = 'Y'
                description = 'Integracion con Sitrack'
                processed = 'N'
                i_isimported = 'N'
                typematrix = 'VE'
                finaltime = None
                totaltime = None
                data_speed = (ad_cliente,
                              ad_org_id,
                              speed.get('location', ''),
                              speed.get('excessType', ''),
                              created,
                              createdby,
                              datetime_str,
                              description,
                              finaltime,
                              speed.get('driver', ''),
                              speed.get('fleet', ''),
                              speed.get('domain', ''),
                              isactive,
                              speed.get('latitude', ''),
                              speed.get('longitude', ''),
                              speed.get('speedMax', ''),
                              processed,
                              speed.get('speed', ''),
                              finaltime,
                              typematrix,
                              updated,
                              updatedby,
                              i_isimported,
                              totaltime,
                              speed.get('zoneName', ''),
                              )
                cursor.execute("""INSERT INTO api.i_driverscontrol (ad_client_id, ad_org_id, address1,categorytype,created, createdby, date1, description,endtime, i_bpartnername,i_flotaname, i_tractovalue, isactive,latitude, longitude, maxspeed, processed,speedcategory,starttime,typematrix,updated,updatedby, i_isimported,waittime, zonename) VALUES (%s, %s, %s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                        """, data_speed)
                connection.commit()
            except Exception as e:
                logger.error(f'Error en la inserción de datos: {e}')
                logger.error(f'Datos con error: {data_speed}')
                connection.rollback()
    else:
        print("Variable speeds vacia")


if response2.getcode() == 200:
    body2 = '[' + body2 + ']'
    stoppeds = json.loads(body2)
    if stoppeds:
        try:
            for stopped in stoppeds:
                # Obtener la fecha en formato 'dd-mm-yy'
                initialDate = stopped.get('initialDate')
                initialTime = stopped.get('initialTime')
                finalDate = stopped.get('finalDate')
                finalTime = stopped.get('finalTime')
                totaltime = stopped.get('totalTime')

                initialDate_obj = datetime.datetime.strptime(
                    initialDate, '%d-%m-%y')
                initialTime_obj = datetime.datetime.strptime(
                    initialTime, '%H:%M:%S')
                datetime_obj2 = datetime.datetime.combine(
                    initialDate_obj.date(), initialTime_obj.time())
                datetime_str_2 = datetime_obj2.strftime('%d-%m-%y %H:%M:%S')

                finalDate_obj = datetime.datetime.strptime(
                    finalDate, '%d-%m-%y')
                finalTime_obj = datetime.datetime.strptime(
                    finalTime, '%H:%M:%S')

                tiempo_detencion = datetime.datetime.combine(
                    finalDate_obj.date(), finalTime_obj.time())
                datetime_str_total = tiempo_detencion.strftime(
                    '%Y-%m-%d %H:%M:%S')

                try:
                    totaltime_obj2 = datetime.datetime.strptime(
                        totaltime, '%H:%M:%S')
                    tiempo_detencion_total = totaltime_obj2.strftime(
                        '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    tiempo_detencion_total = None

                ad_cliente = 1000000
                ad_org_id = 0
                created = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                createdby = 100
                updated = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                updatedby = 100
                isactive = 'Y'
                categoria = None
                description = 'Integracion con Sitrack'
                processed = 'N'
                i_isimported = 'N'
                typematrix_stopped = 'DE'
                maxspeed = None
                speedcategory = None
                data_stopped = (
                    ad_cliente,
                    ad_org_id,
                    stopped.get('location', ''),
                    categoria,
                    created if created else None,  # Verificar si created está vacío
                    createdby,
                    datetime_str_2,  # Verificar si datetime_str_2 está vacío
                    description,
                    datetime_str_total,
                    stopped.get('driver', ''),
                    stopped.get('fleet', ''),
                    stopped.get('domain', ''),
                    isactive,
                    stopped.get('latitude', ''),
                    stopped.get('longitude', ''),
                    maxspeed,
                    processed,
                    speedcategory,
                    datetime_str_2,  # Verificar si datetime_str_2 está vacío
                    typematrix_stopped,
                    updated,
                    updatedby,
                    i_isimported,
                    tiempo_detencion_total  # Verificar si datetime_str_total está vacío
                )
                cursor.execute("""INSERT INTO api.i_driverscontrol (ad_client_id, ad_org_id, address1,categorytype,created, createdby, date1, description,endtime, i_bpartnername,i_flotaname, i_tractovalue, isactive,latitude, longitude, maxspeed, processed,speedcategory,starttime,typematrix,updated,updatedby, i_isimported,waittime) VALUES (%s, %s, %s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                        """, data_stopped)
                connection.commit()
        except Exception as e:
            logger.error(f'Error en la inserción de datos: {e}')
            logger.error(f'Datos con error: {data_stopped}')
            connection.rollback()
    else:
        print("Variable stopped vacia")

connection.close()
