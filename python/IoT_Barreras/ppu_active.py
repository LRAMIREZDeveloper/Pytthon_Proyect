from conec import consume_api_updates, connect_to_db_tsm, isactive_ppu, active_ppu

try:
    # Establecer conexión a la base de datos
    conn = connect_to_db_tsm()

    if conn:
        ppu_desactive = isactive_ppu(conn)
        ppu_active = active_ppu(conn)
        conn.close()
    else:
        raise Exception("No se pudo establecer conexión a la base de datos")

    success = True

    if ppu_desactive:
        for ppu in ppu_desactive:
            data_desactive = {
                "accLevelIds": "4028948787dde47d0187dde53c950436",
                "pin": ppu
            }
            response_data = consume_api_updates("/person/add", data=data_desactive)
            if not response_data:
                print("Fallo en la solicitud a la API para desactivar el pin")
                success = False

    if ppu_active:
        for pin in ppu_active:
            data = {
                "accLevelIds": "4028948787dde47d0187dde53c950436",
                "pin": pin
            }
            response_data = consume_api_updates("/person/add", data=data)
            if not response_data:
                print("Fallo en la solicitud a la API para activar el pin")
                success = False

    if not ppu_active:
        print("No se obtuvieron pines activos desde la base de datos")
        success = False

except Exception as e:
    print(f"Error: {str(e)}")
    success = False

if success:
    print("Proceso completado con éxito.")
