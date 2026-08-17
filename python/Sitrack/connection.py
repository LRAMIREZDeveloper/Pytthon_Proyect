import psycopg2
import requests
import http.client
import time
import json
import hashlib
import datetime
import logging
import ssl
from datetime import date, timedelta
from base64 import b64encode
import urllib3
import pandas as pd
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuración del logging
logging.basicConfig(filename='connection.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s %(message)s')
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
            host="adempiere.tsm.cl",
            database="tsm",
            user="pg_api",
            password="8YR53mDRavJlfd6d",
            port=5432
        )
        logger.info("Conexion exitosa a la BDD")
        return conn
    except psycopg2.Error as e:
        logger.error("Conexion fallido, error: ", e)
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
    context_locations = '/v2/report'
    context_assetlocation = '/files/maintenanceReports'

    return server, context_speed, context_alarms, context_odometer, context_stopped,context_locations,context_assetlocation

# Metodo de conexion a la APIs ( Alarmas y Odometro)
def connect_to_api(user_name, password, server, context):
    user_and_pass = (user_name + ':' + password).encode('ascii')
    encoded_user_and_pass = b64encode(user_and_pass).decode()
    headers = {'Authorization': 'Basic ' + encoded_user_and_pass}
    
    # Configuración del contexto SSL
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    connection_user = http.client.HTTPSConnection(server, context=ssl_context)
    connection_user.request('GET', '/session', None, headers)
    response = connection_user.getresponse()
    body = response.read().decode('utf-8')

    if response.getcode() != 200:
        return None

    session = json.loads(body)
    sessionId = session['sessionId']
    secretKey = session['secretKey']
    timestamp = str(int(time.time()))
    connection_user.close()

    # Verificar que ninguna de las variables es None
    if sessionId is None or secretKey is None or timestamp is None:
        print('Error: Variable sin datos')

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
            conn = http.client.HTTPSConnection(server, context=ssl_context)
            conn.request('GET', context, None, headers)
            response = conn.getresponse()
            if response is not None:
                return response
            else:
                print("Error: Response es None")
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

        # Deshabilita la verificación del certificado SSL
        response = requests.post(url, json=data, headers={'Authorization': apiKey}, verify=False)
        
        response.raise_for_status()
        data = json.loads(response.text)
        return data
    except requests.exceptions.HTTPError as error:
        print("Connection failed:", error)
        return None 
    
def API_connection_telemetry():
    try:
        apiKey = 'Apikey b61023c484994f2d9fa64d9cd5545af7'
        url = 'https://api.sitrack.io/event/flow/trigger?wait=true'
        data = {
            'processId': '28548923-c2fd-4c74-ba87-10ffbf548326',
            #'date': (date.today() - timedelta(days=1)).isoformat()
            'date': '2024-11-01'
        }
        # Deshabilita la verificación del certificado SSL
        response = requests.post(url, json=data, headers={'Authorization': apiKey}, verify=False)
        
        response.raise_for_status()
        data = json.loads(response.text)
        return data
    except requests.exceptions.HTTPError as error:
        print("Connection failed:", error)
        return None 

# Credenciales API asset_location
def API_connection_asset():
    try:
        apiKey = 'Apikey b61023c484994f2d9fa64d9cd5545af7'
        url = 'https://api.sitrack.io/event/flow/trigger?wait=true'
        data = {
            'processId': '2aaff15f-26f4-4b5e-853e-17fe912117a7'
        }
        response = requests.post(url, json=data, headers={'Authorization': apiKey}, verify=False)
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

    # Configuración del contexto SSL
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    conn = http.client.HTTPSConnection(server, context=ssl_context)
    conn.request('GET', '/session', None, headers)
    response = conn.getresponse()
    body = response.read().decode('utf-8')

    if response.getcode() != 200:
        conn.close()
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

        # Configuración del contexto SSL
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        try:
            # Se establece una conexión con el servidor para solicitar la firma
            conn = http.client.HTTPSConnection(server, context=ssl_context)
            conn.request('GET', context, None, headers)
            response = conn.getresponse()
            if response is not None:
                return response
            else:
                print("Error: Response es None")
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
        logger.error(f'Drivercontrol: Error de lectura de la respuesta body: {e}')
        return

    try:
        data = json.loads(dataBody)
        if not data:
            logger.warning(f"Variable {typematrix} vacía")
            return

        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        description = 'Integracion con Sitrack'
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
            document = item.get('driverDocument')
            rut = clean_rut(document) if document else ''

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
                'description': description,
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
                'created': current_time,
                'document' : rut
            }
            records.append(record)

        # Insertar los datos en la base de datos
        with connect_to_db_tsm_nuevo() as connection:
            with connection.cursor() as cursor:
                insert_data_driverscontrol(
                    connection, cursor, records, typematrix)
    except Exception as e:
        logger.error(f'Drivercontrol: Error en la lectura de las respuestas e insercion de datos: {e}')
        
