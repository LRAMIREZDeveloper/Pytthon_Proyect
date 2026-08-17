import logging
import datetime
import requests
from connection import connect_to_db_tsm_nuevo

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


def insert_from_api(date):
    created = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    insert_data = []
    response = API_connection_asset_fuel(date)

    if not response or 'result' not in response:
        logger.error(f"No data returned for {date}")
        return

    datos = response['result']

    with connect_to_db_tsm_nuevo() as connection:
        with connection.cursor() as cursor:
            for dato in datos:
                fuelvolumen = dato.get('tank1FuelChargeVolume', 0.0)
                odometer = dato.get('odometer', 0.0)

                try:
                    data = (
                        dato.get('associatedEventDate', ''),
                        fuelvolumen,
                        odometer,
                        dato.get('reportDate', ''),
                        dato.get('latitude', None),
                        dato.get('longitude', None ),
                        dato.get('domain', ''),
                        dato.get('supplier', ''),
                        dato.get('driverDocumentNumber', ''),
                        dato.get('driverName', ''),
                        dato.get('location', 'Sin Locación'),
                        dato.get('holderId', ''),
                        created,
                        date
                    )
                    insert_data.append(data)
                except Exception as e:
                    logger.exception(f'Error en la preparación de datos: {e}')
            if insert_data:
                try:
                    query = """
                        INSERT INTO api.i_asset_fuel (eventdate, fuelvolumen, odometer,reportdate, latitude, longitude, domain, supplier, driverdocument, drivername, location, holderid, created, datetrx )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.executemany(query, insert_data)
                    connection.commit()
                    logger.info(f"Datos insertados correctamente en la BD para la fecha {date}")
                except Exception as e:
                    logger.exception(f'Error en la inserción en la BD para la fecha {date}: {e}')
                    connection.rollback()                

def main():
    date = '2026-04-22'
    insert_from_api(date)


if __name__ == "__main__":
    main()