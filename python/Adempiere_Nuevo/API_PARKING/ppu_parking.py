import logging

from connection import consume_api_updates, connect_to_db_tsm_nuevo, isactive_ppu, active_ppu

logging.basicConfig(filename='parking_error_ppu.log', level=logging.ERROR,
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)

try:
    # Establecer conexión a la base de datos
    conn = connect_to_db_tsm_nuevo()

    if conn:
        try:
            ppu_desactive = isactive_ppu(conn)
            ppu_active = active_ppu(conn)
            conn.close()

        except Exception as e:
            logger.error(
                "Error al obtener los pines activos y desactivados: %s", str(e))
    else:
        logger.error("No se pudo establecer conexión a la base de datos")

    if ppu_desactive:
        for ppu in ppu_desactive:
            data_desactive = {
                "accLevelIds": "4028948787dde47d0187dde53c950436",
                "pin": ppu
            }
            try:
                # Enviar solicitud a la API para desactivar el pin
                response_data = consume_api_updates(
                    "/person/add", data=data_desactive)
                logger.info(response_data)
            except Exception as e:
                logger.error(
                    "Error al enviar la solicitud a la API para desactivar el pin: %s", str(e))

    if ppu_active:
        for pin in ppu_active:
            data = {
                "accLevelIds": "4028948787dde47d0187dde53c950436",
                "pin": pin
            }
            try:
                # Enviar solicitud a la API para activar el pin
                response_data = consume_api_updates("/person/add", data=data)

                if response_data:
                    logger.info(response_data)
                else:
                    logger.error("Fallo en la solicitud a la API")
            except Exception as e:
                logger.error(
                    "Error al enviar la solicitud a la API para activar el pin: %s", str(e))
    else:
        logger.info("No se obtuvieron pines activos desde la base de datos")

except Exception as e:
    logger.error("Error al establecer conexión a la base de datos: %s", str(e))
