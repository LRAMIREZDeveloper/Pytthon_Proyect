import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import pandas as pd

# Desactivar advertencias de verificación de certificado SSL
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def api():
    # URL de la API que deseas consumir
    api_url = "https://192.168.70.2:8098/api/person/getPersonList"
    # Parámetros de la solicitud
    params = {
        "pageNo": 1,
        "pageSize": 1000,
        "access_token": "E4A5367EBB66E37B7204A675EF00DF7DC13253F26CE8999AE45DFCA615985836"
    }

    # Realizar la solicitud GET a la API sin verificar el certificado SSL
    response = requests.post(api_url, params=params, verify=False)
    return response


response = api()

# Verificar el código de estado de la respuesta
if response.status_code == 200:
    # La solicitud fue exitosa
    data = response.json()

    # Escribir datos en el DataFrame
    df = pd.DataFrame(data['data'])

    # Guardar el DataFrame en un archivo Excel
    df.to_excel("datos.xlsx", index=False)

    print("Datos guardados correctamente en datos.xlsx")
else:
    # La solicitud falló
    print("Error al consumir la API. Código de estado:", response.status_code)
    if response.status_code == 400:
        error_message = response.json().get("message")
        if error_message:
            print("Mensaje de error:", error_message)
        else:
            print("No se proporcionó un mensaje de error en la respuesta.")
    else:
        print("Error desconocido.")