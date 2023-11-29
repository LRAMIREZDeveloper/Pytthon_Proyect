import psycopg2
import http.client
import time
import json
import hashlib
import logging
from base64 import b64encode

logging.basicConfig(level=logging.INFO)

# Funcion para iniciar la sesión
def user_login():
    user = 'ws4057TSM'
    password_user = 'Zoda1310'
    return user, password_user

# Funciona para hacer llamado al servidor de la API
def call_api():
    server = 'externalappgw.cl.sitrack.com'
    context = '/assetStatus'

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
        logging.info("Connected to the database")
        return connection
    except:
        logging.error("Failed to connect to the database")
        return None

# Funcion para conectarse a la API
def connect_to_api(sessionId, secretKey, server, context):
    # Verificar que ninguna de las variables es None
    if sessionId is None:
        logging.error('Error: sessionId es None')
    if secretKey is None:
         logging.error('Error: secretKey es None')

    # Se genera la firma digital para autenticar la sesión
    timestamp = str(int(time.time()))
    if timestamp is None:
        logging.error('Error: timestamp es None')

    # Continuar con el cálculo de sessionHash solo si todas las variables no son None
    if sessionId is not None and secretKey is not None and timestamp is not None:
        sessionHash = hashlib.md5(
            (sessionId + secretKey + timestamp).encode('utf-8')).digest()
        signature = b64encode(sessionHash).decode()
        headers = {
            'Authorization': 'StkAuth session="'+sessionId+'",signature="'+signature+'",timestamp="'+timestamp+'"'
        }

        # Se establece una conexión con el servidor para solicitar la firma
        conn = http.client.HTTPSConnection(server)
        conn.request('GET', context, None, headers)
        response = conn.getresponse()
        return response
    else:
        logging.error('Error: alguna variable es None')
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