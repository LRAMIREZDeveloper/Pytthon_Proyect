import json
from functions2 import connect_to_api, request_new_session, user_login, call_api

# Credenciales de usuario
USER_NAME, PASSWORD = user_login()

# Dirección de servidor y contexto de la API
server, context = call_api()

# Si no existe una sesión activa se solicita una nueva
sessionId, secretKey = request_new_session(server, USER_NAME, PASSWORD)

# Si la respuesta del servidor es exitosa, se procesan los datos y se agregan a la hoja de excel
try:
    # Intentar conectar a la API
    response = connect_to_api(sessionId, secretKey, server, context)
    print('HTTP Code:', response.getcode())
except Exception as e:
    print(f'Error de conexión a la API: {e}')
    exit()

# Se lee el contenido de la respuesta
try:
    body = response.read().decode('utf-8')
    print("Exito en la conexion a la API", body)
    try:
        alarms = json.loads(body)
        if alarms:
            print(alarms)
        else:
            print("La API ha devuelto una respuesta vacía")
    except json.JSONDecodeError as g:
        # Si la respuesta no es un JSON válido, imprimimos el contenido directamente
        print(f'Error en el formato JSON de la respuesta: {g}')
        print("Contenido de la respuesta:", body)
except Exception as f:
    print(f'Error de lectura de la respuestas: {f}')