import logging
from conec import connect_to_db_tsm, isactive_ppu, active_ppu, activate_pins, deactivate_pins

logging.basicConfig(filename='parking_error_ppu.log', level=logging.ERROR,
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)

def get_and_activate_ping():
    try:
        conn = connect_to_db_tsm()
        if not conn:
            logger.error("No se pudo establecer conexión a la base de datos")
            return

        ppu_deactivate = isactive_ppu(conn)
        ppu_active = active_ppu(conn)
        conn.close()

        # logger.info(ppu_active)
        # logger.info(ppu_desactive)
        if ppu_active:
            activate_pins(ppu_active)
        else:
            logger.error("No se pudo activar el PPU")

        if ppu_deactivate:
            deactivate_pins(ppu_deactivate)
        else:
            logger.error("No se pudo desactivar el PPU")

    except Exception as e:
        logger.error("Error general: %s", str(e))


if __name__ == "__main__":
    get_and_activate_ping()