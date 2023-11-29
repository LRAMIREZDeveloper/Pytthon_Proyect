from conec import consume_api_updates, connect_to_db_tsm, isactive_partner, active_partner

# Inicializar la bandera de éxito en False
success = False

try:
    # Establecer conexión a la base de datos
    conn = connect_to_db_tsm()

    if conn:
        partner_desactive = isactive_partner(conn)
        partner_active = active_partner(conn)
        conn.close()
    else:
        raise Exception("No se pudo establecer conexión a la base de datos")

    # Inicializar la bandera de éxito en True si no hay excepciones
    success = True

    # Activar los pines de socios
    if partner_active:
        for pin in partner_active:
            data_active = {
                "isDisabled": False,
                "pin": pin
            }
            try:
                # Enviar solicitud a la API para activar el pin
                response_data_active = consume_api_updates(
                    "/person/add", data=data_active)
            except Exception as e:
                print("Error al enviar la solicitud a la API para activar el pin:", str(e))
                # Si ocurre un error, establecer la bandera a False y salir del bucle
                success = False
                break

    # Desactivar los pines de socios
    if partner_desactive:
        for partner in partner_desactive:
            data_desactive = {
                "isDisabled": True,
                "pin": partner
            }
            try:
                # Enviar solicitud a la API para desactivar el pin
                response_data_desactive = consume_api_updates(
                    "/person/add", data=data_desactive)
            except Exception as e:
                print("Error al enviar la solicitud a la API para desactivar el pin:", str(e))
                # Si ocurre un error, establecer la bandera a False y salir del bucle
                success = False

except Exception as e:
    print(f"Error al establecer conexión a la base de datos: {str(e)}")

# Mostrar mensaje de éxito solo si la bandera "success" es True
if success:
    print("Proceso completado exitosamente.")
