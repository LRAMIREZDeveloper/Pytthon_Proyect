import logging
import time
import logging
import json

from connection import connect_to_db_tsm_nuevo, getnotificationwsp2,send_text_message
from queries import user_data

# Configuración del logging

logging.basicConfig(filename='wsp_variable.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)


response = getnotificationwsp2("2025-02-10", "ABC123", "Mantenimiento", "Juan Pérez")
#send_text_message()