def insert_data_driverscontrol(connection, cursor, data, typematrix):
    try:
        cursor.executemany("""
            INSERT INTO api.i_driverscontrol (address1,zonename,categorytype,created, date1, description, endtime, i_bpartnername, i_flotaname, i_tractovalue, latitude, longitude, maxspeed, speedcategory, starttime, typematrix, waittime, i_document)
            VALUES (%(location)s, %(zonename)s, %(excesstype)s, %(created)s, %(controldate)s, %(description)s, %(endtime)s, %(driver)s, %(fleet)s, %(domain)s, %(latitude)s, %(longitude)s, %(speedmax)s, %(speed)s, %(starttime)s, %(typematrix)s, %(waittime)s, %(document)s);
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
        logger.exception(' ODOMETROS: Error en la lectura de la respuesta: {}'.format(e))
        return

    if not odometros:
        logger.warning('No se encontraron odómetros para insertar.')
        return

    query = "INSERT INTO api.i_odometer(asset_ppu, odometer_amt, created) VALUES (%s, %s, %s);"
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
    
    query = """
        INSERT INTO api.i_alarms (
            holder_domain, entry_date, observation, delay_time, speed, latitude, longitude, location, document, driver_name, fleet_name, 
            comment, duration, speedmax, overspeedstartdate, speedmaxlimit, zonename, idalarms, positiondate, created
        ) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (idalarms) DO NOTHING;
    """
    
    created = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    insert_data = []

    for alarm in alarms:
        try:
            
            if alarm.get('comment', '').strip().lower() == 'minutos de sobrevelocidad':
                continue   

            # Obtener el valor de idalarms
            id_alarms = alarm.get('id', '')
            
            # Preparar los datos para la inserción
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
            # Agregar los datos a la lista
            insert_data.append(data)

        except Exception as e:
            logger.exception('Error en la preparación de datos: {}'.format(e))
            logger.error(f'Datos con error: {alarm}')
    
    try:
        if insert_data:
            cursor.executemany(query, insert_data)
            connection.commit()
            logger.info("Datos insertados correctamente en la BD")
    except Exception as e:
        logger.exception(f'Error en la inserción de datos: {e}')
        connection.rollback()


# Funcion para la insercion de datos de Checklist
def insert_checklist_data(cursor, data):
    query = """INSERT INTO api.i_checklist (report_id, report_date, driver_value, observation, asset_value, m_checklist_question_id, project_name, response, ramp, created)
                VALUES (%s,%s, %s, %s, %s, %s, %s, %s, %s, %s);"""
    created = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    result = data.get('result', {})
    checklist = result.get('checkList', [])
    print(result)
    print(checklist)
    for check in checklist:
        report_id = check.get('reportId', '')
        cursor.execute(
            "SELECT COUNT(*) FROM api.i_checklist WHERE report_id = %s", (report_id,))
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
                    data = (
                        report_id,
                        report_date,
                        driver_rut,
                        observation,
                        domain,
                        question_id,
                        fleet,
                        question_response,
                        ramp,
                        created,
                    )
                    # Insertar los datos en la base de datos
                    cursor.execute(query, data)
                except psycopg2.Error as e:
                    logger.error(
                        "Error al insertar en la base de datos: {}".format(e))
                    raise e
       
# Funcion para la insercion de datos de Checklist
def insert_asset_data(connection, cursor, data):
    query = """
        INSERT INTO api.i_assetlocation (assetid, reportdate, zonename,created, isactive) 
        SELECT %s, %s, %s, %s, %s
        WHERE NOT EXISTS (
            SELECT 1 FROM api.i_assetlocation 
            WHERE assetid = %s AND isactive = 'Y'
        );
    """
    created = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    insert_data = []
    data_assets = data.get('result', {})
    for data_asset in data_assets:
        asset_id = data_asset.get('domain', '')
        insert_data.append((
            asset_id,
            data_asset.get('reportDate', ''),
            data_asset.get('zoneName', ''),
            created,
            'Y',
            asset_id
        ))
    try:
        if insert_data:
            cursor.executemany(query, insert_data)
            connection.commit()
            logger.info("Datos insertados correctamente en la BD")
    except Exception as e:
        logger.exception(f'Error en la inserción de datos: {e}')
        connection.rollback()

                
# Funcion para actualizar los datos de los equipos en mantencion      
def update_data_asset(connection, cursor, data_assets):
    created = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("SELECT assetid FROM api.i_assetlocation WHERE isactive = 'Y'")
    data = cursor.fetchall()
    if data:
        asset_data = data_assets.get('result', {})
        api_asset_ids = [asset['domain'] for asset in asset_data]
        for datos in data:
            assetid = datos[0]
            if assetid not in api_asset_ids:
                cursor.execute(""" UPDATE api.i_assetlocation SET isactive = 'N', date_old = %s WHERE assetid = %s
                """, (created, assetid,)
                )
                print(f"Updated assetid {assetid} to isactive = 'N'")
            else:
                print("Sin detalle para modificar")
                connection.commit()


def generate_asset_excel(data, file_path):
    created = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    data_list = []
    data_assets = data.get('result', {})
    
    for data_asset in data_assets:
        # Incluir todas las variables dinámicamente
        asset_info = {key: data_asset.get(key, '') for key in data_asset.keys()}
        asset_info['created'] = created
        data_list.append(asset_info)
    
    df = pd.DataFrame(data_list)
    try:
        df.to_excel(file_path, index=False)
        print(f"Archivo Excel generado correctamente: {file_path}")
    except Exception as e:
        print(f'Error al generar el archivo Excel: {e}')