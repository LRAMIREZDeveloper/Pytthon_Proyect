import psycopg2
import psycopg2.extras
from decimal import Decimal
from datetime import datetime, date, timedelta
import requests
import base64
import unicodedata

# =============================
# Configuración
# =============================

DSN = dict(
    host="adempiere.tsm.cl",
    database="tsm",
    user="pg_api",
    password="8YR53mDRavJlfd6d",
    port=5432
)

QUERY = """
    SELECT 
        voucher,
        cod_cta, 
        tpo_comp, 
        nombre, 
        fecha::date, 
        descripcion, 
        debe, 
        haber, 
        origen
    FROM bi.bi_general_ledger
    WHERE fecha::date BETWEEN %s AND %s
"""


# =============================
# Funciones utilitarias
# =============================

def get_periodo_tributario(fecha):
    if fecha is None:
        return ""
    if isinstance(fecha, datetime):
        return fecha.strftime("%Y%m")
    s = str(fecha)
    return s[:4] + s[5:7] if len(s) >= 7 else ""


def normalize_number(v):
    if isinstance(v, Decimal):
        return int(v) if v == v.to_integral_value() else float(v)
    if isinstance(v, float):
        return int(v) if v.is_integer() else v
    return v


def fmt_amount(v):
    if v is None:
        return "0.0000"
    try:
        return f"{float(normalize_number(v)):.4f}"
    except Exception:
        return "0.0000"


def fmt_date(d):
    if d is None:
        return ""
    if isinstance(d, datetime):
        return d.strftime("%Y-%m-%d")
    s = str(d)
    return s.split(" ")[0]


def fix_text(s):
    if s is None:
        return ""

    s = (
        str(s)
        .replace("\r", " ")
        .replace("\n", " ")
        .replace("\t", " ")
        .replace("�", "ñ")
        .replace("{->", " ")
        .replace(">", " ")
        .replace("<", " ")
        .strip()
    )

    # Quitar acentos
    highlighting = unicodedata.normalize("NFKD", s)
    return "".join(c for c in highlighting if not unicodedata.combining(c))

def norm(v):
    if isinstance(v, Decimal):
        try:
            return int(v)  # si es entero
        except Exception:
            return float(v)  # o str(v) si prefieres
    return v

def file_to_base64(path):
    """
    Lee un archivo y lo devuelve codificado en Base64 (string)
    """
    with open(path, "rb") as f:
        file_bytes = f.read()
    return base64.b64encode(file_bytes).decode("utf-8")

# =============================
# Acceso a datos
# =============================

def fetch_ledger_data(date_from, date_to):
    conn = psycopg2.connect(**DSN)
    conn.set_client_encoding('UTF8')
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cur.execute(QUERY, (date_from, date_to))
    rows = cur.fetchall()

    cur.close()
    conn.close()

    return rows


# =============================
# Generación de archivo
# =============================

def generate_file(rows, output_file):
    header = (
        "ValorApertura|TpoComp|NumComp|FechaContable|GlosaAnalisis|CodigoCuenta|"
        "Debe|Haber|RutContribuyente|Moneda|Descr|PeriodoTributario"
    )

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(header + "\n")

        for r in rows:
            line = "|".join([
                "0.00",                            
                str(r.get("tpo_comp") or ""),
                str(r.get("voucher") or ""),
                fmt_date(r.get("fecha")),
                fix_text(str(r.get("descripcion") or "")),
                str(r.get("cod_cta") or ""),
                fmt_amount(r.get("debe")),
                fmt_amount(r.get("haber")),
                "79705390-2",                  
                "PESO-CL",
                fix_text(r.get("nombre")),
                get_periodo_tributario(r.get("fecha"))
            ])

            f.write(line + "\n")


# =============================
# Post a la API
# =============================


def generate_book(ip, rut, auth_key, period, lce_content_base64):
    url = f"http://{ip}/api/Core.svc/core/SendDocumentLce"
    headers = {
        "AuthKey": auth_key,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    body = {
        "Environment": "P",
        "Rut": rut,
        "LceContent": lce_content_base64,
        "LceType": "LD",
        "Period": period
    }

    try:
        response = requests.post(url, headers=headers, json=body)
        print(f"🔄 Estado HTTP: {response.status_code}")

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error HTTP {response.status_code}")
            print("Respuesta:", response.text)
            return None

    except Exception as e:
        print("Excepción al hacer la solicitud:", str(e))
        return None

# =============================
# Main
# =============================

def main():
    ip_dtebox = "200.6.99.113"
    api_auth = "e94a9f68-79c1-4157-83ec-312951533703"
    rut = "79705390-2"

    # Fecha de hoy
    hoy = date.today()

    # Primer día del mes actual
    primer_dia_mes_actual = hoy.replace(day=1)

    # Último día del mes anterior
    ultimo_dia_mes_anterior = primer_dia_mes_actual - timedelta(days=1)

    # Primer día del mes anterior
    primer_dia_mes_anterior = ultimo_dia_mes_anterior.replace(day=1)

    # Convertir a string formato YYYY-MM-DD
    #today = ultimo_dia_mes_anterior.strftime("%Y-%m-%d")
    #yesterday = primer_dia_mes_anterior.strftime("%Y-%m-%d")

    today = '2025-12-31'
    yesterday = '2025-12-01'


    period = get_periodo_tributario(today)

    OUTPUT_FILE = f"LD_79705390-2_{period}_{period}_PESO-CL_0.txt"

    rows = fetch_ledger_data(yesterday, today)

    if not rows:
        print("No hay datos para generar el archivo")
        return

    # Generar archivo
    generate_file(rows, OUTPUT_FILE)
    print("Archivo generado:", OUTPUT_FILE)

    # Convertir archivo a Base64
    lce_base64 = file_to_base64(OUTPUT_FILE)

    # Enviar a la API 
    response = generate_book(ip_dtebox, rut, api_auth, period, lce_base64)
    print("Respuesta API:", response)

# =============================
# Entry point
# =============================

if __name__ == "__main__":
    main()