import psycopg2
import psycopg2.extras
from decimal import Decimal
from datetime import datetime, date, timedelta


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

OUTPUT_FILE = "libro_diario.txt"


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
    return "" if s is None else str(s).replace("�", "ñ")


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

    with open(output_file, "w", encoding="utf-8-sig") as f:
        f.write(header + "\n")

        for r in rows:
            line = "|".join([
                "0.00",                            
                str(r.get("tpo_comp") or ""),
                str(r.get("voucher") or ""),
                fmt_date(r.get("fecha")),
                str(r.get("descripcion") or ""),
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
# Main
# =============================

def main():
    today = date.today()
    yesterday = today - timedelta(days=10)

    rows = fetch_ledger_data(yesterday, yesterday)

    if not rows:
        print("No hay datos para generar el archivo")
        return

    generate_file(rows, OUTPUT_FILE)
    print("Archivo generado:", OUTPUT_FILE)


# =============================
# Entry point
# =============================

if __name__ == "__main__":
    main()
