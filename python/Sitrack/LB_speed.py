import http.client
import time
import json
import hashlib
import os
import ssl
from base64 import b64encode
import psycopg2
from datetime import datetime

# Desactivar warnings de SSL
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Conexión a BDD
def connect_to_db_tsm_nuevo(BD_HOST, BD_DATABASE, BD_USER, BD_PASSWORD):
    try:
        conn = psycopg2.connect(
            host=BD_HOST,
            database=BD_DATABASE,
            user=BD_USER,
            password=BD_PASSWORD,
            port=5432
        )
        return conn
    except psycopg2.Error as e:
        print(f"ERROR: Error al conectar a la base de datos: {e}")
        return None

def clean_rut(rut):
    rut = rut.replace('.', '').replace('-', '')
    rut = rut[:-1]
    return rut

def request_session(server, user_name, password):
    user_and_pass = f'{user_name}:{password}'.encode('ascii')
    encoded_user_and_pass = b64encode(user_and_pass).decode()
    headers = {'Authorization': f'Basic {encoded_user_and_pass}'}

    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    try:
        conn = http.client.HTTPSConnection(server, context=ssl_context)
        conn.request('GET', '/session', None, headers)
        response = conn.getresponse()
        body = response.read().decode('utf-8')
        conn.close()
    except Exception as e:
        print(f"ERROR: Error durante la solicitud de sesión: {e}")
        return None, None

    if response.status != 200:
        print(f"ERROR: Error al autenticar sesión. Código HTTP: {response.status}")
        return None, None

    try:
        session = json.loads(body)
        sessionId = session.get('sessionId')
        secretKey = session.get('secretKey')
    except Exception as e:
        print(f"ERROR: Error al interpretar JSON de sesión: {e}")
        return None, None

    if not sessionId or not secretKey:
        print("ERROR: Sesión inválida: falta sessionId o secretKey")
        return None, None

    return sessionId, secretKey

def connect_to_api_driverscontrol(sessionId, secretKey, server, context):
    if not sessionId:
        print("ERROR: sessionId es None")
        return None
    if not secretKey:
        print("ERROR: secretKey es None")
        return None

    timestamp = str(int(time.time()))
    if not timestamp:
        print("ERROR: timestamp es None")
        return None

    try:
        sessionHash = hashlib.md5((sessionId + secretKey + timestamp).encode('utf-8')).digest()
        signature = b64encode(sessionHash).decode()
        headers = {
            'Authorization': f'StkAuth session="{sessionId}",signature="{signature}",timestamp="{timestamp}"'
        }

        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        conn = http.client.HTTPSConnection(server, context=ssl_context)
        conn.request('GET', context, None, headers)
        response = conn.getresponse()
        if response:
            return response
        else:
            print("ERROR: Response es None")
            return None

    except Exception as e:
        print(f"ERROR: Error al conectar con la API: {e}")
        return None

