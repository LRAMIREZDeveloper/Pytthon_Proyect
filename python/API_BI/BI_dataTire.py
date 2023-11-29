import requests
import pandas as pd
from datetime import datetime

base_url = "https://tsm.hivetire.app/"
token = "fcba4d869a72d68a19b01e1cfc3fcb3612f03793"
inspection_type = "TIRE-INSPECTIONS"

current_date = datetime.now()
current_month = int(current_date.strftime('%m'))

headers = {
    "Authorization": f"Token {token}"
}

ordered_data = []

for month in range(1, current_month + 1):
    url = f"{base_url}hiveSmanagement/API/INTEGRATIONS/{inspection_type}?page=1&limit=10000&month={month}&year=2023"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        ordered_data.extend(response.json()["data"])
        excel_path = f"TIRE.xlsx"

df = pd.DataFrame(ordered_data)
df.to_excel(excel_path)
