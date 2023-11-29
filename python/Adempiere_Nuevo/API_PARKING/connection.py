import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import psycopg2
import datetime

# Desactivar advertencias de verificación de certificado SSL
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def connect_to_db_tsm_nuevo():
    try:
        conn = psycopg2.connect(
            host="tsm.prolinux.cl",
            database="adempiere",
            user="adempiere",
            password="quL2CDAY5kdh",
            port=5432
        )
        print("Connected to the database")
        return conn
    except psycopg2.Error as e:
        print("Failed to connect to the database", e)
        return None


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


def active_ppu(conn):
    cur = conn.cursor()
    try:
        query = """
        SELECT ppu_ping
            FROM api.i_parking_ppu
        WHERE ppu_ping = 'HHBG86'
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


def active_partner(conn):
    cur = conn.cursor()
    try:
        query = """
        SELECT ppu_ping
            FROM api.i_parking_ppu
        WHERE ppu_ping = 'HHBG86'
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


def isactive_partner(conn):
    cur = conn.cursor()
    try:
        query = """
        SELECT rut_ping FROM api.i_parking_partner
        WHERE rut_ping = '18365540K'
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


def update_ppu_data(cur, conn, pin, full_name, accLevelIds, dptname, bdd_ppu, ppu_name, ppu_acclevelids, ppu_dptname):
    if full_name != ppu_name or accLevelIds != ppu_acclevelids or dptname != ppu_dptname:
        query_update_ppu = "UPDATE api.ti_parking_ppu SET pin_ppu = %s, name = %s, acclevelids = %s, dptname = %s WHERE pin_ppu = %s"
        cur.execute(query_update_ppu, (pin, full_name,
                    accLevelIds, dptname, bdd_ppu))
        conn.commit()


def update_user_data(cur, conn, pin, full_name, accLevelIds, dptname, bdd_user, user_name, user_acclevelids, user_dptname):
    if full_name != user_name or accLevelIds != user_acclevelids or dptname != user_dptname:
        query_update_user = "UPDATE api.ti_parking_partner SET pin_partner = %s, name = %s, acclevelids = %s, dptname = %s WHERE pin_partner = %s"
        cur.execute(query_update_user, (pin, full_name,
                    accLevelIds, dptname, bdd_user))
        conn.commit()


def insert_data(cur, conn, pin, name, lastname, accLevelIds, created, dptname):
    fullname = f"{name} {lastname}"
    if len(pin) == 6 or len(pin) == 5:
        insert_query = "INSERT INTO api.ti_parking_ppu (pin_ppu, name, accLevelIds, created, dptname) VALUES (%s, %s, %s, %s, %s)"
        # Es una patente de auto o moto
        values = (pin, fullname, accLevelIds, created, dptname)
    else:
        # Es un RUT de persona
        rut_adempiere = pin[:-1]  # Obtener PIN sin el último dígito
        values = (pin, rut_adempiere, fullname, accLevelIds, created, dptname)
        insert_query = "INSERT INTO api.ti_parking_partner (pin_partner, partner_adempiere, name, accLevelIds, created, dptname) VALUES (%s, %s, %s, %s, %s, %s)"
    cur.execute(insert_query, values)
    conn.commit()


def get_counts_for_pin(cur, pin):
    query_user_count = "SELECT COUNT(*) FROM api.ti_parking_partner WHERE pin_partner = %s"
    cur.execute(query_user_count, (pin,))
    count_user = cur.fetchone()[0]

    query_ppu_count = "SELECT COUNT(*) FROM api.ti_parking_ppu WHERE pin_ppu = %s"
    cur.execute(query_ppu_count, (pin,))
    count_ppu = cur.fetchone()[0]

    return count_user, count_ppu


def process_ppu_data(cur, conn, pin, full_name, accLevelIds, dptname):
    query_ppu = "SELECT pin_ppu, name, acclevelids, dptname FROM api.ti_parking_ppu WHERE pin_ppu = %s"
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


def process_user_data(cur, conn, pin, full_name, accLevelIds, dptname):
    query_user = "SELECT pin_partner, name, acclevelids, dptname FROM api.ti_parking_partner WHERE pin_partner = %s"
    cur.execute(query_user, (pin,))
    result_user = cur.fetchone()
    if result_user is not None:
        bdd_user = result_user[0]
        user_name = result_user[1]
        user_acclevelids = result_user[2]
        user_dptname = result_user[3]
        update_user_data(cur, conn, pin, full_name, accLevelIds, dptname,
                         bdd_user, user_name, user_acclevelids, user_dptname)


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
                process_ppu_data(cur, conn, pin, full_name,
                                 accLevelIds, dptname)
            else:
                process_user_data(cur, conn, pin, full_name,
                                  accLevelIds, dptname)
