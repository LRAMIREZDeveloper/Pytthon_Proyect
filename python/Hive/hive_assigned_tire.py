import requests
import psycopg2
import time
from datetime import date

# ---------------- CONFIG API ----------------
base_url = "https://tsm.hivetire.app/"
token = "fcba4d869a72d68a19b01e1cfc3fcb3612f03793"
inspection_type = "assigned-tires"

headers = {
    "Authorization": f"Token {token}"
}

# ---------------- DB ----------------
def connect_to_db_tsm():
    return psycopg2.connect(
        host="adempiere.tsm.cl",
        database="tsm",
        user="pg_api",
        password="8YR53mDRavJlfd6d",
        port=5432
    )

# ---------------- LIMPIEZA ----------------
def limpiar_valor(valor):
    if valor is None or valor == "":
        return None
    return valor

def convertir_min_tread(valor):
    if valor is None or valor == "":
        return None
    return float(str(valor).replace(",", "."))

def normalizar_tire_number(valor):
    if valor is None or valor == "":
        return None
    return str(valor)

# ---------------- CONEXIÓN DB ----------------
connection = connect_to_db_tsm()
cursor = connection.cursor()

# TRUNCATE antes de insertar
cursor.execute("TRUNCATE TABLE bi.assigned_tires;")
connection.commit()
print("Tabla bi.assigned_tires truncada")

# ---------------- PRIMERA LLAMADA ---------------- 
url = f"{base_url}api/v1/tire/{inspection_type}?page=1&limit=1000"
response = requests.get(url, headers=headers)

if response.status_code != 200:
    print("Error al consultar API")
    exit()

json_data = response.json()
total = json_data.get("total")
last_page = json_data.get("last_page")

print(f"Total registros: {total}")
print(f"Total páginas: {last_page}")

# ---------------- FUNCIÓN INSERT ----------------
def insertar_registro(datos):
    cursor.execute("""
        INSERT INTO bi.assigned_tires(
            vehicle_identification,
            tire_number,
            tire_stage,
            size,
            case_brand,
            case_model,
            level_brand,
            level_model,
            position,
            last_pressure_inspection,
            last_pressure_inspection_date,
            last_tread_inspection,
            last_tread_inspection_date,
            min_tread_inspection,
            created
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, %s);
    """, (
        limpiar_valor(datos.get('vehicle_identification')),
        normalizar_tire_number(datos.get('tire_number')),
        limpiar_valor(datos.get('tire_stage')),
        limpiar_valor(datos.get('size')),
        limpiar_valor(datos.get('case_brand')),
        limpiar_valor(datos.get('case_model')),
        limpiar_valor(datos.get('level_brand')),
        limpiar_valor(datos.get('level_model')),
        limpiar_valor(datos.get('position')),
        limpiar_valor(datos.get('last_pressure_inspection')),
        limpiar_valor(datos.get('last_pressure_inspection_date')),
        limpiar_valor(datos.get('last_tread_inspection')),
        limpiar_valor(datos.get('last_tread_inspection_date')),
        convertir_min_tread(datos.get('min_tread_inspection')),
        date.today()
    ))

# ---------------- PROCESAR PÁGINAS ----------------
def procesar_pagina(data):
    for item in data:
        insertar_registro(item)

# Página 1
procesar_pagina(json_data.get("data", []))

# Resto de páginas
for n in range(2, last_page + 1):
    print(f"Procesando página {n}/{last_page}")

    time.sleep(1)

    url = f"{base_url}api/v1/tire/{inspection_type}?page={n}&limit=100"
    
    try:
        response = requests.get(url, headers=headers, timeout=30)

        if response.status_code == 200:
            procesar_pagina(response.json().get("data", []))
        else:
            print(f"Error página {n} - Status: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Error en página {n}: {e}")

# ---------------- COMMIT FINAL ----------------
connection.commit()
cursor.close()
connection.close()

print("Carga finalizada correctamente")