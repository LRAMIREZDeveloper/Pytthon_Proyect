import requests
import psycopg2
import logging
import os
from dotenv import load_dotenv

# Configuración del logging
logging.basicConfig(filename='wsp_connection.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)

# Cargar variables de entorno desde el archivo .env
load_dotenv("pass.env")

def connect_to_db_tsm_nuevo():
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT")
        )
        logger.info("Conexión exitosa a la BDD")
        return conn
    except ValueError as e:
        logger.error(f"Error de configuración: {e}")
        return None
    except psycopg2.Error as e:
        logger.error(f"Conexión fallida, error: {e}")
        return None


def send_text_message():
    
    token = os.getenv("FB_TOKEN")
    
    url = "https://graph.facebook.com/v21.0/566514616542708/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": "56989551020",
        "type": "text",
        "text": {
            "body": "Hola, este es un mensaje de prueba desde la API de WhatsApp."
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    print("Status Code:", response.status_code)
    print("Response JSON:", response.json())


def getnotificationwsp2(date, ppu, concepto, supervisor):
    url = "https://graph.facebook.com/v21.0/566514616542708/messages"
    headers = {
        "Authorization": "Bearer EAAOTuXcyn2sBOysYAWCR1erJzgI9mLqGUlq0zvcQNH8JKUEV1o3vKgVTFzPqzNQRz1DHZB2Ye2BRSwoDOQZBGCRJ1BjxziFeeH9UGu8iZAXPywyZB5M2sG9ALTc8ZBgvBl4v2RjI4RqdZBzXZC9ZA7GZAAr6cOK8H8S5p7SrDsuMSfjoeumKAnXXoQqtmZB0ibJUHx5QZDZD",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": "56997419280",  # Número del usuario
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": f"Hola {supervisor}, ¿confirmas la acción del {date} para el vehículo {ppu} por {concepto}?"
            },
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": "YES_CONFIRM",
                            "title": "Sí"
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "NO_CONFIRM",
                            "title": "No"
                        }
                    }
                ]
            }
        }
    }
    
    response = requests.post(url, headers=headers, json=payload)
    
    print (response.status_code)
    print (response.json())

    return response.json()

def getnotificationwsp(date, ppu, concepto, supervisor):
    
    token = os.getenv("FB_TOKEN")

    url = "https://graph.facebook.com/v21.0/566514616542708/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    # Cuerpo de la solicitud (payload)
    payload = {
        "messaging_product": "whatsapp",
        "to": "56997419280",
        "type": "template",
        "template": {
            "name": "fc_defeated",
            "language": {
                "code": "es_ES"
            },
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "parameter_name": "name","text": f"{supervisor}"},
                        {"type": "text", "parameter_name": "date","text": f"{date}"},
                        {"type": "text", "parameter_name": "ppu","text": f"{ppu}"},
                        {"type": "text", "parameter_name": "concept","text": f"{concepto}"}
                    ]
                }
            ]
        }
    }
    response = requests.post(url, headers=headers, json=payload)
 
    return response