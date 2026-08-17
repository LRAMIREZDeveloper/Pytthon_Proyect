import requests
import pandas as pd
import time

base_url = "https://tsm.hivetire.app/"
token = "fcba4d869a72d68a19b01e1cfc3fcb3612f03793"
inspection_type = "tires"

headers = {
    "Authorization": f"Token {token}"
}

excel_path = "mounting.xlsx"
ordered_data = []

# Rango de fechas
fecha_inicio = "2026-03-01"
fecha_fin = "2026-04-30"

url = f"{base_url}api/public/{inspection_type}/mounting"

# Primera consulta
params = {
    "start_date": fecha_inicio,
    "end_date": fecha_fin,
    "page": 1
}

response = requests.get(url, headers=headers, params=params)

if response.status_code == 200:
    json_data = response.json()

    total = json_data.get("total", 0)
    last_page = json_data.get("last_page", 1)

    # Guardar data de la página 1
    ordered_data.extend(json_data.get("data", []))

    print(f"Total registros: {total}")
    print(f"Total páginas: {last_page}")
    print(f"Página 1 descargada. Registros: {len(json_data.get('data', []))}")

    # Consultar desde página 2 hasta la última
    for page in range(2, last_page + 1):
        print(f"Descargando página {page} de {last_page}...")

        params = {
            "start_date": fecha_inicio,
            "end_date": fecha_fin,
            "page": page
        }

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            json_data = response.json()
            data_page = json_data.get("data", [])
            ordered_data.extend(data_page)

            print(f"Página {page} descargada. Registros: {len(data_page)}")
        else:
            print(f"Error en página {page}, código {response.status_code}")
            print(response.text)

        time.sleep(1)

else:
    print(f"Error al consultar: {response.status_code}")
    print(response.text)

# Exportar a Excel
if ordered_data:
    df = pd.DataFrame(ordered_data)
    df.to_excel(excel_path, index=False)
    print(f"Archivo guardado en {excel_path}")
    print(f"Total registros exportados: {len(ordered_data)}")
else:
    print("No se obtuvieron datos")