def process_insert_driverscontrol_data(response, typematrix, BD_HOST, BD_DATABASE, BD_USER, BD_PASSWORD):
    try:
        body = response.read().decode('utf-8').strip()
        print("RAW API BODY:")
        print(body)
        
        if not body:
            print("ERROR: El cuerpo de la respuesta está vacío.")
            return None

        # Si empieza con { pero no está envuelto en []
        if body.startswith('{') and not body.startswith('['):
            print("WARNING: Formateando múltiples objetos JSON sin corchetes...")

            # Eliminar comas al final de líneas (entre objetos), para evitar 'Extra data'
            lines = [line.strip().rstrip(',') for line in body.splitlines() if line.strip()]
            # Volver a unir y envolver con []
            body = "[" + ",".join(lines) + "]"

        data = json.loads(body)

        # Encapsular en lista si viene como objeto único
        if not isinstance(data, list):
            data = [data]

        

    except json.JSONDecodeError as e:
        print(f"ERROR: Drivercontrol: Error de lectura de la respuesta body (JSON malformado): {e}")
        print(f"ERROR: Contenido recibido (raw): {body}")
        return None
    except Exception as e:
        print(f"ERROR: Drivercontrol: Error inesperado al procesar la respuesta: {e}")
        return None


    try:
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        description = 'Integracion con Sitrack por AWS'
        records = []

        for item in data:
            initialDate = item.get('initialDate')
            initialTime = item.get('initialTime')
            finalDate = item.get('finalDate')
            finalTime = item.get('finalTime')
            totaltime = item.get('totalTime')
            date = item.get('date')
            time_ = item.get('time')
            zoneName = item.get('zoneName')
            speed = item.get('speed')
            excessType = item.get('excessType')
            speedMax = item.get('speedMax')
            document = item.get('driverDocument')
            rut = clean_rut(document) if document else ''

            datetime_startime = None
            datetime_endtime = None
            datetime_total = None
            datetime_str = None

            if date and time_:
                try:
                    date_obj = datetime.strptime(date, '%d-%m-%y')
                    time_obj = datetime.strptime(time_, '%H:%M:%S')
                    datetime_obj = datetime.combine(date_obj.date(), time_obj.time())
                    datetime_str = datetime_obj.strftime('%Y-%m-%d %H:%M:%S')
                except Exception as e:
                    print(f"WARNING: Fecha u hora inválida en campo 'date/time': {e}")

            if initialDate and initialTime:
                try:
                    initialDate_obj = datetime.strptime(initialDate, '%d-%m-%y')
                    initialTime_obj = datetime.strptime(initialTime, '%H:%M:%S')
                    datetime_obj2 = datetime.combine(initialDate_obj.date(), initialTime_obj.time())
                    datetime_startime = datetime_obj2.strftime('%Y-%m-%d %H:%M:%S')
                except Exception as e:
                    print(f"WARNING: Fecha/hora inválida en initialDate/initialTime: {e}")

            if finalDate and finalTime:
                try:
                    finalDate_obj = datetime.strptime(finalDate, '%d-%m-%y')
                    finalTime_obj = datetime.strptime(finalTime, '%H:%M:%S')
                    tiempo_detencion = datetime.combine(finalDate_obj.date(), finalTime_obj.time())
                    datetime_endtime = tiempo_detencion.strftime('%Y-%m-%d %H:%M:%S')
                except Exception as e:
                    print(f"WARNING: Fecha/hora inválida en finalDate/finalTime: {e}")

            if totaltime:
                try:
                    totaltime_obj2 = datetime.strptime(totaltime, '%H:%M:%S')
                    datetime_total = totaltime_obj2.strftime('%Y-%m-%d %H:%M:%S')
                except ValueError:
                    datetime_total = None

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
                'document': rut
            }
            records.append(record)

        with connect_to_db_tsm_nuevo(BD_HOST, BD_DATABASE, BD_USER, BD_PASSWORD) as connection:
            with connection.cursor() as cursor:
                insert_data_driverscontrol(connection, cursor, records, typematrix)

    except Exception as e:
        print(f"ERROR: Drivercontrol: Error en la lectura de las respuestas e inserción de datos: {e}")

def insert_data_driverscontrol(connection, cursor, data, typematrix):
    try:
        for record in data:
            cursor.execute("""
                INSERT INTO api.i_driverscontrol (
                    address1, zonename, categorytype, created, date1, description,
                    endtime, i_bpartnername, i_flotaname, i_tractovalue,
                    latitude, longitude, maxspeed, speedcategory, starttime,
                    typematrix, waittime, i_document
                )
                VALUES (
                    %(location)s, %(zonename)s, %(excesstype)s, %(created)s, %(controldate)s,
                    %(description)s, %(endtime)s, %(driver)s, %(fleet)s, %(domain)s,
                    %(latitude)s, %(longitude)s, %(speedmax)s, %(speed)s, %(starttime)s,
                    %(typematrix)s, %(waittime)s, %(document)s
                );
            """, record)
            print("INSERT OK:", record)
        connection.commit()
    except Exception as e:
        print(f"ERROR: Error en la inserción de datos: {e}")
        print(f"DEBUG: Datos con error: {data}")
        connection.rollback()

def action():
    api_user = os.environ.get('API_USER')
    api_password = os.environ.get('API_PASSWORD')
    api_server = os.environ.get('API_SERVER')
    PATH_SPEED = os.environ.get('PATH_SPEED')
    PATH_STOPPED = os.environ.get('PATH_STOPPED')

    host = os.environ.get('DB_HOST')
    database = os.environ.get('DATABASE')
    db_user = os.environ.get('DB_USER')
    db_password = os.environ.get('DB_PASSWORD')

    sessionId, secretKey = request_session(api_server, api_user, api_password)
    if not sessionId or not secretKey:
        print("ERROR: No se pudo obtener sesión. Abortando ejecución.")
        return

    for context in [PATH_STOPPED, PATH_SPEED]:
        try:
            response = connect_to_api_driverscontrol(sessionId, secretKey, api_server, context)
            if response is None:
                print(f"ERROR: No se obtuvo respuesta para {context}")
                continue

            tipo = 'VE' if context == PATH_SPEED else 'DE'

            process_insert_driverscontrol_data(response, tipo, host, database, db_user, db_password)
            

        except Exception as e:
            print(f"ERROR: Error de conexión a la API Driverscontrol, tipo: {context} Error: {e}")

def lambda_handler(event, context):
    try:
        action()
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Ejecución completada"})
        }
    except Exception as e:
        print(f"ERROR: Error en lambda_handler: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

if __name__ == "__main__":
    action()
