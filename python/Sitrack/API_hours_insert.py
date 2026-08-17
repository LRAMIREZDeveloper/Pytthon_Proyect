import http.client
import time
import json
import hashlib
import logging
import ssl
from base64 import b64encode
import urllib3
from datetime import datetime, timezone
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from pathlib import Path
from typing import List, Tuple, Any

import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_values


# Configuración del logging
logging.basicConfig(filename='connection_json.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)
   

def limpiar_fecha(fecha_str):
    return fecha_str.replace('-', '')

def connect_to_db_tsm_nuevo():
    try:
        conn = psycopg2.connect(
            host="adempiere.tsm.cl",
            database="tsm",
            user="pg_api",
            password="8YR53mDRavJlfd6d",
            port=5432
        )
        logger.info("Conexion exitosa a la BDD")
        return conn
    except psycopg2.Error as e:
        logger.error("Conexion fallido, error: ", e)
        return None

INSERT_SQL = """
    INSERT INTO bi.i_workday (
        driverdocument,
        totalhourstasks,
        roadmapid,
        fleetname,
        holderdomain,
        eventstartname,
        eventendname,
        datestart,
        dateend,
        timeseconds,
        firstodometer,
        lastodometer,
        distance,
        averagespeed,
        created
    )
    VALUES %s
"""

def _carga_json(json_path: str) -> list:
    """
    Lee el archivo JSON y devuelve una lista de objetos.
    Si el JSON raíz es un dict, lo envuelve en una lista.
    """
    p = Path(json_path)
    if not p.exists():
        raise FileNotFoundError(f"No se encuentra el archivo: {json_path}")
    with p.open('r', encoding='utf-8') as f:
        data = json.load(f)
    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list):
        raise ValueError("El JSON debe ser lista o dict en la raíz.")
    return data

def _aplanar_registros(data_hours: list, created: str) -> List[Tuple[Any, ...]]:
    """
    Transforma la lista de objetos de 'data_hours' al formato esperado por la tabla.
    Estructura esperada por cada elemento:
      {
        "driverDocument": "...",
        "totalHoursAuxiliaryTasks": 0,
        "items": [
          {
            "roadmapId": ...,
            "fleetName": "...",
            "holderDomain": "...",
            "eventStartName": "...",
            "eventEndName": "...",
            "time": 0,
            "firstOdometer": ...,
            "lastOdometer": ...,
            "distance": 0,
            "averageSpeed": 0,
            "dateEnd": "...",
            "dateStart": "..."
          }, ...
        ]
      }
    """
    rows = []
    for root in data_hours:
        driverDocument = root.get('driverDocument', '')
        totalHoursAuxiliaryTasks = root.get('totalHoursAuxiliaryTasks', 0)
        items = root.get('items', []) or []

        for detail in items:
            rows.append((
                driverDocument,
                totalHoursAuxiliaryTasks,
                detail.get('roadmapId'),
                detail.get('fleetName', ''),
                detail.get('holderDomain', ''),
                detail.get('eventStartName', ''),
                detail.get('eventEndName', ''),
                detail.get('dateStart', ''),
                detail.get('dateEnd', ''),
                detail.get('time', 0),
                detail.get('firstOdometer'),
                detail.get('lastOdometer'),
                detail.get('distance', 0),
                detail.get('averageSpeed', 0),
                created
            ))
    return rows

def main(json_path: str, created: str = '2025-08-04') -> None:
    """
    Proceso OFFLINE: inserta en bi.i_workday a partir de un archivo JSON local.
    - json_path: ruta al archivo JSON que enviarás.
    - created: fecha (string) que se guardará en la columna 'created'.
    """
    try:
        created_limpio = limpiar_fecha(created)

        # 1) Cargar JSON desde archivo
        data_hours = _carga_json(json_path)

        # 2) Aplanar/normalizar en filas para la tabla
        rows = _aplanar_registros(data_hours, created_limpio)

        if not rows:
            logger.info("No hay filas para insertar (JSON sin 'items').")
            print(created_limpio)
            return

        # 3) Insertar en bloque
        with connect_to_db_tsm_nuevo() as connection:
            try:
                with connection.cursor() as cursor:
                    # execute_values arma los VALUES (...), (...), (...) eficientemente
                    execute_values(cursor, INSERT_SQL, rows, page_size=1000)
                connection.commit()
                logger.info(f"Insertadas {len(rows)} filas en bi.i_workday.")
            except Exception as db_err:
                connection.rollback()
                logger.exception(f"Error al insertar en la base de datos: {db_err}")
                raise

        print(created_limpio)

    except FileNotFoundError as fe:
        logger.exception(str(fe))
        raise
    except json.JSONDecodeError as je:
        logger.exception(f"El archivo no es un JSON válido: {je}")
        raise
    except Exception as e:
        logger.exception(f"Error general en el proceso offline: {e}")
        raise


if __name__ == "__main__":
    main("C:/Users/lramirez/Github/Pytthon_Proyect/workday_20250826.json", created="2025-08-26")