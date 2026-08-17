import json
import logging
import pandas as pd
import datetime
import sys
sys.path.append('C:/Users/lramirez/Github/Pytthon_Proyect/python/Sitrack') 
from connection import connect_to_api, user_login, call_apis, clean_rut

logging.basicConfig(filename='error_alarmsExcel.log', level=logging.ERROR,
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')

def main():
    try:
        USER_NAME, PASSWORD = user_login()
        SERVER,_,CONTEXT_ALARMS,_,_,_ = call_apis()
        response = connect_to_api(USER_NAME, PASSWORD, SERVER, CONTEXT_ALARMS)
        print('HTTP Code:',response.getcode())
        
        body = response.read().decode('utf-8')
        print("Exito en la conexion a la API")
        
        data_list =  []
        created = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if response.getcode() == 200:
            alarms = json.loads(body)
            id_alarms = alarm.get('id', '')
            for alarm in alarms:
                delay_time = int(float(alarm.get('delayTime', 0)))
                document = alarm.get('document', '')
                cleaned_document = clean_rut(document) if document else ''
                speed = alarm.get('speed', 0) if alarm.get('speed') is not None else 0
                speedMax = alarm.get('speedMax', 0) if alarm.get('speedMax') is not None else 0
                speedMaxLimit = alarm.get('speedMaxLimit', 0) if alarm.get('speedMaxLimit') is not None else 0
                data = {
                    'holderDomain': alarm.get('holderDomain', ''),
                    'entryDate': alarm.get('entryDate', ''),
                    'observation':alarm.get('observation', ''),
                    'delay_time':delay_time,
                    'speed': speed,
                    'latitude': alarm.get('latitude', ''),
                    'longitude':alarm.get('longitude', ''),
                    'location': alarm.get('location', ''),
                    'document': cleaned_document,
                    'driverName':alarm.get('driverName', ''),
                    'fleets': alarm.get('fleets', [{}])[0].get('name', ''),
                    'comment':alarm.get('comment', ''),
                    'duration':alarm.get('duration', ''),
                    'speedMax':speedMax,
                    'overspeedStartDate':alarm.get('overspeedStartDate', ''),
                    'speedMaxLimit':speedMaxLimit,
                    'zoneName': alarm.get('zoneName', ''),
                    'id':id_alarms,
                    'positionDate':alarm.get('positionDate', ''),
                    'created':created}
                data_list.append(data)
        df = pd.DataFrame(data_list)
        df.to_excel('alarms_data.xlsx', index=False)
    except Exception as e:
        print(f'Error en la lectura de la respuesta: {e}')
        
if __name__ == "__main__":
    main()