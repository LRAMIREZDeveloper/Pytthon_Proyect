import psycopg2
import http.client
import time
import json
import hashlib
from base64 import b64encode

# Funcion para iniciar la sesión


def user_login():
    user = 'ws4057TSM'
    password_user = 'Zoda1310'
    return user, password_user

# Funciona para hacer llamado al servidor de la API


def call_api():
    server = 'externalappgw.cl.sitrack.com'
    context = '/files/alarms'

    return server, context

# Funcion para conectarse a la base de datos


def connect_to_db_tsm():
    try:
        connection = psycopg2.connect(
            host="192.168.1.29",
            database="tsm",
            user="api",
            password="Api2022"
        )
        print("Connected to the database")
        return connection
    except:
        print("Failed to connect to the database")
        return None

# Funcion para conectarse a la API


def connect_to_api(sessionId, secretKey, server, context):
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
# Funcion para solicitar una nueva sesión


def request_new_session(server, user_name, password):
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

# Funcion para trasformar los datos del RUT


def clean_rut(rut):
    rut = rut.replace('.', '').replace('-', '')
    rut = rut[:-1]
    return rut
