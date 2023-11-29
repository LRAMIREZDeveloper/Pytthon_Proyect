import psycopg2
import requests
import http.client
import time
import json
import hashlib
import datetime
import logging
from datetime import date, timedelta
from base64 import b64encode

logging.basicConfig(filename='error_detail_Sitrack.log', level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)

#-----------------------------------------------------------------------------
#CONEXION A API, FUNCIONES Y BDD.

# Funcion para dar formato al RUT
def clean_rut(rut):
    rut = rut.replace('.', '').replace('-', '')
    rut = rut[:-1]
    return rut

# Conexion a BDD
def connect_to_db_tsm_nuevo():
    try:
        conn = psycopg2.connect(
            host="tsm.prolinux.cl",
            database="adempiere",
            user="adempiere",
            password="quL2CDAY5kdh",
            port=5432
        )
        print("Connected to the database")
        return conn
    except psycopg2.Error as e:
        print("Failed to connect to the database", e)
        return None

# Credenciales de Usuario para la Sesion
def user_login():
    user = 'ws4057TSM'
    password_user = 'Zoda1310'
    return user, password_user

# Credenciales APIs
def call_apis():
    server = 'externalappgw.cl.sitrack.com'
    context_alarms = '/files/alarms'
    context_odometer = '/assetStatus'
    context_speed = '/files/speed'
    context_stopped = '/files/stopped'

    return server, context_speed, context_alarms, context_odometer, context_stopped

# Metodo de conexion a la APIs ( Alarmas y Odometro)
def connect_to_api(user_name, password, server, context):
    user_and_pass = (user_name + ':' + password).encode('ascii')
    encoded_user_and_pass = b64encode(user_and_pass).decode()
    headers = {'Authorization': 'Basic ' + encoded_user_and_pass}

    connection_user = http.client.HTTPSConnection(server)
    connection_user.request('GET', '/session', None, headers)
    response = connection_user.getresponse()
    body = response.read().decode('utf-8')

    if response.getcode() != 200:
        return None

    session = json.loads(body)
    sessionId = session['sessionId']
    secretKey = session['secretKey']
    connection_user.close()

    # Verificar que ninguna de las variables es None
    if sessionId is None:
        print('Error: sessionId es None')
    if secretKey is None:
        print('Error: secretKey es None')

    # Se genera la firma digital para autenticar la sesión
    timestamp = str(int(time.time()))
    if timestamp is None:
        print('Error: timestamp es None')

    # Continuar con el cálculo de sessionHash solo si todas las variables no son None
    if sessionId is not None and secretKey is not None and timestamp is not None:
        sessionHash = hashlib.md5(
            (sessionId + secretKey + timestamp).encode('utf-8')).digest()
        signature = b64encode(sessionHash).decode()
        headers = {
            'Authorization': 'StkAuth session="'+sessionId+'",signature="'+signature+'",timestamp="'+timestamp+'"'
        }
        try:
            # Se establece una conexión con el servidor para solicitar la firma
            conn = http.client.HTTPSConnection(server)
            conn.request('GET', context, None, headers)
            response = conn.getresponse()
            if response is not None:
                return response
            else:
                print("Error: La respuesta de la API es None")
                return None
        except Exception as e:
            print(f"Error al conectar con el servidor: {e}")
            return None
    else:
        print('Error: alguna variable es None')
        return None

# Credenciales API Checklist
def API_connection():
    try:
        apiKey = 'Apikey b61023c484994f2d9fa64d9cd5545af7'
        url = 'https://api.sitrack.io/event/flow/trigger?wait=true'
        data = {
            'processId': 'd8f9d79d-82c5-43b0-9342-832d9dfff9e9',
            'date': (date.today() - timedelta(days=1)).isoformat()
            # 'date': '2023-05-08'
        }
        response = requests.post(url, json=data, headers={
                                 'Authorization': apiKey})
        response.raise_for_status()
        data = json.loads(response.text)
        return data
    except requests.exceptions.HTTPError as error:
        print("Connection failed:", error)
        return None

#---------------------------------------------------------------------------
#DRIVERSCONTROL

# Credenciales de inicio de sesion para API de Driverscontrol
def request_session(server, user_name, password):
    user_and_pass = (user_name + ':' + password).encode('ascii')
    encoded_user_and_pass = b64encode(user_and_pass).decode()
    headers = {'Authorization': 'Basic ' + encoded_user_and_pass}

    conn = http.client.HTTPSConnection(server)
    conn.request('GET', '/session', None, headers)
    response = conn.getresponse()
    body = response.read().decode('utf-8')

    if response.getcode() != 200:
        return None, None

    session = json.loads(body)
    sessionId = session['sessionId']
    secretKey = session['secretKey']
    conn.close()
    return sessionId, secretKey

