import pandas as pd
import json
import psycopg2

def connect_to_db():
    try:
        conn = psycopg2.connect(
            host="adempiere.tsm.cl",
            database="tsm",
            user="pg_api",
            password="8YR53mDRavJlfd6d",
            port=5432
        )
        print("Conexion exitosa a la BDD")
        return conn
    except psycopg2.Error as e:
        print("Conexion fallido, error: ", e)
        return None

def read_excel_data(file_path):
    try:
        # Lee el archivo de Excel
        df = pd.read_excel(file_path)
        print("Datos de Excel cargados exitosamente")
        return df
    except Exception as e:
        print("Error al cargar datos desde el archivo de Excel:", e)
        return None

def excel_to_json(df):
    try:
        # Formatea las fechas a un formato legible
        df['datetrx'] = pd.to_datetime(df['datetrx'], unit='ms')
        
        # Convierte el DataFrame a JSON
        json_data = df.to_json(orient='records', date_format='iso')
        return json_data
    except Exception as e:
        print("Error al convertir DataFrame a JSON:", e)
        return None
    
    
    
# Llamada a la función para leer los datos del archivo Excel
file_path = "C:/Users/lramirez/Github/Pytthon_Proyect/extracted_files/data_asset_agosto.xlsx"
excel_data = read_excel_data(file_path)

if excel_data is not None:
    
    # Convierte los datos de Excel a JSON
    json_data = excel_to_json(excel_data)
    data = json.loads(json_data)
    print(data)
else:
    print("No se pudieron cargar los datos desde el archivo Excel.")
    
if data is not None:
    data_list = [] 
    for row in data:
        data_list.append(row)

if data_list is not None:
    try:
        with connect_to_db() as connection:
            with connection.cursor() as cursor:
                cursor.executemany("""INSERT INTO bi.quantity_utilization_asset (fleet, ppu, datetrx_hdr, quantity, datetrx)
                                   VALUES (%(fleet)s, %(PPU)s, %(datetrx_hdr)s, %(quantity)s, %(datetrx)s);""",data_list)
    except psycopg2.Error as e:
        print("Error al conectar con el servidor: ", e)
        connection.rollback()
        