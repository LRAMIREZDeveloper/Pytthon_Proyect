import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import psycopg2
import datetime
import logging

logging.basicConfig(filename='function_error.log', level=logging.ERROR,
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)

# Desactivar advertencias de verificación de certificado SSL
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

#CONSULTAS A BDD.

# Conexion a la BDD
def connect_to_db_tsm():
    try:
        conn = psycopg2.connect(
            host="192.168.1.29",
            database="tsm",
            user="api",
            password="Api2022",
            port=5432
        )
        print("Connected to the database")
        return conn
    except psycopg2.Error as e:
        print("Failed to connect to the database", e)
        return None

# Qry para la activacion de usuarios
def active_ppu(conn):
    cur = conn.cursor()
    try:
        query = """
        SELECT ppu_ping FROM api.i_parking_ppu WHERE ppu_ping = 'HHBG86'
        """
        cur.execute(query)
        results = cur.fetchall()
        # Eliminar duplicados utilizando un conjunto (set)
        ppu_active = list(set([row[0] for row in results]))
        return ppu_active
    except Exception as e:
        print("Error al recuperar datos de la base de datos", e)
        return []
    finally:
        cur.close()


# Qry para realizar bloqueo de usuarios en ZKBio
def isactive_ppu(conn):
    cur = conn.cursor()
    try:
        query = """
        SELECT rut_ping FROM api.i_parking_partner
        WHERE rut_ping = '18365540K'
        """
        cur.execute(query)
        results = cur.fetchall()
        # Eliminar duplicados utilizando un conjunto (set)
        ppu_isactive = list(set([row[0] for row in results]))
        return ppu_isactive
    except Exception as e:
        print("Error al recuperar datos de la base de datos", e)
        return []
    finally:
        cur.close()


# Qry para realizar activacion de camiones para salir.
def active_partner(conn):
    cur = conn.cursor()
    try:
        query = """
        SELECT rut_ping FROM api.i_parking_partner
        WHERE rut_ping = '18365540K'
        """
        cur.execute(query)
        results = cur.fetchall()
        # Eliminar duplicados utilizando un conjunto (set)
        active_partner = list(set([row[0] for row in results]))
        return active_partner
    except Exception as e:
        print("Error al recuperar datos de la base de datos", e)
        return []
    finally:
        cur.close()


# Qry para realizar la salida de camiones.
def isactive_partner(conn):
    cur = conn.cursor()
    try:
        query = """
        SELECT rut_ping FROM api.i_parking_partner
        WHERE rut_ping = '166946743'
        """
        cur.execute(query)
        results = cur.fetchall()
        # Eliminar duplicados utilizando un conjunto (set)
        isactive_partner = list(set([row[0] for row in results]))
        return isactive_partner
    except Exception as e:
        print("Error al recuperar datos de la base de datos", e)
        return []
    finally:
        cur.close()

#---------------------------------------------------------------------------------------------------

#LLAMADO A LA API Y VALIDACION.

# Funcion relacionada al llamado de la API para la modificacion de datos de camiones o personal en ZKBio
def consume_api_updates(endpoint, params=None, data=None):
    api_url = "https://192.168.70.2:8098/api" + endpoint

    # Parámetros de la solicitud
    params = params or {}
    params["access_token"] = "E4A5367EBB66E37B7204A675EF00DF7DC13253F26CE8999AE45DFCA615985836"

    # Realizar la solicitud a la API sin verificar el certificado SSL
    response = requests.post(api_url, params=params, json=data, verify=False)

    # Verificar el código de estado de la respuesta
    if response.status_code == 200:
        data = response.json()  # Obtener los datos de la respuesta en formato JSON
        return data
    else:
        # La solicitud falló
        print("Error al consumir la API. Código de estado:", response.status_code)
        if response.status_code == 400:
            error_message = response.json().get("message")
            if error_message:
                print("Mensaje de error:", error_message)
            else:
                print("No se proporcionó un mensaje de error en la respuesta.")
        else:
            print("Error desconocido.")


