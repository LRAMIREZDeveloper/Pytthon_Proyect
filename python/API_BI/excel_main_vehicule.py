from connection import ordered_data_vehicule, save_to_excel, get_inspection_data_main
import os

def main():

    result = get_inspection_data_main("vehicle", '','')

    if result:
        data_list = result["data"]
        
        ordered_data = ordered_data_vehicule(data_list)

        excel_path = f"VEHICULE.xlsx"
        
        # Eliminar el archivo existente si existe
        if os.path.exists(excel_path):
            os.remove(excel_path)
        
        save_to_excel(ordered_data, excel_path)
    else:
        print("No data found")

if __name__ == "__main__":
    main()