def connect_to_api_driverscontrol(sessionId, secretKey, server, context):
    # Verificar que ninguna de las variables es None
    if sessionId is None:
        print('Error: sessionId es None')
    if secretKey is None:
        print('Error: secretKey es None')

    # Se genera la firma digital para autenticar la sesión
    timestamp = str(int(time.time()))
    if timestamp is None:
        print('Error: timestamp es None')

    # Continuar con el cálculo de sessionHash solo si todas las variables no son None
    if sessionId is not None and secretKey is not None and timestamp is not None:
        sessionHash = hashlib.md5(
            (sessionId + secretKey + timestamp).encode('utf-8')).digest()
        signature = b64encode(sessionHash).decode()
        headers = {
            'Authorization': 'StkAuth session="'+sessionId+'",signature="'+signature+'",timestamp="'+timestamp+'"'
        }
        try:
            # Se establece una conexión con el servidor para solicitar la firma
            conn = http.client.HTTPSConnection(server)
            conn.request('GET', context, None, headers)
            response = conn.getresponse()
            if response is not None:
                return response
            else:
                print("Error: La respuesta de la API es None")
                return None
        except Exception as e:
            print(f"Error al conectar con el servidor: {e}")
            return None
    else:
        print('Error: alguna variable es None')
        return None


# Funcion para procesar los datos de las API asociadas al control de velocidades y detenciones
def process_insert_driverscontrol_data(response, typematrix):
    try:
        body = response.read().decode('utf-8')
        dataBody = '[' + body + ']'
    except Exception as e:
        logger.error(f'Error de lectura de la respuesta: {e}')
        return

    try:
        data = json.loads(dataBody)
        if not data:
            logger.error(f"Variable {typematrix} vacía")
            return

        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        records = []
        for item in data:
            initialDate = item.get('initialDate')
            initialTime = item.get('initialTime')
            finalDate = item.get('finalDate')
            finalTime = item.get('finalTime')
            totaltime = item.get('totalTime')
            date = item.get('date')
            time = item.get('time')
            zoneName = item.get('zoneName')
            speed = item.get('speed')
            excessType = item.get('excessType')
            speedMax = item.get('speedMax')

            # Verificar si las variables contienen datos válidos antes de convertirlas
            datetime_startime = None
            datetime_endtime = None
            datetime_total = None
            datetime_str = None

            if date and time:
                date_obj = datetime.datetime.strptime(date, '%d-%m-%y')
                time_obj = datetime.datetime.strptime(time, '%H:%M:%S')
                datetime_obj = datetime.datetime.combine(
                    date_obj.date(), time_obj.time())
                datetime_str = datetime_obj.strftime('%Y-%m-%d %H:%M:%S')

            if initialDate and initialTime:
                initialDate_obj = datetime.datetime.strptime(
                    initialDate, '%d-%m-%y')
                initialDate = initialDate_obj.strftime('%Y-%m-%d')
                initialTime_obj = datetime.datetime.strptime(
                    initialTime, '%H:%M:%S')
                datetime_obj2 = datetime.datetime.combine(
                    initialDate_obj.date(), initialTime_obj.time())
                datetime_startime = datetime_obj2.strftime('%Y-%m-%d %H:%M:%S')

            if finalDate and finalTime:
                finalDate_obj = datetime.datetime.strptime(
                    finalDate, '%d-%m-%y')
                finalTime_obj = datetime.datetime.strptime(
                    finalTime, '%H:%M:%S')
                tiempo_detencion = datetime.datetime.combine(
                    finalDate_obj.date(), finalTime_obj.time())
                datetime_endtime = tiempo_detencion.strftime(
                    '%Y-%m-%d %H:%M:%S')

            if totaltime:
                try:
                    totaltime_obj2 = datetime.datetime.strptime(
                        totaltime, '%H:%M:%S')
                    datetime_total = totaltime_obj2.strftime(
                        '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    datetime_total = None
            # Procesar los datos y guardarlos en una lista
            record = {
                'location': item.get('location', ''),
                'excesstype': excessType if typematrix == 'VE' else None,
                'controldate': datetime_str if typematrix == 'VE' else datetime_startime,
                'endtime': datetime_endtime if typematrix == 'DE' and datetime_endtime is not None else None,
                'driver': item.get('driver', ''),
                'fleet': item.get('fleet', ''),
                'domain': item.get('domain', ''),
                'latitude': item.get('latitude', ''),
                'longitude': item.get('longitude', ''),
                'speedmax': speedMax if typematrix == 'VE' else None,
                'speed': speed if typematrix == 'VE' else None,
                'starttime': datetime_startime if typematrix == 'DE' and datetime_startime is not None else None,
                'typematrix': typematrix,
                'waittime': datetime_total if typematrix == 'DE' and datetime_total is not None else None,
                'zonename': zoneName if typematrix == 'VE' else None,
                'created': current_time
            }
            records.append(record)

        # Insertar los datos en la base de datos
        with connect_to_db_tsm_nuevo() as connection:
            with connection.cursor() as cursor:
                insert_data_driverscontrol(
                    connection, cursor, records, typematrix)
    except Exception as e:
        logger.error(f'Error en la lectura de las respuestas: {e}')
        
def insert_data_driverscontrol(connection, cursor, data, typematrix):
    try:
        cursor.executemany("""
            INSERT INTO api.ti_driverscontrol (location, excesstype, controldate, endtime, driver_name, fleet_name, domain_name, latitude, longitude, speedmax, speed, starttime, typematrix, waittime, zonename, created)
            VALUES (%(location)s, %(excesstype)s, %(controldate)s, %(endtime)s, %(driver)s, %(fleet)s, %(domain)s, %(latitude)s, %(longitude)s, %(speedmax)s, %(speed)s, %(starttime)s, %(typematrix)s, %(waittime)s, %(zonename)s, %(created)s);
        """, data)
        connection.commit()
    except Exception as e:
        logger.error(f'Error en la inserción de datos: {e}')
        logger.error(f'Datos con error: {data}')
        connection.rollback()

#--------------------------------------------------------------------------
#INSERCION DE DATOS EN BDD.

# Funcion para la insercion de datos de Odometros
def insert_data_odometer(connection, cursor, data):
    try:
        odometros = json.loads(data)
    except Exception as e:
        logger.exception('Error en la lectura de la respuesta: {}'.format(e))
        return

    if not odometros:
        logger.warning('No se encontraron odómetros para insertar.')
        return

    query = "INSERT INTO api.ti_odometer(asset_ppu, odometer_amt, created) VALUES (%s, %s, %s);"
    created = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    for odometro in odometros:
        asset_id = odometro.get('assetId')
        odometer_amt = odometro.get('odometer')
        if asset_id and odometer_amt:
            datos = (asset_id, odometer_amt, created)
            try:
                cursor.execute(query, datos)
            except Exception as e:
                logger.exception(
                    'Error en la inserción de datos: {}'.format(e))
                connection.rollback()
        else:
            logger.warning(
                'Se omitió la inserción debido a datos faltantes o inválidos.')

# Funcion para la insercion de datos de alarmas
def insert_alarm_data(connection, cursor, alarms):
    if not alarms:
        logger.warning('No se encontraron alarmas para insertar.')
        return
    created = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    for alarm in alarms:
        try:
            id_alarms = alarm.get('id', '')
            cursor.execute(
                "SELECT COUNT(*) FROM api.ti_alarms WHERE idalarms = %s", (id_alarms,))
            count = cursor.fetchone()[0]
            if count == 0:
                delay_time = int(float(alarm.get('delayTime', 0)))
                document = alarm.get('document', '')
                cleaned_document = clean_rut(document) if document else ''
                speed = alarm.get('speed', 0) if alarm.get('speed') is not None else 0
                speedMax = alarm.get('speedMax', 0) if alarm.get('speedMax') is not None else 0
                speedMaxLimit = alarm.get('speedMaxLimit', 0) if alarm.get('speedMaxLimit') is not None else 0
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
                    alarm.get('fleets', [{}])[0].get('name', ''),
                    alarm.get('comment', ''),
                    alarm.get('duration', ''),
                    speedMax,
                    alarm.get('overspeedStartDate', ''),
                    speedMaxLimit,
                    alarm.get('zoneName', ''),
                    id_alarms,
                    alarm.get('positionDate', ''),
                    created
                )
                cursor.execute("""INSERT INTO api.ti_alarms (holder_domain, entry_date, observation, delay_time, 
                        speed, latitude, longitude, location, document, driver_name, fleet_name, comment, duration, speedmax, overspeedstartdate, speedmaxlimit, zonename, idalarms, positiondate, created
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                    """, data)
                connection.commit()
        except Exception as e:
            logger.exception('Error en la inserción de datos: {}'.format(e))
            logger.error(f'Datos con error: {data}')
            connection.rollback()

