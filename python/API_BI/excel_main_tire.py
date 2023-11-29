from connection import ordered_data_tire, save_to_excel, get_inspection_data_main
from datetime import datetime
import os


def main():
    date = datetime.now()
    month = date.strftime('%m')
    month_detail = '7'
    year = date.strftime('%Y')

    result = get_inspection_data_main("tire", month_detail, year)

    if result:
        data_list = result["data"]

        ordered_data = ordered_data_tire(data_list)

        excel_path = f"{month_detail}-{year}_TIRE.xlsx"

        if os.path.exists(excel_path):
            os.remove(excel_path)

        save_to_excel(ordered_data, excel_path)
    else:
        print("No data found")


if __name__ == "__main__":
    main()
