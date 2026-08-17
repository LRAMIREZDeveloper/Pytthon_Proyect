import psycopg2

# =============================
# Configuración conexión
# =============================
DB_CONFIG = {
    "host": "adempiere.petroamerica.cl",
    "database": "petro",
    "user": "api",
    "password": "8YR53mDRavJlfd6d",
    "port": 5432
}

try:
    print("Intentando conectar a PostgreSQL...")

    conn = psycopg2.connect(**DB_CONFIG)

    print("✅ Conexión exitosa a la base de datos.")

    conn.close()
    print("🔒 Conexión cerrada correctamente.")

except Exception as e:
    print("❌ Error al conectar:")
    print(e)