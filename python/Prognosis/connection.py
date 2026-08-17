import psycopg2


def connect_to_db_tsm_nuevo():
    try:
        conn = psycopg2.connect(
            host="adempiere.tsm.cl",
            database="tsm",
            user="pg_api",
            password="8YR53mDRavJlfd6d",
            port=5432
        )
        return conn
    except psycopg2.Error as e:
        print("Conexion fallida, error: ", e)
        return None

def obtener_ciclos_mantencion(patente):
    query = f"""
    SELECT
        m.description AS descripcion_mantencion,
        m.interval AS intervalo,
        md.lastmp AS ultima_mantencion,
        ot.mp_maintain_id AS mantencion_ot,
        ot.documentno AS documento,
        ot.created AS fecha
    FROM adempiere.mp_maintain m
    JOIN adempiere.mp_maintaindetail md ON md.mp_maintain_id = m.mp_maintain_id
    JOIN adempiere.a_asset a ON a.a_asset_id = md.a_asset_id
    LEFT JOIN (
        SELECT ot1.a_asset_id, ot1.mp_maintain_id, ot1.documentno, ot1.created
        FROM adempiere.mp_ot ot1
        WHERE ot1.C_DocType_ID = 1000081
        AND ot1.documentno = (
            SELECT MAX(ot2.documentno)
            FROM adempiere.mp_ot ot2
            WHERE ot2.a_asset_id = ot1.a_asset_id
                AND ot2.mp_maintain_id = ot1.mp_maintain_id
                AND ot2.C_DocType_ID = 1000081
        )
    ) ot ON ot.a_asset_id = a.a_asset_id AND ot.mp_maintain_id = m.mp_maintain_id
    WHERE m.isactive = 'Y'
    AND a.value = '{patente}'
    AND m.interval > 0
    ORDER BY ot.created DESC;
    """
    conn = connect_to_db_tsm_nuevo()
    if conn is None:
        return []

    try:
        with conn.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            result = [dict(zip(columns, row)) for row in rows]
            return result
    except psycopg2.Error as e:
        print("Error ejecutando la consulta: ", e)
        return []
    finally:
        conn.close()

def generar_mantenciones(ciclos_mantencion, km_limite):
    resultados = []

    for ciclo in sorted(ciclos_mantencion, reverse=True):
        multiplo = ciclo
        while multiplo <= km_limite:
            resultados.append({'mantencion correspondiente': ciclo, 'km': multiplo})
            multiplo += ciclo

    resultado_final = []
    km_vistos = set()

    for resultado in resultados:
        km = resultado['km']
        mantencion = resultado['mantencion correspondiente']
        if km not in km_vistos:
            km_vistos.add(km)
            resultado_final.append(resultado)
        else:
            for i, existing_result in enumerate(resultado_final):
                if existing_result['km'] == km:
                    if mantencion > existing_result['mantencion correspondiente']:
                        resultado_final[i] = resultado
                    break

    resultado_final = sorted(resultado_final, key=lambda x: x['km'])

    return resultado_final


def ajustar_mantenciones(mantenciones_generadas, km_ultima_mantencion):
    mantenciones_ajustadas = {}
    diferencia_km = None

    if km_ultima_mantencion is not None:
        mantencion_mas_cercana = min(mantenciones_generadas, key=lambda x: abs(x['km'] - km_ultima_mantencion))
        diferencia_km = km_ultima_mantencion - mantencion_mas_cercana['km']

        for resultado in mantenciones_generadas:
            if resultado['km'] > mantencion_mas_cercana['km']:
                ciclo = resultado['mantencion correspondiente']         
                resultado_ajustado = {
                    'mantencion correspondiente': ciclo,
                    'km': resultado['km'] + diferencia_km
                }
                if ciclo not in mantenciones_ajustadas or resultado_ajustado['km'] < mantenciones_ajustadas[ciclo]['km']:
                    mantenciones_ajustadas[ciclo] = resultado_ajustado

    return diferencia_km, mantenciones_ajustadas

def seach_date(datos):
    ultima_fecha_no_vacia = None
    km_ultima_mantencion = None

    for dato in datos:
        fecha = dato.get('fecha')
        if fecha and (ultima_fecha_no_vacia is None or fecha > ultima_fecha_no_vacia):
            ultima_fecha_no_vacia = fecha
            km_ultima_mantencion = dato['ultima_mantencion']

    return km_ultima_mantencion