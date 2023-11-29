import logging
from connection import consume_api_updates, connect_to_db_tsm_nuevo, isactive_ppu, active_ppu

logging.basicConfig(filename='parking_error_ppu.log', level=logging.ERROR,
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)

ACC_LEVEL_IDS = "4028948787dde47d0187dde53c950436"

def get_and_activate_ping():
    try:
        conn = connect_to_db_tsm_nuevo()
        if not conn:
            logger.error("No se pudo establecer conexión a la base de datos")
            return

        ppu_desactive = isactive_ppu(conn)
        ppu_active = active_ppu(conn)
        conn.close()

        #logger.info(ppu_active)
        #logger.info(ppu_desactive)

        activate_pins(ppu_active)
        deactivate_pins(ppu_desactive)

    except Exception as e:
        logger.error("Error general: %s", str(e))

def activate_pins(ppu_active):
    if not ppu_active:
        logger.info("No se obtuvieron pines activos desde la base de datos")
        return

    for pin in ppu_active:
        data = {"accLevelIds": ACC_LEVEL_IDS, "pin": pin}
        try:
            response_data = consume_api_updates("/person/add", data=data)
            if response_data:
                logger.info(response_data)
            else:
                logger.error("Fallo en la solicitud a la API")
        except Exception as e:
            logger.error("Error al enviar la solicitud a la API para activar el pin: %s", str(e))

def deactivate_pins(ppu_desactive):
    if not ppu_desactive:
        return

    for ppu in ppu_desactive:
        data_desactive = {"accLevelIds": ACC_LEVEL_IDS, "pin": ppu}
        try:
            response_data = consume_api_updates("/person/add", data=data_desactive)
            logger.info(response_data)
        except Exception as e:
            logger.error("Error al enviar la solicitud a la API para desactivar el pin: %s", str(e))

if __name__ == "__main__":
    get_and_activate_ping()
