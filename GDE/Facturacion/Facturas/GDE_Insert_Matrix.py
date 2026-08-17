import pandas as pd
import psycopg2
import datetime
import math


def vacio_a_none(valor):
    if pd.isna(valor) or valor == '':
        return None
    return valor

def connect_to_db_tsm():
    try:
        conn = psycopg2.connect(
            host="adempiere.tsm.cl",
            database="tsm",
            user="pg_api",
            password="8YR53mDRavJlfd6d",
            port=5432
        )
        print("Conexion exitosa a la BDD")
        return conn
    except psycopg2.Error as e:
        print(f"Conexion fallida, error: {e}")
        return None

dataframe = pd.read_excel('data_clientes_insert.xlsx')

for index, datos in dataframe.iterrows():
    ad_client_id = 1000000
    ad_org_id = datos['ad_org_id']
    created = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    createdby = 100
    updated = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    updatedby = 100
    isactive = 'Y'
    rut = vacio_a_none(datos.get('Rut'))
    rznsoc = vacio_a_none(datos.get('rznsoc'))
    detail = vacio_a_none(datos.get('detail'))
    number = vacio_a_none(datos.get('number'))
    approver = vacio_a_none(datos.get('approver_one'))
    tipo = vacio_a_none(datos.get('type'))
    c_charge_id = vacio_a_none(datos.get('c_charge_id'))
    m_product_id = vacio_a_none(datos.get('m_product_id'))
    c_currency_id = vacio_a_none(datos.get('c_currency_id'))
    c_paymentterm_id = vacio_a_none(datos.get('c_paymentterm_id'))
    salesrep_id = vacio_a_none(datos.get('salesrep_id'))
    c_bpartner_id = vacio_a_none(datos.get('c_bpartner_id'))
    approver2 = vacio_a_none(datos.get('approver_two'))
    user_id = vacio_a_none(datos.get('user_id_one')) 
    user2_id = vacio_a_none(datos.get('user_id_two'))
    
    with connect_to_db_tsm() as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                           INSERT INTO adempiere.facct_matrix(ad_client_id, ad_org_id, created, updatedby, updated, isactive, createdby, 
                           rut, rznsoc, detail, number, approver, tipo, c_charge_id,  m_product_id, c_currency_id, c_paymentterm_id, salesrep_id, c_bpartner_id, approver_two, user_id, user2_id)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);""",
                           (ad_client_id, ad_org_id, created, updatedby, updated, isactive, createdby, rut, rznsoc, detail, number, approver, tipo, c_charge_id, m_product_id, c_currency_id,
                            c_paymentterm_id, salesrep_id, c_bpartner_id, approver2, user_id, user2_id))