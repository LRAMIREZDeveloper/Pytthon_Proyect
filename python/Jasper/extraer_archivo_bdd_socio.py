import psycopg2
import zipfile
 
 
def connect_to_db():
    try:
        conn = psycopg2.connect(
            host="adempiere.tsm.cl",
            database="tsm",
            user="pg_api",
            password="8YR53mDRavJlfd6d",
            port=5432,
        )
        print("Conexion exitosa a la BDD")
        return conn
    except psycopg2.Error as e:
        print("Conexion fallido, error: ", e)
        return None
 
def identify_file_type(binary_data):
    file_signatures = {
        b'\x25\x50\x44\x46': 'pdf',  # PDF
        b'\x50\x4B\x03\x04': 'zip',  # ZIP
        b'\xFF\xD8\xFF': 'jpg',      # JPEG
        b'\x89\x50\x4E\x47': 'png',  # PNG
        b'\x47\x49\x46\x38': 'gif',  # GIF
        # Añade más firmas según sea necesario
    }
 
    for signature, file_type in file_signatures.items():
        if binary_data.startswith(signature):
            return file_type
    return 'unknown'
 
# Función para guardar el archivo con la extensión correcta
def save_file(binary_data, filename):
    file_type = identify_file_type(binary_data)
    if file_type == 'unknown':
        print("Tipo de archivo desconocido")
        return file_type
 
    file_path = f'{filename}.{file_type}'
    with open(file_path, 'wb') as f:
        f.write(binary_data)
   
    return file_type, file_path
 
# Función modificada para obtener y guardar los datos binarios
def consult_data_and_save(ppu):
    # Conectar a la base de datos
    conn = connect_to_db()
    cur = conn.cursor()

    try:
        # Ejecutar la consulta
        cur.execute("""
            SELECT cb.value, cd.c_bpartner_id, at.binarydata
            FROM adempiere.C_CriticalDate cd
            JOIN adempiere.ad_attachment at ON at.record_id = cd.C_CriticalDate_id
            JOIN adempiere.c_bpartner cb ON cb.c_bpartner_id = cd.c_bpartner_id
            WHERE cd.c_bpartner_id = %s AND cd.status = 'AL'
            ORDER BY cd.created DESC
        """, (ppu,))
        
        # Obtener todas las filas devueltas
        rows = cur.fetchall()

        # Procesar cada fila individualmente
        for row in rows:
            value = row[0]
            a_asset_id = row[1]
            binary_data = row[2]

            if binary_data:
                binary_data = binary_data.tobytes()  # Convertir a bytes si es necesario
                file_type, file_path = save_file(binary_data, f'output_{a_asset_id}')
                
                if file_type == 'zip':
                    # Extraer el contenido del archivo ZIP
                    with zipfile.ZipFile(file_path, 'r') as zip_ref:
                        extract_dir = f'extracted_files_{value}'
                        zip_ref.extractall(extract_dir)
                    print(f"Archivo ZIP de a_asset_id={a_asset_id} extraído con éxito en '{extract_dir}'")
                else:
                    print(f"Archivo de a_asset_id={a_asset_id} guardado como '{file_path}'")
            else:
                print(f"No se encontraron datos binarios para a_asset_id={a_asset_id}")

    except Exception as e:
        print(f"Error al procesar datos para ppu={ppu}: {e}")
    finally:
        # Cerrar el cursor y la conexión
        cur.close()
        conn.close()

with connect_to_db() as conn:
    with conn.cursor() as cursor:
        # Ejecutar la consulta
        cursor.execute("SELECT c_bpartner_id FROM adempiere.c_bpartner WHERE ad_orgref_id = 1000067 AND isactive = 'Y'")
        
        # Obtener todos los resultados
        ppu_exists = cursor.fetchall()
        
        if ppu_exists:
            # Iterar sobre cada registro
            for ppu_data in ppu_exists:
                ppu = ppu_data[0]  # Extraer el valor de a_asset_id
                consult_data_and_save(ppu)  # Llamar a la función para cada a_asset_id
        else:
            print(f"No se encontraron a_asset_id asociados a la ad_org_id especificada.")
