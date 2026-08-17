import json
import logging
import pandas as pd
import sys
sys.path.append('C:/Users/lramirez/Github/Pytthon_Proyect/python/Sitrack') 
from connection import connect_to_api, user_login, call_apis

logging.basicConfig(filename='error_alarmsExcel.log', level=logging.ERROR,
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')

def main():
    try:
        USER_NAME, PASSWORD = user_login()
        SERVER,_,_,_,_,_,CONTEXT_ASSETLOCATION = call_apis()
        response = connect_to_api(USER_NAME, PASSWORD, SERVER, CONTEXT_ASSETLOCATION)
        print('HTTP Code:',response.getcode())
        
        body = response.read().decode('utf-8')
        print("Exito en la conexion a la API")
        dataBody = '[' + body + ']'
        data = json.loads(dataBody)
        data_list =  []
        if response.getcode() == 200:
            data_asset = json.loads(dataBody)
            for item in data_asset:
                data = {
                    'assetId': item.get('assetId', ''),
                    'reportDate': item.get('reportDate', ''),
                    'odometer':item.get('odometer', ''),
                    'zoneName': item.get('zoneName', ''),
                    'zoneCondition':item.get('zoneCondition', ''),}
                data_list.append(data)
        df = pd.DataFrame(data_list)
        df.to_excel('asset_data.xlsx', index=False)
    except Exception as e:
        print(f'Error en la lectura de la respuesta: {e}')
        
if __name__ == "__main__":
    main()