import requests
import psycopg2
import pandas as pd
import time
from datetime import datetime, date

# ---------------- CONFIG API ----------------
base_url = "https://tsm.hivetire.app/"
token = "fcba4d869a72d68a19b01e1cfc3fcb3612f03793"
inspection_type = "inspections"

today = date.today()

if today.day == 1:
    if today.month == 1:
        month = 12
        year = today.year - 1
    else:
        month = today.month - 1
        year = today.year
else:
    month = today.month
    year = today.year

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

def convertir_fecha_excel(valor):
    if valor is None or valor == "":
        return None

    # Si ya es date
    if isinstance(valor, date):
        return valor

    if isinstance(valor, pd.Timestamp):
        return valor.date()

    # Si viene como string DD-MM-YYYY
    try:
        return datetime.strptime(str(valor), "%d-%m-%Y").date()
    except:
        pass

    # Si viene como número tipo 7012025
    try:
        num = int(valor)
        s = str(num)

        if len(s) == 7:  # DMMYYYY
            d = int(s[0])
            m = int(s[1:3])
            y = int(s[3:7])
            return date(y, m, d)

        if len(s) == 8:  # DDMMYYYY
            d = int(s[0:2])
            m = int(s[2:4])
            y = int(s[4:8])
            return date(y, m, d)
    except:
        pass

    # ISO 2025-12-04
    try:
        return datetime.fromisoformat(str(valor)).date()
    except:
        pass

    return None

def normalizar_tire_number(valor):
    if valor is None or valor == "":
        return None
    return str(valor)

# ---------------- CONEXIÓN DB ----------------
connection = connect_to_db_tsm()
cursor = connection.cursor()

# ---------------- INSERT ----------------
def insertar_inspection(datos):

    tire_number = normalizar_tire_number(datos.get('tire_number'))
    license_plate = limpiar_valor(datos.get('license_plate'))
    pressure_date = convertir_fecha_excel(datos.get('pressure_inspection_date'))

    cursor.execute("""
        INSERT INTO bi.inspections(
            terminal,
            fleet,
            tire_number,
            license_plate,
            position,
            pressure_psi,
            pressure_axle,
            pressure_condition,
            pressure_correction,
            pressure_inspection_date,
            pressure_inspection_month,
            pressure_inspection_year,
            is_flat,
            min_tread,
            min_tread_date,
            min_tread_month,
            min_tread_year,
            under_min_tread_limit,
            inspector,
            created
        ) VALUES (
            %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
            %s,%s,%s,%s,%s,%s,%s,%s,%s,%s
        );
    """, (
        limpiar_valor(datos.get('terminal')),
        limpiar_valor(datos.get('fleet')),
        tire_number,
        license_plate,
        limpiar_valor(datos.get('position')),
        limpiar_valor(datos.get('pressure_psi')),
        limpiar_valor(datos.get('pressure_axle')),
        limpiar_valor(datos.get('pressure_condition')),
        limpiar_valor(datos.get('pressure_correction')),
        pressure_date,
        limpiar_valor(datos.get('pressure_inspection_month')),
        limpiar_valor(datos.get('pressure_inspection_year')),
        limpiar_valor(datos.get('is_flat')),
        limpiar_valor(datos.get('min_tread')),
        convertir_fecha_excel(datos.get('min_tread_date')),
        limpiar_valor(datos.get('min_tread_month')),
        limpiar_valor(datos.get('min_tread_year')),
        limpiar_valor(datos.get('under_min_tread_limit')),
        limpiar_valor(datos.get('inspector')),
        date.today()
    ))

def borrar_mes_actual(cursor, month, year):
    cursor.execute("""
        DELETE FROM bi.inspections
        WHERE pressure_inspection_month = %s
          AND pressure_inspection_year = %s;
    """, (month, year))

# ---------------- PRIMERA PÁGINA ----------------

def main():

    print(f"Borrando datos del mes actual {month}, año {year} ...")
    borrar_mes_actual(cursor,month, year)
    

    url = f"{base_url}api/v1/tire/{inspection_type}?page=1&limit=1000&month={month}&year={year}"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print("Error consultando API")
        exit()

    json_data = response.json()
    total = json_data.get("total")
    last_page = json_data.get("last_page")

    print(f"Total registros: {total}")
    print(f"Total páginas: {last_page}")

    # Página 1
    for item in json_data.get("data", []):
        insertar_inspection(item)

    # ---------------- RESTO DE PÁGINAS ----------------
    for n in range(2, last_page + 1):
        print(f"Procesando página {n}/{last_page}")
        url = f"{base_url}api/v1/tire/{inspection_type}?page={n}&limit=1000&month={month}&year={year}"
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            for item in response.json().get("data", []):
                insertar_inspection(item)
        else:
            print(f"Error página {n}")

        time.sleep(1)

    # ---------------- COMMIT FINAL ----------------
    connection.commit()
    cursor.close()
    connection.close()

# ---------------- ENTRY POINT ----------------
if __name__ == "__main__":
    main()