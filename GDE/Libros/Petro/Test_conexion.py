import psycopg2

# =============================
# Configuración
# =============================

DSN = dict(
    host="adempiere.petroamerica.cl",
    database="petro",
    user="adempiere",
    password="36jwhowHAoJFKO0z9wc8M4nPh2hPHIY1",
    port=5432
)

def probar_conexion():
    conn = None
    try:
        # Intentar conexión
        conn = psycopg2.connect(**DSN)
        print("✅ Conexión exitosa a la base de datos")

        # Probar una consulta simple
        cur = conn.cursor()
        cur.execute("SELECT 1;")
        resultado = cur.fetchone()
        print("Resultado de prueba:", resultado)

        cur.close()

    except Exception as e:
        print("❌ Error al conectar:", e)

    finally:
        if conn:
            conn.close()
            print("🔒 Conexión cerrada")

if __name__ == "__main__":
    probar_conexion()
