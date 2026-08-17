import logging
import json
import datetime
import pandas as pd

# Configuración del logging
logging.basicConfig(
    filename='data_asset_location_excel.log', 
    level=logging.DEBUG, 
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)
logger = logging.getLogger(__name__)

def process_data_to_excel(json_file_path, excel_file_path):
    created = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    data_for_excel = []

    try:
        with open(json_file_path, 'r', encoding='utf-8') as json_file:
            datos = json.load(json_file)  # Cargar datos JSON
            
            for dato in datos:
                tfu = dato.get('tfu', 0.0)
                odometer = dato.get('odometer', 0.0)
                drivintime = dato.get('drivingTime', 0.0)
                
                # Preparar datos para Excel
                data_for_excel.append({
                    'date': dato.get('date', ''),
                    'domain': dato.get('domain', ''),
                    'odometer': odometer,
                    'tfu': tfu,
                    'hourmeter': dato.get('hourmeter', 0.0),
                    'ralentiTime': dato.get('ralentiTime', 0.0),
                    'drivingTime': drivintime,
                    'created': created
                })
    except Exception as e:
        logger.exception(f'Error al procesar datos del archivo JSON: {e}')
        return

    # Generar el archivo Excel con los datos procesados
    try:
        generate_asset_excel(data_for_excel, excel_file_path)
    except Exception as e:
        logger.exception(f'Error al generar el archivo Excel: {e}')

def generate_asset_excel(data, file_path):
    try:
        df = pd.DataFrame(data)
        df.to_excel(file_path, index=False)
        logger.info(f"Archivo Excel generado correctamente: {file_path}")
    except Exception as e:
        logger.exception(f'Error al generar el archivo Excel: {e}')

def main():
    # Ruta completa para el archivo JSON de entrada
    json_file_path = 'C:/Users/lramirez/Github/Pytthon_Proyect/extracted_files/tsm-20240101.json'
    # Ruta completa para el archivo Excel de salida
    excel_file_path = 'C:/Users/lramirez/Github/Pytthon_Proyect/extracted_files/data_01.xlsx'
    
    # Procesar datos y generar Excel
    process_data_to_excel(json_file_path, excel_file_path)

if __name__ == "__main__":
    main()
