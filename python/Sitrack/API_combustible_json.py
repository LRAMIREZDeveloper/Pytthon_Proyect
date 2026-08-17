import logging
import json
import datetime
import requests

# Configuración del logging
logging.basicConfig(
    filename='combustible.log',
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)

logger = logging.getLogger(__name__)

def API_connection_asset_fuel(date):
    try:
        apiKey = 'Apikey b61023c484994f2d9fa64d9cd5545af7'
        url = 'https://api.sitrack.io/event/flow/trigger?wait=true'

        data = {
            'processId': '9bfbcdf1-bf4b-4fe3-81a2-39bbc9223171',
            'date': date
        }

        response = requests.post(url, json=data, headers={'Authorization': apiKey})
        response.raise_for_status()

        return response.json()

    except requests.exceptions.HTTPError as error:
        logger.error(f"Connection failed for {date}: {error}")
        return None 


def consulta_from_api(date):
    response = API_connection_asset_fuel(date)

    if not response or 'result' not in response:
        logger.error(f"No data returned for {date}")
        return

    datos = response['result']

    # nombre del archivo
    nombre_archivo = f"datos_sitrack_{date}.json"

    # guardar JSON
    with open(nombre_archivo, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)

    logger.info(f"Datos guardados en {nombre_archivo}")


def main():
    date = '2026-03-19'
    consulta_from_api(date)


if __name__ == "__main__":
    main()