import logging
import json
import datetime
import requests
from connection import connect_to_db_tsm_nuevo

# Configuración del logging
logging.basicConfig(filename='data_asset_location.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)

def API_connection_telemetry(date):
    try:
        apiKey = 'Apikey b61023c484994f2d9fa64d9cd5545af7'
        url = 'https://api.sitrack.io/event/flow/trigger?wait=true'
        data = {
            'processId': '28548923-c2fd-4c74-ba87-10ffbf548326',
            'date': date
        }
        # Deshabilita la verificación del certificado SSL
        response = requests.post(url, json=data, headers={'Authorization': apiKey}, verify=False)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as error:
        logger.error(f"Connection failed for {date}: {error}")
        return None 

def insert_data_from_json(date):
    created = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    insert_data = []
    response = API_connection_telemetry(date)
    
    if not response or 'result' not in response:
        logger.error(f"No data returned for {date}")
        return

    datos = response['result']

    logger.info(f'Estos son los datos que envia el Sitrack para el ICAN.\n'
                f'{datos}')

    with connect_to_db_tsm_nuevo() as connection:
        with connection.cursor() as cursor:
            for dato in datos:
                tfu = dato.get('tfu', 0.0)
                odometer = dato.get('odometer', 0.0)
                drivintime = dato.get('drivingTime', 0.0)
                servicebreak = dato.get('serviceBrake', 0.0)
                motorbreak = dato.get('motorBrake', 0.0)
                
                try:
                    data = (
                        dato.get('date', ''),
                        dato.get('domain', ''),
                        odometer,
                        tfu,
                        dato.get('hourmeter', 0.0),
                        dato.get('ralentiTime', 0.0),
                        drivintime,
                        created,
                        servicebreak,
                        motorbreak        
                    )
                    insert_data.append(data)
                except Exception as e:
                    logger.exception(f'Error en la preparación de datos: {e}')
            
            # Ejecutar inserciones en la base de datos una vez, después del ciclo
            if insert_data:
                try:
                    query = """
                        INSERT INTO api.i_ican (datetrx, asset, odometer, tfu, hourmeter, ralentime, drivingtime, created, servicebreak, motorbreak)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.executemany(query, insert_data)
                    connection.commit()
                    logger.info(f"Datos insertados correctamente en la BD para la fecha {date}")
                except Exception as e:
                    logger.exception(f'Error en la inserción en la BD para la fecha {date}: {e}')
                    connection.rollback()

def main():
    date = '2025-08-31'
    insert_data_from_json(date)

if __name__ == "__main__":
    main()
