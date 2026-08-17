import requests
import sys

def aprobar_factura(ip, rut, tipo, folio, auth_key):
    url = f"http://{ip}/api/Core.svc/core/SendComercialResponse"
    headers = {
        "AuthKey": auth_key,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    body = {
    "Environment" : "P", 
    "RutEmisor" : rut, 
    "DTEType" : tipo, 
    "Folio" : folio, 
    "ContactName" : "Valentina Lorca", 
    "ContactPhone" : "+56938697242", 
    "ContactEmail" : "vlorca@tsm.cl", 
    "Observations" : "Aprobación realizada a traves de integraciones", 
    "ResponseType" : "A", 
    "Action" : "0" 
}

    try:
        response = requests.post(url, headers=headers, json=body)
        print(f"Estado HTTP: {response.status_code}")

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error HTTP {response.status_code}")
            print("Respuesta:", response.text)
            return None

    except Exception as e:
        print("Excepción al hacer la solicitud:", str(e))
        return None


def main():
    
    folio = "547"
    rut_emisor = "77340861-0"
    tipodte = "33"

        # === CONFIGURACIÓN ===
    ip_dtebox = "200.6.99.113"
    api_auth = "e94a9f68-79c1-4157-83ec-312951533703"
    
    # === USO ===
    json_resultado = aprobar_factura(ip_dtebox, rut_emisor, tipodte, folio, api_auth)
    print(json_resultado)


if __name__ == "__main__":
    main()