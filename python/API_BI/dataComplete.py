from connection import save_to_excel,get_inspection_data
import os


def main():

    ordered_data = get_inspection_data("vehicle")
    excel_path = f"VEHICLE_General.xlsx"

    # Eliminar el archivo existente si existe
    if os.path.exists(excel_path):
        os.remove(excel_path)

    save_to_excel(ordered_data, excel_path)


if __name__ == "__main__":
    main()
