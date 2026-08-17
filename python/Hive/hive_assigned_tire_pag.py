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

# ---------------- CONFIG PÁGINA ----------------
page = 99
limit = 1000

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
    return valor if valor not in (None, "") else None

def convertir_min_tread(valor):
    if valor in (None, ""):
        return None
    return float(str(valor).replace(",", "."))

def normalizar_tire_number(valor):
    return str(valor) if valor not in (None, "") else None

# ---------------- CONEXIÓN DB ----------------
connection = connect_to_db_tsm()
cursor = connection.cursor()

print(f"Procesando SOLO la página {page}")

# ---------------- CONSULTA API ----------------
url = f"{base_url}api/v1/tire/{inspection_type}?page={page}&limit={limit}"

try:
    time.sleep(1)  # 👈 pausa antes de llamar
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()


    data = response.json().get("data", [])

    if not data:
        print("La página no tiene datos")
    else:
        print(f"Registros obtenidos: {len(data)}")

        for item in data:
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
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);
            """, (
                limpiar_valor(item.get('vehicle_identification')),
                normalizar_tire_number(item.get('tire_number')),
                limpiar_valor(item.get('tire_stage')),
                limpiar_valor(item.get('size')),
                limpiar_valor(item.get('case_brand')),
                limpiar_valor(item.get('case_model')),
                limpiar_valor(item.get('level_brand')),
                limpiar_valor(item.get('level_model')),
                limpiar_valor(item.get('position')),
                limpiar_valor(item.get('last_pressure_inspection')),
                limpiar_valor(item.get('last_pressure_inspection_date')),
                limpiar_valor(item.get('last_tread_inspection')),
                limpiar_valor(item.get('last_tread_inspection_date')),
                convertir_min_tread(item.get('min_tread_inspection')),
                date.today()
            ))

        connection.commit()
        print("Página insertada correctamente")

except requests.exceptions.RequestException as e:
    connection.rollback()
    print(f"Error en la API: {e}")

except Exception as e:
    connection.rollback()
    print(f"Error en BD: {e}")

# ---------------- CIERRE ----------------
cursor.close()
connection.close()