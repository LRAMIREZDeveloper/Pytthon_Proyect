import logging

from connection import consume_api_updates, connect_to_db_tsm_nuevo, isactive_partner, active_partner

logging.basicConfig(filename='parking_error_partner.log', level=logging.ERROR,
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)

try:
    # Establecer conexión a la base de datos
    conn = connect_to_db_tsm_nuevo()

    if conn:
        try:
            partner_desactive = isactive_partner(conn)
            partner_active = active_partner(conn)
            conn.close()

            logger.info(partner_desactive)
            logger.info(partner_active)

        except Exception as e:
            logger.error(
                "Error al obtener los pines activos y desactivados: %s", str(e))
    else:
        logger.error("No se pudo establecer conexión a la base de datos")

    if partner_active:
        for pin in partner_active:
            data = {
                "isDisabled": False,
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
        logger.info("No se obtuvieron pines activos desde la base de datos, 1")

    if partner_desactive:
        for partner in partner_desactive:
            data_desactive = {
                "isDisabled": False,
                "pin": partner
            }
            try:
                # Enviar solicitud a la API para desactivar el pin
                response_data = consume_api_updates(
                    "/person/add", data=data_desactive)
                logger.info(response_data)
            except Exception as e:
                logger.error(
                    "Error al enviar la solicitud a la API para desactivar el pin: %s", str(e))
    else:
        logger.info("No se obtuvieron pines activos desde la base de datos, 2")
except Exception as e:
    logger.error("Error al establecer conexión a la base de datos: %s", str(e))
