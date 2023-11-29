import requests
import pandas as pd

base_url = "https://tsm.hivetire.app/"
token = "fcba4d869a72d68a19b01e1cfc3fcb3612f03793"
inspection_type = "VEHICLE-INSPECTIONS"

headers = {
    "Authorization": f"Token {token}"
}

ordered_data = []


url = f"{base_url}hiveSmanagement/API/INTEGRATIONS/{inspection_type}?page=1&limit=1000"
response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()
    data_list = data["data"]

    for entry in data_list:
        ordered_data.append({
            "terminal": entry["terminal"],
            "fleet": entry["fleet"],
            "license_plate": entry["license_plate"],
            "has_pressure_inspection": entry["has_pressure_inspection"],
            "has_tread_inspection": entry["has_tread_inspection"],
            "identification": entry["identification"],
            "inspection_date": entry["inspection_date"],
            "month": entry["month"],
            "year": entry["year"]
        })
    excel_path = f"VEHICLE.xlsx"

    df_vehicle = pd.DataFrame(ordered_data)
    df_vehicle.to_excel(excel_path)