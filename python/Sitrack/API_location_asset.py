import logging
from connection import connect_to_db_tsm_nuevo, API_connection_asset,insert_asset_data,update_data_asset,generate_asset_excel

# Configuración del logging
logging.basicConfig(filename='data_asset_location.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)


def main():
    # Validar la conexión a la API
    data = API_connection_asset()
    if data is not None:
        logger.info("Conexión a la API exitosa.")
        logger.info(data)
    else:
        logger.error("No se pudo conectar a la API.")
        exit(1)

    # Generar el archivo Excel
    try:
        # Ruta completa para el archivo Excel (incluyendo nombre y extensión)
        file_path = 'C:/Users/lramirez/Github/Pytthon_Proyect/extracted_files/assets_data.xlsx'
        generate_asset_excel(data, file_path)
        #logger.info(f"Archivo Excel generado en: {file_path}")
        
        # Si necesitaras conectar a la base de datos en el futuro
        #with connect_to_db_tsm_nuevo() as conn:
        #    with conn.cursor() as cur:
        #        insert_asset_data(conn, cur, data)
        #        update_data_asset(conn, cur, data)  
        #        conn.commit()
     
    except ConnectionError as e:
        logger.error("No se pudo conectar a la base de datos: {}".format(e))
        exit(1)

if __name__ == "__main__":
    main()