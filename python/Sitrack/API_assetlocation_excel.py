import json
import logging
import pandas as pd
from connection import connect_to_api, user_login, call_apis

logging.basicConfig(
    filename='error_assetlocation.log',
    level=logging.ERROR,
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)

logger = logging.getLogger(__name__)


def data_asset():
    try:
        # Credenciales de usuario
        USER_NAME, PASSWORD = user_login()

        server, _, _, _, _, context_location, _ = call_apis()

        response = connect_to_api(
            USER_NAME,
            PASSWORD,
            server,
            context_location
        )

        body = response.read().decode('utf-8')

        if response.getcode() == 200:

            # Convertir respuesta a JSON
            assets = json.loads(body)

            # Convertir TODOS los datos del JSON a un DataFrame
            # json_normalize permite expandir objetos internos
            df = pd.json_normalize(assets)

            # Crear archivo Excel
            nombre_archivo = 'assets.xlsx'

            df.to_excel(
                nombre_archivo,
                index=False,
                engine='openpyxl'
            )

            print(f'Excel creado correctamente: {nombre_archivo}')
            print(f'Total de assets encontrados: {len(df)}')
            print('Columnas encontradas:')
            
            for columna in df.columns:
                print(f'- {columna}')

            return assets

        else:
            print(f'Error API: {response.getcode()}')
            return None

    except Exception as e:
        logger.error('Error: {}'.format(e))
        print(f'Error: {e}')
        return None


if __name__ == "__main__":
    datos = data_asset()