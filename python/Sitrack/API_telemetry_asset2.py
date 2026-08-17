import logging
import json
import datetime
from connection import connect_to_db_tsm_nuevo

# Configuración del logging
logging.basicConfig(filename='data_asset_location.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)

def insert_data_from_json(json_file_path):
    created = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    insert_data = []

    with open(json_file_path, 'r', encoding='utf-8') as json_file:
        datos = json.load(json_file)  # Cargar datos JSON

        with connect_to_db_tsm_nuevo() as connection:
            with connection.cursor() as cursor:
                for dato in datos:
                    tfu = dato.get('tfu', 0.0)
                    odometer = dato.get('odometer', 0.0)
                    drivintime = dato.get('drivingTime', 0.0)    
                    try:
                        data = (
                            dato.get('date', ''),
                            dato.get('domain', ''),
                            odometer,
                            tfu,
                            dato.get('hourmeter', 0.0),
                            dato.get('ralentiTime', 0.0),
                            drivintime,
                            created
                        )
                        insert_data.append(data)
                    except Exception as e:
                        logger.exception(f'Error en la preparación de datos: {e}')
                
                # Ejecutar inserciones en la base de datos
                if insert_data:
                    try:
                        query = """
                            INSERT INTO api.i_ican (datetrx, asset, odometer, tfu, hourmeter, ralentime, drivingtime, created)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """
                        cursor.executemany(query, insert_data)
                        connection.commit()
                        logger.info("Datos insertados correctamente en la BD")
                    except Exception as e:
                        logger.exception(f'Error en la inserción en la BD: {e}')
                        connection.rollback()
                        
def main():
    # Ruta completa para el archivo JSON de entrada
    json_file_path = 'C:/Users/lramirez/Github/Pytthon_Proyect/extracted_files/tsm-20241101.json'
    insert_data_from_json(json_file_path)

if __name__ == "__main__":
    main()
