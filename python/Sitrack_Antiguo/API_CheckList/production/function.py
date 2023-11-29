import requests
import json
import psycopg2
from datetime import date, timedelta
import logging

logger = logging.getLogger(__name__)

# Conexion a la base de datos de TSM
def connect_to_db_tsm():
    try:
        conn = psycopg2.connect(
            host="192.168.1.29",
            database="tsm",
            user="api",
            password="Api2022",
            port=5432
        )
        logger.info("Connected to the database")
        return conn
    except psycopg2.Error as e:
        logger.error("Failed to connect to the database", e)
        return None

# Function clean the rut


def clean_rut(rut):
    rut = rut.replace('.', '').replace('-', '')
    rut = rut[:-1]
    return rut

# Function connect to the API


def API_connection():
    try:
        apiKey = 'Apikey b61023c484994f2d9fa64d9cd5545af7'
        url = 'https://api.sitrack.io/event/flow/trigger?wait=true'
        data = {
            'processId': 'd8f9d79d-82c5-43b0-9342-832d9dfff9e9',
            'date': (date.today() - timedelta(days=1)).isoformat()
            # 'date': '2023-05-08'
        }
        response = requests.post(url, json=data, headers={
                                 'Authorization': apiKey})
        response.raise_for_status()
        data = json.loads(response.text)
        return data
    except requests.exceptions.HTTPError as error:
        print("Connection failed:", error)
        return None
