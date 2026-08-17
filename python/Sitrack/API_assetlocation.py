import json
import logging
from connection import connect_to_api, user_login, call_apis

logging.basicConfig(filename='error_assetlocation.log', level=logging.ERROR,
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)

def data_asset():
    try:
        # Credenciales de usuario
        USER_NAME, PASSWORD = user_login()  
        server, _, _, _, _ ,context_location,_ = call_apis()
        response = connect_to_api(USER_NAME, PASSWORD, server, context_location)
        body = response.read().decode('utf-8')  
        data_list = [] 
        if response.getcode() == 200:
            assets = json.loads(body)
            for asset in assets:
                data = {
                    'assetId': asset.get('assetId'),
                    'location': asset.get('location'),
                }
                data_list.append(data)
        return data_list
    except Exception as e:
        logger.error('Error: {}'.format(e))
        return None

if __name__ == "__main__":
    datos = data_asset()
    print (json.dumps(datos))