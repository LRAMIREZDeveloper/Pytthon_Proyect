import pyodbc
from connection import connection_sqlserver

connection_string = connection_sqlserver()

# Conectar a la base de datos
try:
    connection = pyodbc.connect(connection_string)
    print("Conexión exitosa")
except Exception as e:
    print("Error al conectar a la base de datos:", e)

# Aquí puedes realizar tus consultas
try:
    query = """
    SELECT * FROM softland.sw_personal 
        WHERE nombres LIKE '%ROJAS%'
    ORDER BY nombres DESC
    """
    with connection.cursor() as cursor:  # Obtener un cursor
        cursor.execute(query)
        rows = cursor.fetchall()
        for row in rows:
            print(row)
except Exception as e:
    print("Error al realizar la consulta:", e)
finally:
    connection.close()
