from datetime import datetime
import pandas as pd
import requests

def get_inspection_data(inspection_type):
    BASE_URL = "https://tsm.hivetire.app/"
    TOKEN = "fcba4d869a72d68a19b01e1cfc3fcb3612f03793"

    if inspection_type not in ["vehicle", "tire"]:
        raise ValueError("Invalid inspection type")

    current_date = datetime.now()
    current_month = current_date.month

    headers = {"Authorization": f"Token {TOKEN}"}
    data = []


    for month in range(1, 13):
        if month > current_month:
            break

        url = f"{BASE_URL}hiveSmanagement/API/INTEGRATIONS/{inspection_type.upper()}-INSPECTIONS?page=1&limit=500"
        params = {"month": month, "year": "2023"}
        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            data.extend(response.json()["data"])

    return data

def main():
    inspection_type = "tire"

    result = get_inspection_data(inspection_type)

    if result:
        df = pd.DataFrame(result)
        excel_filename = f'datos_{inspection_type}.xlsx'
        df.to_excel(excel_filename, index=False)
        print(f"Data saved to {excel_filename}")
    else:
        print("No data found")

if __name__ == "__main__":
    main()