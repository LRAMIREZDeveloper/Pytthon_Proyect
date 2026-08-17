import requests
import pandas as pd
import time

base_url = "https://tsm.hivetire.app/"
token = "fcba4d869a72d68a19b01e1cfc3fcb3612f03793"
inspection_type = "assigned-tires"

headers = {
    "Authorization": f"Token {token}"
}

excel_path = "assigned-tires.xlsx"
ordered_data = []

url = f"{base_url}api/v1/tire/{inspection_type}?page=1&limit=1000"
response = requests.get(url, headers=headers)

if response.status_code == 200:
    json_data = response.json()
    ordered_data.extend(response.json().get("data", []))

    # Datos de paginación
    total = json_data.get("total")
    last_page = json_data.get("last_page")

    print(f"Total registros: {total}")
    print(f"Total páginas: {last_page}")

    for n in range(2, last_page + 1):
        print(f"Descargando página {n} de {last_page}...")


        url = f"{base_url}api/v1/tire/{inspection_type}?page={n}&limit=100"
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            ordered_data.extend(response.json().get("data", []))
        else:
            print(f"Error en página {n}, código {response.status_code}")
        
        time.sleep(1)  # para evitar bloqueo del servidor

else:
    print(f"Error al consultar:  {response.status_code}")

if ordered_data:
    df = pd.DataFrame(ordered_data)
    df.to_excel(excel_path, index=False)
    print(f"Archivo guardado en {excel_path}")
else:
    print("No se obtuvieron datos")