# Funcion relacionada con la insercion o modificacion de ID desde ZKBio
def consume_api_user(endpoint, pageNo=1, pageSize=1000, params=None, data=None):
    api_url = "https://192.168.70.2:8098/api" + endpoint

    # Parámetros de la solicitud
    params = params or {}
    params["access_token"] = "E4A5367EBB66E37B7204A675EF00DF7DC13253F26CE8999AE45DFCA615985836"
    params["pageNo"] = pageNo
    params["pageSize"] = pageSize

    # Realizar la solicitud a la API sin verificar el certificado SSL
    response = requests.post(api_url, params=params, json=data, verify=False)

    # Verificar el código de estado de la respuesta
    if response.status_code == 200:
        data = response.json()  # Obtener los datos de la respuesta en formato JSON
        return data
    else:
        # La solicitud falló
        print("Error al consumir la API. Código de estado:", response.status_code)
        if response.status_code == 400:
            error_message = response.json().get("message")
            if error_message:
                print("Mensaje de error:", error_message)
            else:
                print("No se proporcionó un mensaje de error en la respuesta.")
        else:
            print("Error desconocido.")


# Codigo validador de patentes o usuarios, impidiendo el ingreso de datos duplicados.
def get_counts_for_pin(cur, pin):
    query_user_count = "SELECT COUNT(*) FROM api.i_parking_partner WHERE rut_ping = %s"
    cur.execute(query_user_count, (pin,))
    count_user = cur.fetchone()[0]

    query_ppu_count = "SELECT COUNT(*) FROM api.i_parking_ppu WHERE ppu_ping = %s"
    cur.execute(query_ppu_count, (pin,))
    count_ppu = cur.fetchone()[0]

    return count_user, count_ppu

#-----------------------------------------------------------------------------------------------------

#PROCESAR LOS DATOS.

# Función para procesar los datos obtenidos de la API
def process_api_data(data, cur, conn):
    for item in data.get('data', []):
        created = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        pin = str(item.get('pin', ''))
        dptname = str(item.get('deptName', ''))
        name = str(item.get('name', ''))
        lastname = str(item.get('lastName', ''))
        accLevelIds = str(item.get('accLevelIds', ''))
        full_name = name + " " + lastname

        count_user, count_ppu = get_counts_for_pin(cur, pin)

        if count_user == 0 and count_ppu == 0:
            if len(pin) == 6 or len(pin) == 5:
                insert_data(cur, conn, pin, name, lastname,
                            accLevelIds, created, dptname)
            else:
                insert_data(cur, conn, pin, name, lastname,
                            accLevelIds, created, dptname)
        else:
            if len(pin) == 6 or len(pin) == 5:
                modify_ppu_data(cur, conn, pin, full_name,
                                 accLevelIds, dptname)
            else:
                modify_user_data(cur, conn, pin, full_name,
                                  accLevelIds, dptname)

# Codigo para procesar los datos de PPU
def modify_ppu_data(cur, conn, pin, full_name, accLevelIds, dptname):
    query_ppu = "SELECT ppu_ping, name, acclevelids, dptname FROM api.i_parking_ppu WHERE ppu_ping = %s"
    cur.execute(query_ppu, (pin,))
    result_ppu = cur.fetchone()
    if result_ppu is not None:
        bdd_ppu = result_ppu[0]
        ppu_name = result_ppu[1]
        ppu_acclevelids = result_ppu[2]
        ppu_dptname = result_ppu[3]
        update_ppu_data(cur, conn, pin, full_name, accLevelIds,
                        dptname, bdd_ppu, ppu_name, ppu_acclevelids, ppu_dptname)
    else:
        print('Proceso sin PPU a modificar')

# Funcion para la modificacion de patentes
def update_ppu_data(cur, conn, pin, full_name, accLevelIds, dptname, bdd_ppu, ppu_name, ppu_acclevelids, ppu_dptname):
    if full_name != ppu_name or accLevelIds != ppu_acclevelids or dptname != ppu_dptname:
        query_update_ppu = "UPDATE api.i_parking_ppu SET ppu_ping = %s, name = %s, acclevelids = %s, dptname = %s WHERE ppu_ping = %s"
        cur.execute(query_update_ppu, (pin, full_name,
                    accLevelIds, dptname, bdd_ppu))
        conn.commit()

# Codigo para procesar los datos de usuarios
def modify_user_data(cur, conn, pin, full_name, accLevelIds, dptname):
    query_user = "SELECT rut_ping, name, acclevelids, dptname FROM api.i_parking_partner WHERE rut_ping = %s"
    cur.execute(query_user, (pin,))
    result_user = cur.fetchone()
    if result_user is not None:
        bdd_user = result_user[0]
        user_name = result_user[1]
        user_acclevelids = result_user[2]
        user_dptname = result_user[3]
        update_user_data(cur, conn, pin, full_name, accLevelIds, dptname,
                         bdd_user, user_name, user_acclevelids, user_dptname)

