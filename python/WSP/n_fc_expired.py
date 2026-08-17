import logging 
import time
from connection import connect_to_db_tsm_nuevo, getnotificationwsp
from queries import user_data, ppu_data


# Configuración del logging
logging.basicConfig(filename='wsp_fc.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)


with connect_to_db_tsm_nuevo() as connection:
    with connection.cursor() as cursor:
        cursor.execute(user_data)
        data = cursor.fetchall()
        
        if not data:
            print("No hay datos para enviar notificaciones.")
        else:
            for datos in data:
                supervisor, phone = datos
                cursor.execute(ppu_data)
                rows = cursor.fetchall()

                # Verifica si hay datos antes de procesar
                if not rows:
                    print("No hay datos para enviar notificaciones.")
                else:
                    for row in rows:
                        ppu, date, concept_name = row
                        notification = getnotificationwsp(date, ppu, concept_name, supervisor)
                        print(f'Notificación enviada: {notification.status_code}')
                        time.sleep(2)  # Espera 2 segundos entre envíos
