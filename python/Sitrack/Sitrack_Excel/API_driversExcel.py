import json
import logging
import pandas as pd
import datetime
import sys
sys.path.append('C:/Users/lramirez/Github/Pytthon_Proyect/python/Sitrack') 
from connection import connect_to_api_driverscontrol, user_login, request_session, call_apis

logging.basicConfig(filename='error_driversExcel.log', level=logging.ERROR,
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)

def main():
    # Credenciales de usuario
    USER_NAME, PASSWORD = user_login()

    # Dirección de servidor y contexto de las APIs
    SERVER, PATH_SPEED, _, _, PATH_STOPPED,_,_ = call_apis()

    # Solicitud de sesión
    SESSIONID, SECRETKEY = request_session(SERVER, USER_NAME, PASSWORD)
    records = []

    # Procesar e insertar datos de la API de velocidad y detenciones
    for context in [PATH_SPEED, PATH_STOPPED]:
        try:
            response = connect_to_api_driverscontrol(
                SESSIONID, SECRETKEY, SERVER, context)
            print('HTTP Code:', response.getcode())
        except Exception as e:
            logger.error(f'Error de conexión a la API Driverscontrol, tipo: {context} Error:  {e}')
        try:
            body = response.read().decode('utf-8')
            dataBody = '[' + body + ']'
            data = json.loads(dataBody)
            print(data)
        except Exception as e:
            logger.error(f'Error de conexión a la API Driverscontrol, tipo: {context} Error:  {e}')
        try:
            current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            description = 'Integracion con Sitrack'
            for item in data:
                initialDate = item.get('initialDate')
                initialTime = item.get('initialTime')
                finalDate = item.get('finalDate')
                finalTime = item.get('finalTime')
                totaltime = item.get('totalTime')
                date = item.get('date')
                time = item.get('time')
                zoneName = item.get('zoneName')
                speed = item.get('speed')
                excessType = item.get('excessType')
                speedMax = item.get('speedMax')

                # Verificar si las variables contienen datos válidos antes de convertirlas
                datetime_startime = None
                datetime_endtime = None
                datetime_total = None
                datetime_str = None

                if date and time:
                    date_obj = datetime.datetime.strptime(date, '%d-%m-%y')
                    time_obj = datetime.datetime.strptime(time, '%H:%M:%S')
                    datetime_obj = datetime.datetime.combine(
                        date_obj.date(), time_obj.time())
                    datetime_str = datetime_obj.strftime('%Y-%m-%d %H:%M:%S')

                if initialDate and initialTime:
                    initialDate_obj = datetime.datetime.strptime(
                        initialDate, '%d-%m-%y')
                    initialDate = initialDate_obj.strftime('%Y-%m-%d')
                    initialTime_obj = datetime.datetime.strptime(
                        initialTime, '%H:%M:%S')
                    datetime_obj2 = datetime.datetime.combine(
                        initialDate_obj.date(), initialTime_obj.time())
                    datetime_startime = datetime_obj2.strftime('%Y-%m-%d %H:%M:%S')

                if finalDate and finalTime:
                    finalDate_obj = datetime.datetime.strptime(
                        finalDate, '%d-%m-%y')
                    finalTime_obj = datetime.datetime.strptime(
                        finalTime, '%H:%M:%S')
                    tiempo_detencion = datetime.datetime.combine(
                        finalDate_obj.date(), finalTime_obj.time())
                    datetime_endtime = tiempo_detencion.strftime(
                        '%Y-%m-%d %H:%M:%S')

                if totaltime:
                    try:
                        totaltime_obj2 = datetime.datetime.strptime(
                            totaltime, '%H:%M:%S')
                        datetime_total = totaltime_obj2.strftime(
                            '%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        datetime_total = None
                # Procesar los datos y guardarlos en una lista
                record = {
                    'location': item.get('location', ''),
                    'excesstype': excessType if item.get('typematrix') == 'VE' else None,
                    'controldate': datetime_str if item.get('typematrix') == 'VE' else datetime_startime,
                    'description': description,
                    'endtime': datetime_endtime if item.get('typematrix') == 'DE' and datetime_endtime is not None else None,
                    'driver': item.get('driver', ''),
                    'fleet': item.get('fleet', ''),
                    'domain': item.get('domain', ''),
                    'latitude': item.get('latitude', ''),
                    'longitude': item.get('longitude', ''),
                    'speedmax': speedMax if item.get('typematrix') == 'VE' else None,
                    'speed': speed if item.get('typematrix') == 'VE' else None,
                    'starttime': datetime_startime if item.get('typematrix') == 'DE' and datetime_startime is not None else None,
                    'typematrix': item.get('typematrix'),
                    'waittime': datetime_total if item.get('typematrix')== 'DE' and datetime_total is not None else None,
                    'zonename': zoneName if item.get('typematrix') == 'VE' else None,
                    'created': current_time
                }
                records.append(record)
        except Exception as e:
            logger.error(f'Error de conexión a la API Driverscontrol, tipo: {context} Error:  {e}')
    df = pd.DataFrame(records)
    filename = f"driverscontrol_{datetime.date.today()}.xlsx"
    df.to_excel(filename, index=False)
            
if __name__ == "__main__":
    main()
