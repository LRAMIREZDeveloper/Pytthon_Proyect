import mysql.connector
from mysql.connector import Error

# Configuración de la base de datos
DB_CONFIG = {
    "host": "45.169.100.114",
    "user": "tsmcl1_api_tsm",
    "password": "8@)@28uSl@^MHMPW",
    "database": "tsmcl1_certifications_tsm"
}

try:
    # Intentar conexión
    conn = mysql.connector.connect(**DB_CONFIG)
    
    if conn.is_connected():
        print("Conexión exitosa a la base de datos MySQL\n")
        
        # Crear cursor
        cursor = conn.cursor()

        # Escribir tu consulta SQL
        query = "SELECT * FROM certifications_asset LIMIT 10;"  # 👈 cambia el nombre de la tabla

        # Ejecutar la consulta
        cursor.execute(query)

        # Obtener todos los registros
        rows = cursor.fetchall()

        # Verificar si hay datos
        if rows:
            print("📋 Resultados:")
            for row in rows:
                print(row)
        else:
            print("⚠️ No se encontraron registros en la tabla.")
        
except Error as e:
    print(f"❌ Error al conectar o ejecutar consulta: {e}")

finally:
    # Cerrar conexión
    if 'conn' in locals() and conn.is_connected():
        cursor.close()
        conn.close()
        print("\n🔒 Conexión cerrada.")
