
from connection import generar_mantenciones,obtener_ciclos_mantencion, ajustar_mantenciones,seach_date

def main():
    km_limite = 3000000
    patente = 'PSVR54'

    # Obtener ciclos de mantención desde la base de datos
    data_mantencion = obtener_ciclos_mantencion(patente)
    ciclos_mantencion = [item['intervalo'] for item in data_mantencion]

    # Encontrar el kilometraje correspondiente
    km_ultima_mantencion = seach_date(data_mantencion)
    
    # Generar las mantenciones hasta el límite especificado
    mantenciones_generadas = generar_mantenciones(ciclos_mantencion, km_limite)
    _, mantenciones_ajustadas = ajustar_mantenciones(mantenciones_generadas, km_ultima_mantencion)
    
    
    if mantenciones_ajustadas:
        print("Las próximas mantenciones ajustadas son:")
        for ciclo in sorted(mantenciones_ajustadas):
            mantencion = mantenciones_ajustadas[ciclo]
            print(f"A los {mantencion['km']} km con una mantención correspondiente de {mantencion['mantencion correspondiente']} km.")
    else:
        print("No se encontraron próximas mantenciones dentro de los límites especificados.")


if __name__ == "__main__":
    main()