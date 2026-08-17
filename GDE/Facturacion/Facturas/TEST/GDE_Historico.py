import datetime
from GDE_connection import obtener_dte, guardar_xml_desde_data, extraer_campos_y_guardar_json

def main():
    resultado = obtener_dte()
    current_time = datetime.datetime.now().strftime('%Y-%m-%d')

    if not resultado:
        print("No se pudo obtener resultado de la API.")
        return

    print("Cabeceras del resultado:")
    print(list(resultado.keys()))

    # 🔥 Buscar primero 'Data', si no existe usar 'data'
    data_base64 = resultado.get('Data') or resultado.get('data')

    if data_base64:
        nombre_xml = f"data_{current_time}.xml"
        nombre_json = f"data_{current_time}.json"

        guardar_xml_desde_data(data_base64, nombre_xml)
        extraer_campos_y_guardar_json(nombre_xml, nombre_json)
    else:
        print("No se encontró el campo 'Data' ni 'data' en el resultado.")

if __name__ == "__main__":
    main()