# Funcion para la modificacion de usuarios
def update_user_data(cur, conn, pin, full_name, accLevelIds, dptname, bdd_user, user_name, user_acclevelids, user_dptname):
    if full_name != user_name or accLevelIds != user_acclevelids or dptname != user_dptname:
        query_update_user = "UPDATE api.i_parking_partner SET rut_ping = %s, name = %s, acclevelids = %s, dptname = %s WHERE rut_ping = %s"
        cur.execute(query_update_user, (pin, full_name,
                    accLevelIds, dptname, bdd_user))
        conn.commit()


# Codigo para la insercion de datos.
def insert_data(cur, conn, pin, name, lastname, accLevelIds, created, dptname):
    fullname = f"{name} {lastname}"
    if len(pin) == 6 or len(pin) == 5:
        insert_query = "INSERT INTO api.i_parking_ppu (ppu_ping, name, accLevelIds, created, dptname) VALUES (%s, %s, %s, %s, %s)"
        # Es una patente de auto o moto
        values = (pin, fullname, accLevelIds, created, dptname)
    else:
        # Es un RUT de persona
        rut_adempiere = pin[:-1]  # Obtener PIN sin el último dígito
        values = (pin, rut_adempiere, fullname, accLevelIds, created, dptname)
        insert_query = "INSERT INTO api.i_parking_partner (rut_ping, rut_adempiere, name, accLevelIds, created, dptname) VALUES (%s, %s, %s, %s, %s, %s)"
    cur.execute(insert_query, values)
    conn.commit()

#------------------------------------------------------------------------------------

# FUNCIONES CREADAS PARA LAS PRUEBAS DE METODOLOGIAS DE INSERCION.

# Funcion para la activacion de las ppu para salida diaria
def activate_pins(ppu_active):
    access_general = "4028948787dde47d0187dde53c950436"
    # access_tag_input = "4028c68288b7c8e40188d44de00c592d"
    # access_tag_output = "4028c68288b7c8e40188d4389f82578c"
    if not ppu_active:
        logger.info("No se obtuvieron pines activos desde la base de datos")
        return

    for pin in ppu_active:
        data = {"accLevelIds": access_general, "pin": pin}
        try:
            response_data = consume_api_updates("/person/add", data=data)
            if response_data:
                logger.info(response_data)
            else:
                logger.error("Fallo en la solicitud a la API")
        except Exception as e:
            logger.error(
                "Error al enviar la solicitud a la API para activar el pin: %s", str(e))


# Funcion para la desactivación de las ppu para salida diaria
def deactivate_pins(ppu_desactive):
    access_general = "4028948787dde47d0187dde53c950436"
    # access_tag_input = "4028c68288b7c8e40188d44de00c592d"
    # access_tag_output = "4028c68288b7c8e40188d4389f82578c"
    if not ppu_desactive:
        return

    for ppu in ppu_desactive:
        data_desactive = {"accLevelIds": access_general, "pin": ppu}
        try:
            response_data = consume_api_updates(
                "/person/add", data=data_desactive)
            if response_data:
                logger.info(response_data)
            else:
                logger.error("Fallo en la solicitud a la API")
        except Exception as e:
            logger.error(
                "Error al enviar la solicitud a la API para desactivar el pin: %s", str(e))


# Funcion para la activacion de los usuarios para salida diaria
def activate_pins_partner(partner_active):
    for pin in partner_active:
        data_active = {
            "isDisabled": False,
            "pin": pin
        }
        try:
            response_data_active = consume_api_updates(
                "/person/add", data=data_active)
            if response_data_active:
                logger.info(response_data_active)
            else:
                logger.error("Fallo en la solicitud a la API")
        except Exception as e:
            print("Error al enviar la solicitud a la API para activar el pin:", str(e))
            return False
    return True


# Funcion para la desactivación de los usuarios para salida diaria
def deactivate_pins_partner(partner_desactive):
    for partner in partner_desactive:
        data_desactive = {
            "isDisabled": False,
            "pin": partner
        }
        try:
            response_data_desactive = consume_api_updates(
                "/person/add", data=data_desactive)
            if response_data_desactive:
                logger.info(response_data_desactive)
            else:
                logger.error("Fallo en la solicitud a la API")
        except Exception as e:
            print("Error al enviar la solicitud a la API para desactivar el pin:", str(e))
            return False
    return True
