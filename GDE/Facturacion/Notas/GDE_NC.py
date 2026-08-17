import datetime
from GDE_connection_NC import obtener_dte, guardar_xml_desde_data, extraer_campos_y_guardar_json, procesar_json_e_insertar

def main():
    resultado = obtener_dte()
    current_time = datetime.datetime.now().strftime('%Y-%m-%d')

    if resultado:
        data_base64 = resultado.get('Data')

        if data_base64:
            nombre_xml = f"data_{current_time}.xml"
            nombre_json = f"data_{current_time}.json"
            guardar_xml_desde_data(data_base64, nombre_xml)
            extraer_campos_y_guardar_json(nombre_xml, nombre_json)
            #procesar_json_e_insertar(nombre_json)
        else:
            print("No se encontró el campo 'Data' en el resultado.")
    else:
        print("No se pudo obtener resultado de la API.")


if __name__ == "__main__":
    main()