# Funcion para la insercion de datos de Checklist
def insert_checklist_data(cursor, data):
    created = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    result = data.get('result', {})
    checklist = result.get('checkList', [])
    for check in checklist:
        report_id = check.get('reportId', '')
        cursor.execute(
            "SELECT COUNT(*) FROM api.ti_checklist WHERE report_id = %s", (report_id,))
        count = cursor.fetchone()[0]
        if count == 0:
            fleet = check.get('fleet', '')
            report_id = check.get('reportId', '')
            report_date = check.get('reportDate', '')
            driver = check.get('driver', {})
            driver_rut = clean_rut(driver.get('document', ''))
            observation = check.get('observation', '')
            domain = check.get('domain', '')
            ramp = check.get('ramp', '')
            questions = check.get('question', [])
            for question in questions:
                question_response = question.get('response', '')
                question_id = question.get('id', '')
                try:
                    # Insertar los datos en la base de datos
                    cursor.execute(
                        "INSERT INTO api.ti_checklist (report_id, report_date, driver_value, observation, asset_value, m_checklist_question_id, project_name, response, ramp, created) VALUES (%s,%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                        (report_id, report_date, driver_rut, observation, domain, question_id, fleet, question_response, ramp, created))
                except psycopg2.Error as e:
                    logger.error(
                        "Error al insertar en la base de datos: {}".format(e))
                    raise e
                