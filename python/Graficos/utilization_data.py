from graphic import connection_bdd, grafic_partner, grafic_asset
import matplotlib.pyplot as plt
import os

# Ruta base donde guardar los gráficos
OUTPUT_DIR = "C:/Users/lramirez/Github/Pytthon_Proyect/python/Graficos"

def guardar_grafico(figura, nombre_archivo):
    if figura is not None:
        ruta_completa = os.path.join(OUTPUT_DIR, nombre_archivo)
        figura.savefig(ruta_completa)
        plt.close(figura)
        print(f"Gráfico guardado en: {ruta_completa}")
    else:
        print("No se pudieron generar los datos para la figura.")

def main():
    data_partner, data_asset = connection_bdd()

    if data_partner is not None:
        figura_partner = grafic_partner(data_partner)
        guardar_grafico(figura_partner, "grafico_partner.png")
    else:
        print("No se pudieron cargar los datos de partner desde la base de datos.")

    if data_asset is not None:
        figura_asset = grafic_asset(data_asset)
        guardar_grafico(figura_asset, "grafico_asset.png")
    else:
        print("No se pudieron cargar los datos de asset desde la base de datos.")

if __name__ == '__main__':
    main()
