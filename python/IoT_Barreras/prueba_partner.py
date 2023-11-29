from conec import connect_to_db_tsm, isactive_partner, active_partner, activate_pins_partner, deactivate_pins_partner

def main():
    success = True

    try:
        conn = connect_to_db_tsm()

        if conn:
            partner_desactive = isactive_partner(conn)
            partner_active = active_partner(conn)
            conn.close()
        else:
            print("No se pudo establecer conexión a la base de datos")
            success = False

        if partner_active:
            if not activate_pins_partner(partner_active):
                success = False
        else:
            print("No se obtuvieron pines activos desde la base de datos, 1")
            success = False

        if partner_desactive:
            if not deactivate_pins_partner(partner_desactive):
                success = False
        else:
            print("No se obtuvieron pines activos desde la base de datos, 2")
            success = False

    except Exception as e:
        print(f"Error al establecer conexión a la base de datos: {str(e)}")
        success = False

    if success:
        print("Proceso completado exitosamente.")

if __name__ == "__main__":
    main()
