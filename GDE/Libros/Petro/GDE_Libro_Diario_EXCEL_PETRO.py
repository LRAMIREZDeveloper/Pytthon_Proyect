import psycopg2
import psycopg2.extras
from decimal import Decimal
from datetime import datetime
import pandas as pd
import openpyxl
import re

# elimina caracteres ilegales para Excel (control chars ASCII 0–31)
_illegal_chars = re.compile(r'[\x00-\x08\x0B\x0C\x0E-\x1F]')

DSN = dict(
    host="adempiere.petroamerica.cl",
    database="petro",
    user="adempiere",
    password="36jwhowHAoJFKO0z9wc8M4nPh2hPHIY1",
    port=5432
)

DATA = """
    SELECT 
        voucher,
        cod_cta, 
        tpo_comp, 
        nombre, 
        fecha, 
        descripcion, 
        debe, 
        haber, 
        origen
    FROM adempiere.bi_general_ledger
    WHERE fecha::date BETWEEN '2024-07-01' AND '2024-07-31'
"""

def normalize_number(v):
    if isinstance(v, Decimal):
        if v == v.to_integral_value():
            return int(v)
        return float(v)
    if isinstance(v, float):
        if v.is_integer():
            return int(v)
        return v
    return v  

def fmt_date(d):
    if d is None:
        return None
    if isinstance(d, datetime):
        return d.date()  # pandas will keep as date
    s = str(d)
    if " " in s:
        return s.split(" ")[0]
    return s

def fix_text(s):
    if s is None:
        return ""
    s = str(s)

    # reemplazos comunes de encoding
    s = s.replace("�", "ñ")

    # eliminar caracteres ilegales para openpyxl
    s = _illegal_chars.sub("", s)

    # limpiar saltos raros
    s = s.replace("\r", " ").replace("\n", " ").replace("\t", " ")

    return s.strip()

# Conexión y obtención de datos
conn = psycopg2.connect(**DSN)
conn.set_client_encoding('UTF8')
cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
cur.execute(DATA)
rows = cur.fetchall()
cur.close()
conn.close()

# Mapear filas a una lista de dicts con los campos exactos que quieres en el Excel
data = []
for r in rows:
    voucher = normalize_number(r.get('voucher'))
    cod_cta = fix_text(r.get('cod_cta'))
    nombre = fix_text(r.get('nombre'))
    fecha = fmt_date(r.get('fecha'))

    # AQUÍ ESTABA FALLANDO
    descripcion = fix_text(r.get('descripcion'))

    debe = normalize_number(r.get('debe'))
    haber = normalize_number(r.get('haber'))
    tpo_comp = fix_text(r.get('tpo_comp'))

    valor_apertura = 0.00
    num_comp = voucher if voucher is not None else ""
    rut_contrib = "76008989-3"
    moneda = "PESO-CL"
    periodo_tributario = "202510"

    data.append({
        "ValorApertura": valor_apertura,
        "TpoComp": tpo_comp,
        "NumComp": num_comp,
        "FechaContable": fecha,
        "GlosaAnalisis": descripcion,
        "CodigoCuenta": cod_cta,
        "Debe": debe if debe is not None else 0.0,
        "Haber": haber if haber is not None else 0.0,
        "RutContribuyente": rut_contrib,
        "Moneda": moneda,
        "Descr": nombre,
        "PeriodoTributario": periodo_tributario
    })

# Crear DataFrame
df = pd.DataFrame(data, columns=[
    "ValorApertura","TpoComp","NumComp","FechaContable","GlosaAnalisis",
    "CodigoCuenta","Debe","Haber","RutContribuyente","Moneda","Descr","PeriodoTributario"
])

# Asegurar tipos: Fecha como datetime, montos como float
df['FechaContable'] = pd.to_datetime(df['FechaContable'], errors='coerce').dt.date
df['Debe'] = pd.to_numeric(df['Debe'], errors='coerce').fillna(0.0)
df['Haber'] = pd.to_numeric(df['Haber'], errors='coerce').fillna(0.0)
df['ValorApertura'] = pd.to_numeric(df['ValorApertura'], errors='coerce').fillna(0.0)

# Escribir a Excel con formato (usa openpyxl)
output_xlsx = "LD_febrero_2025_petro.xlsx"

with pd.ExcelWriter(output_xlsx, engine='openpyxl') as writer:
    df.to_excel(writer, index=False, sheet_name='LibroDiario')

    # formatear columnas numéricas a 4 decimales
    workbook = writer.book
    worksheet = writer.sheets['LibroDiario']

    # aplicar formato de número con 4 decimales a las columnas 'Debe' y 'Haber' y 'ValorApertura'
    from openpyxl.styles import numbers

    # localizar índices (1-based en openpyxl, pandas escribe encabezado en fila 1)
    header = list(df.columns)
    # buscar posiciones
    def col_idx(name):
        return header.index(name) + 1

    fmt_4dec = '0.0000'
    for col_name in ('ValorApertura', 'Debe', 'Haber'):
        col_letter = openpyxl.utils.get_column_letter(col_idx(col_name))
        for row in range(2, 2 + len(df)):
            cell = worksheet[f"{col_letter}{row}"]
            cell.number_format = fmt_4dec

print("Excel generado:", output_xlsx)
