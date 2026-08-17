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
        print("Conexión exitosa a la BDD")
        return conn
    except psycopg2.Error as e:
        print("Conexión fallida, error:", e)
        return None

def identify_file_type(binary_data):
    file_signatures = {
        b'\x25\x50\x44\x46': 'pdf',  # PDF
        b'\x50\x4B\x03\x04': 'zip',  # ZIP
        b'\xFF\xD8\xFF': 'jpg',      # JPEG
        b'\x89\x50\x4E\x47': 'png',  # PNG
        b'\x47\x49\x46\x38': 'gif',  # GIF
    }

    for signature, file_type in file_signatures.items():
        if binary_data.startswith(signature):
            return file_type
    return 'unknown'

def save_file(binary_data, filename):
    file_type = identify_file_type(binary_data)
    if file_type == 'unknown':
        print("Tipo de archivo desconocido")
        return None, None

    file_path = f'{filename}.{file_type}'
    with open(file_path, 'wb') as f:
        f.write(binary_data)

    return file_type, file_path

def consult_data_and_save(requisition_id):
    conn = connect_to_db()
    if conn is None:
        return

    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT record_id, binarydata, created 
            FROM adempiere.ad_attachment 
            WHERE record_id = %s 
        """, (requisition_id,))
        
        rows = cur.fetchall()

        if not rows:
            print(f"No se encontraron datos para record_id={requisition_id}")
            return

        for row in rows:
            requisition = row[0]
            binary_data = row[1]

            if binary_data:
                binary_data = bytes(binary_data)  # Asegura que sean bytes
                file_type, file_path = save_file(binary_data, f'output_{requisition}')
                
                if file_type == 'zip' and file_path:
                    with zipfile.ZipFile(file_path, 'r') as zip_ref:
                        extract_dir = f'extracted_files_{requisition}'
                        zip_ref.extractall(extract_dir)
                        extracted_files = zip_ref.namelist()
                    print(f"Archivos extraídos en '{extract_dir}': {extracted_files}")
                    print(f"Archivo ZIP de record_id={requisition} extraído en '{extract_dir}'")
                elif file_path:
                    print(f"Archivo de record_id={requisition} guardado como '{file_path}'")
            else:
                print(f"No se encontraron datos binarios para record_id={requisition}")

    except Exception as e:
        print(f"Error al procesar datos para record_id={requisition_id}: {e}")
    finally:
        cur.close()
        conn.close()

# Llamada a la función corregida
consult_data_and_save(1184794)
