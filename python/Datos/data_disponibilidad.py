import psycopg2
import pandas as pd

conn = psycopg2.connect(
    host="adempiere.tsm.cl",
    database="tsm",
    user="pg_api",
    password="8YR53mDRavJlfd6d",
    port=5432
)

query = """
SELECT d.fleet AS flota, 
       d.documento AS documento, 
       d.value AS rut, 
       d.name AS nombre, 
       d.date AS fecha, 
       d.acronym AS sigla,
       arl.description AS detalle_sigla,
       d.t AS HDR
FROM api.api_cbpartner_availability d
  LEFT JOIN adempiere.AD_Ref_List arl ON arl.value = d.acronym AND arl.AD_Reference_ID = 1000171
  WHERE d.date::date BETWEEN '2024-06-01' AND now()::date - 5
  AND d.t = 0
  AND d.acronym = ANY (ARRAY['PA', 'T1', 'T2', 'T3', 'TI', 'TL', 'TN', 'TS'])
  ORDER BY d.date DESC
"""

# Ejecutar la consulta y obtener los datos en un DataFrame de pandas
with conn:
    with conn.cursor() as cursor:
        cursor.execute(query)
        datos = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(datos, columns=columns)

# Exportar los datos a un archivo Excel
df.to_excel("resultado.xlsx", index=False)

print("Datos exportados a resultado.xlsx")
