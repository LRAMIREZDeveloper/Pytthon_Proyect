import requests
import base64
import xml.etree.ElementTree as ET
import json
import sys
import os

def load_db_config(env):
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    path = os.path.join(base_dir,'server','config', 'config.json')
    with open(path, 'r') as f:
        config = json.load(f)
    return config[env]


def extraer_detalle(xml_file):
    """
    Procesa un archivo XML y devuelve una lista de diccionarios con los detalles encontrados.
    No guarda nada en disco, solo devuelve la lista.
    """
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()

        ns = {'sii': 'http://www.sii.cl/SiiDte'}
        detalles = root.findall('.//sii:Detalle', ns)

        lista_detalles = []
        for detalle in detalles:
            nmb_item = detalle.find('sii:NmbItem', ns)
            dsc_item = detalle.find('sii:DscItem', ns)
            nro_linea = detalle.find('sii:NroLinDet', ns)
            qty_item = detalle.find('sii:QtyItem', ns)
            prc_item = detalle.find('sii:PrcItem', ns)
            mont_item = detalle.find('sii:MontoItem', ns)
            
            item_dict = {
                'NmbItem': nmb_item.text if nmb_item is not None else '',
                'DscItem': dsc_item.text if dsc_item is not None else '',
                'NroLinDet': nro_linea.text if nro_linea is not None else '',
                'QtyItem' : qty_item.text if qty_item is not None else '',
                'PrcItem': str(round(float(prc_item.text))) if prc_item is not None and prc_item.text else '',
                'MontoItem': mont_item.text if mont_item is not None else ''
            }
            
            lista_detalles.append(item_dict)

        return lista_detalles

    except Exception as e:
        print(f"Error al procesar el XML: {str(e)}", file=sys.stderr)
        sys.exit(1)



def obtener_dte_pdf(ip, group, rut, tipo, folio, auth_key):
    url = f"http://{ip}/api/Core.svc/core/RecoverXML_V2"
    headers = {
        "AuthKey": auth_key,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    body = {
        "Environment": "P",
        "Group": group,
        "Rut": rut,
        "DocType": tipo,
        "Folio": folio,
        "IsForDistribution": "true"
    }

    try:
        response = requests.post(url, headers=headers, json=body)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error HTTP {response.status_code}", file=sys.stderr)
            print(f"Respuesta: {response.text}", file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        print(f"Excepción al hacer la solicitud: {str(e)}", file=sys.stderr)
        sys.exit(1)


def guardar_xml_desde_json(json_data, output_path):
    if json_data and json_data.get("Data"):
        try:
            xml_content = base64.b64decode(json_data["Data"])
            with open(output_path, "wb") as f:
                f.write(xml_content)
        except Exception as e:
            print(f"Error al guardar el XML: {str(e)}", file=sys.stderr)
            sys.exit(1)
    else:
        print("El campo 'Data' está vacío o no contiene información.", file=sys.stderr)
        print("Mensaje:", json_data.get("Description", "Sin descripción") if json_data else "Sin respuesta", file=sys.stderr)
        sys.exit(1)


def main():
    folio = "14044168"
    rut_emisor = "96556940-5"
    tipo_dte = "33"


    # === CONFIGURACIÓN ===
    ip_dtebox = "200.6.99.113"
    group = "R"
    api_auth = "e94a9f68-79c1-4157-83ec-312951533703"

    xml_path = f'C:/Users/lramirez/Github/Pytthon_Proyect/extracted_files/DTE_{folio}.xml'

    # === USO ===
    json_resultado = obtener_dte_pdf(ip_dtebox, group, rut_emisor, tipo_dte, folio, api_auth)
    guardar_xml_desde_json(json_resultado, xml_path)
    detalles  = extraer_detalle(xml_path)

    if detalles is None:
        print("No se pudieron extraer detalles del XML", file=sys.stderr)

    print(json.dumps(detalles, ensure_ascii=False))


if __name__ == "__main__":
    main()
