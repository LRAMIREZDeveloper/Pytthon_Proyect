import logging
from decimal import Decimal
import requests


# Configuración del logging
logging.basicConfig(filename='GDE_log_reclassification.log', level=logging.DEBUG, format='%(asctime)s | %(levelname)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)


#=================== Utilidades =========================
def norm(v):
    if isinstance(v, Decimal):
        try:
            return int(v)  # si es entero
        except Exception:
            return float(v)  # o str(v) si prefieres
    return v


#================ Funcion para realizar la aprobación de la factura en caso de que caiga en "Recepcionar" ==================

def gte_approver_facct(ip, rut, tipo, folio, auth_key):
    url = f"http://{ip}/api/Core.svc/core/SendComercialResponse"
    headers = {
        "AuthKey": auth_key,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
 
    body = {
    "Environment" : "P", 
    "RutEmisor" : rut, 
    "DTEType" : norm(tipo), 
    "Folio" : norm(folio), 
    "ContactName" : "Valentina Lorca", 
    "ContactPhone" : "+56938697242", 
    "ContactEmail" : "vlorca@tsm.cl", 
    "Observations" : "Aprobacion realizada a traves de integraciones", 
    "ResponseType" : "A", 
    "Action" : "0" 
} 
    response = requests.post(url, headers=headers, json=body)
    print(f"Estado HTTP: {response.status_code}")

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error HTTP {response.status_code}")
        print("Respuesta:", response.text)
        return None

#=============== Orquestación de las funciones ================

def main():
    folio = "46755"
    rut_emisor = "77667230-0"
    tipo = "33"
    ip_dtebox = "200.6.99.113"
    api_auth = "e94a9f68-79c1-4157-83ec-312951533703"

    json_resultado = gte_approver_facct(ip_dtebox, rut_emisor, tipo, folio, api_auth)
    print(f"Aprobación API: {json_resultado}")
            

if __name__ == "__main__":
    main()