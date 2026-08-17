import http.client
import time
import json
import hashlib
import logging
import ssl
from base64 import b64encode
import urllib3
import pandas as pd
from datetime import datetime, timedelta
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# Configuración del logging
logging.basicConfig(filename='connection_json.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)
   
# Credenciales de Usuario para la Sesion
def user_login():
    user = 'ws4057TSM'
    password_user = 'Zoda1310'
    return user, password_user

# Credenciales APIs
def call_apis(date):
    server = 'externalappgw.cl.sitrack.com'
    context_hours = f'/files/workday_{date}'
    return server, context_hours


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

def limpiar_fecha(fecha_str):
    return fecha_str.replace('-', '')


def main():
    created = (datetime.now() - timedelta(days=80)).strftime('%Y-%m-%d')
    date = limpiar_fecha(created)
    
    # Credenciales de usuario
    USER_NAME, PASSWORD = user_login()
    server, context_hours = call_apis(date)
    try:
        response = connect_to_api(USER_NAME, PASSWORD, server, context_hours)
        print('HTTP Code:', response.getcode())
        body = response.read().decode('utf-8')
        print("Éxito en la conexión a la API")
        if response.getcode() == 200:
            try:
                if body:
                    data_hours = json.loads(body)
                    # Guardar el JSON en un archivo
                    with open('data_hours.json', 'w', encoding='utf-8') as f:
                        json.dump(data_hours, f, ensure_ascii=False, indent=4)
                else:
                    data_hours = []
            except Exception as e:
                logger.exception(f'Error en la lectura de las respuestas: {e}')
                data_hours = []
    except Exception as e:
        logger.exception(f'Error de conexión a la API: {e}')


if __name__ == "__main__":
    main()