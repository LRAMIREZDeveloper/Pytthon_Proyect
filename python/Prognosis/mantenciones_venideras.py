def generar_mantenciones(ciclos_mantencion, km_limite):
    resultados = []

    # Recorrer los ciclos de mantenimiento de mayor a menor
    for ciclo in sorted(ciclos_mantencion, reverse=True):
        multiplo = ciclo
        while multiplo <= km_limite:
            resultados.append({'mantencion correspondiente': ciclo, 'km': multiplo})
            multiplo += ciclo

    # Eliminar duplicados basados en 'km', priorizando 'mantencion correspondiente' más alta
    resultado_final = []
    km_vistos = set()

    for resultado in resultados:
        km = resultado['km']
        mantencion = resultado['mantencion correspondiente']
        if km not in km_vistos:
            km_vistos.add(km)
            resultado_final.append(resultado)
        else:
            # Reemplazar el existente si la mantencion es más alta
            for i, existing_result in enumerate(resultado_final):
                if existing_result['km'] == km:
                    if mantencion > existing_result['mantencion correspondiente']:
                        resultado_final[i] = resultado
                    break

    # Ordenar los resultados finales por 'km' de menor a mayor
    resultado_final = sorted(resultado_final, key=lambda x: x['km'])

    return resultado_final

# Datos proporcionados
km_ultima_mantencion = 865915
ciclos_mantencion = [30000, 120000]
km_limite = 3000000  # Puedes ajustar este límite según sea necesario

# Generar las mantenciones hasta el límite especificado
mantenciones_generadas = generar_mantenciones(ciclos_mantencion, km_limite)

# Encontrar la mantención más cercana al km_ultima_mantencion
mantencion_mas_cercana = min(mantenciones_generadas, key=lambda x: abs(x['km'] - km_ultima_mantencion))

# Calcular la diferencia en km
diferencia_km = km_ultima_mantencion - mantencion_mas_cercana['km']

# Ajustar las mantenciones futuras
mantenciones_ajustadas = []
for resultado in mantenciones_generadas:
    if resultado['km'] > mantencion_mas_cercana['km']:
        resultado_ajustado = {
            'mantencion correspondiente': resultado['mantencion correspondiente'],
            'km': resultado['km'] + diferencia_km
        }
        mantenciones_ajustadas.append(resultado_ajustado)

# Imprimir resultados
print(f"La mantención más cercana al kilometraje {km_ultima_mantencion} es a los {mantencion_mas_cercana['km']} km con una mantención correspondiente de {mantencion_mas_cercana['mantencion correspondiente']} km.")
print(f"La diferencia en km es de {diferencia_km} km.")

if mantenciones_ajustadas:
    print("Las próximas mantenciones ajustadas son:")
    for mantencion in mantenciones_ajustadas:
        print(f"A los {mantencion['km']} km con una mantención correspondiente de {mantencion['mantencion correspondiente']} km.")
else:
    print("No se encontraron próximas mantenciones dentro de los límites especificados.")
