import requests
import pandas as pd
from datetime import datetime


def get_inspection_data_main(type, month, year):
    base_url = "https://tsm.hivetire.app/"
    token = "fcba4d869a72d68a19b01e1cfc3fcb3612f03793"

    if type == "vehicle":
        endpoint = "VEHICLE-INSPECTIONS"
    elif type == "tire":
        endpoint = "TIRE-INSPECTIONS"
    else:
        raise ValueError("Invalid inspection type")
    
    if type == "vehicle":
        url = f"{base_url}hiveSmanagement/API/INTEGRATIONS/{endpoint}?page=1&limit=5000"
    else:
        url = f"{base_url}hiveSmanagement/API/INTEGRATIONS/{endpoint}?page=1&limit=250&month={month}&year={year}"

    headers = {
        "Authorization": f"Token {token}"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Request failed with status code: {response.status_code}")
        return None


def ordered_data_vehicule(data_list):
    ordered_data = []
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
    return ordered_data


def ordered_data_tire(data_list):
    ordered_data = []
    for entry in data_list:
        ordered_data.append({
            "terminal": entry["terminal"],
            "fleet": entry["fleet"],
            "tire_number": entry["tire_number"],
            "license_plate": entry["license_plate"],
            "vehicle_type": entry["vehicle_type"],
            "position": entry["position"],
            "pressure_psi": entry["pressure_psi"],
            "pressure_axle": entry["pressure_axle"],
            "pressure_condition": entry["pressure_condition"],
            "pressure_correction": entry["pressure_correction"],
            "pressure_inspection_date": entry["pressure_inspection_date"],
            "pressure_inspection_month": entry["pressure_inspection_month"],
            "pressure_inspection_year": entry["pressure_inspection_year"],
            "is_flat": entry["is_flat"],
            "min_tread": entry["min_tread"],
            "min_tread_date": entry["min_tread_date"],
            "min_tread_month": entry["min_tread_month"],
            "min_tread_year": entry["min_tread_year"],
            "under_min_tread_limit": entry["under_min_tread_limit"],
            "driven_delta": entry["driven_delta"],
            "over_delta_limit": entry["over_delta_limit"],
            "inspector": entry["inspector"]
        })
    return ordered_data


def save_to_excel(data, filename):
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False)
    print(f"Data saved to {filename}")


def get_inspection_data(inspection_type):
    base_url = "https://tsm.hivetire.app/"
    token = "fcba4d869a72d68a19b01e1cfc3fcb3612f03793"

    if inspection_type not in ["vehicle", "tire"]:
        raise ValueError("Invalid inspection type")

    current_date = datetime.now()
    current_month = current_date.month
    current_year = current_date.year

    headers = {"Authorization": f"Token {token}"}

    ordered_data = []

    for year in range(2023, current_year + 1):
        for month in range(1, 13):
            if year == current_year and month > current_month:
                break

            url = f"{base_url}hiveSmanagement/API/INTEGRATIONS/{inspection_type.upper()}-INSPECTIONS?page=1&limit=500&month={month}&year={year}"
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                data = response.json()
                data_list = data.get("data", [])

                for entry in data_list:
                    if inspection_type == "vehicle":
                        inspection_data = {
                            "terminal": entry["terminal"],
                            "fleet": entry["fleet"],
                            "license_plate": entry["license_plate"],
                            "has_pressure_inspection": entry["has_pressure_inspection"],
                            "has_tread_inspection": entry["has_tread_inspection"],
                            "identification": entry["identification"],
                            "inspection_date": entry["inspection_date"],
                            "month": entry["month"],
                            "year": entry["year"]
                        }
                    if inspection_type == "tire":
                        inspection_data = {
                            "terminal": entry["terminal"],
                            "fleet": entry["fleet"],
                            "tire_number": entry["tire_number"],
                            "license_plate": entry["license_plate"],
                            "vehicle_type": entry["vehicle_type"],
                            "position": entry["position"],
                            "pressure_psi": entry["pressure_psi"],
                            "pressure_axle": entry["pressure_axle"],
                            "pressure_condition": entry["pressure_condition"],
                            "pressure_correction": entry["pressure_correction"],
                            "pressure_inspection_date": entry["pressure_inspection_date"],
                            "pressure_inspection_month": entry["pressure_inspection_month"],
                            "pressure_inspection_year": entry["pressure_inspection_year"],
                            "is_flat": entry["is_flat"],
                            "min_tread": entry["min_tread"],
                            "min_tread_date": entry["min_tread_date"],
                            "min_tread_month": entry["min_tread_month"],
                            "min_tread_year": entry["min_tread_year"],
                            "under_min_tread_limit": entry["under_min_tread_limit"],
                            "driven_delta": entry["driven_delta"],
                            "over_delta_limit": entry["over_delta_limit"],
                            "inspector": entry["inspector"]
                        }
                    ordered_data.append(inspection_data)
    return ordered_data
