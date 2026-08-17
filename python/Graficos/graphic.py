import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
import numpy as np
from scipy.stats import linregress
import locale 
locale.setlocale(locale.LC_TIME, 'es_ES')

def connection_bdd():
    engine = create_engine('postgresql://pg_api:8YR53mDRavJlfd6d@adempiere.tsm.cl:5432/tsm')
    query_partner = """
        SELECT * FROM bi.quantity_utilization_bpartner
            """
    query_asset = """
        SELECT * FROM bi.quantity_utilization_asset"""
    df = pd.read_sql(query_partner, engine)
    dfa = pd.read_sql(query_asset, engine)
    return df, dfa

# Función para generar el gráfico lineal con línea de tendencia y etiquetas de datos
def grafic_partner(df):
    try:
        # Verificar que la columna 'datetrx' está en el DataFrame y convertirla a datetime si no lo está
        if 'datetrx' not in df.columns:
            raise ValueError("La columna 'datetrx' no está presente en el DataFrame")
        if not pd.api.types.is_datetime64_any_dtype(df['datetrx']):
            df['datetrx'] = pd.to_datetime(df['datetrx'])
        
        # Filtrar los datos para incluir solo los últimos 30 días
        end_date = pd.Timestamp.now()
        start_date = end_date - pd.Timedelta(days=30)
        last_30_days_df = df[(df['datetrx'] >= start_date) & (df['datetrx'] <= end_date)]
        
        # Verificar si el DataFrame filtrado está vacío
        if last_30_days_df.empty:
            raise ValueError("No hay datos para los últimos 30 días")
        
        # Agrupar los datos por fecha y contar la cantidad de líneas para cada fecha
        counts_by_date = last_30_days_df.groupby(last_30_days_df['datetrx'].dt.date).size()
        
        # Verificar si la agrupación resultó en un DataFrame vacío
        if counts_by_date.empty:
            raise ValueError("No se encontraron datos agrupados por fecha")
        
        # Calcular la línea de tendencia
        x = np.arange(len(counts_by_date.index))
        y = counts_by_date.values
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)
        
        # Establecer rango de fechas para los marcadores del eje x
        min_date = min(counts_by_date.index)
        max_date = max(counts_by_date.index)
        date_range = pd.date_range(start=min_date, end=max_date)
        
        # Formatear las fechas al formato deseado (día-mes)
        formatted_dates = [date.strftime('%d-%b') for date in date_range]
        
        # Estilo del gráfico
        plt.style.use('ggplot')
        
        # Graficar los datos y la línea de tendencia
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(counts_by_date.index, counts_by_date.values, marker='o', linestyle='-', label='Conductores')
        ax.plot(counts_by_date.index, p(x), linestyle='--', color='red', label='Línea de tendencia')
        
        # Agregar etiquetas de datos
        for i, value in enumerate(y):
            ax.text(counts_by_date.index[i], value, str(value), ha='center', va='bottom', fontsize=10)
        
        # ax.set_title('Conductores sin Movimiento')
        ax.set_ylabel('Cantidad de Conductores')
        ax.set_xticks(date_range)
        ax.set_xticklabels(formatted_dates, rotation=90, fontsize=10)
        ax.tick_params(axis='y', labelsize=10)
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.legend(fontsize=10)
        plt.tight_layout()
        
        return fig
    except Exception as e:
        print("Error al generar el gráfico lineal con línea de tendencia y etiquetas de datos:", e)
        return None


def grafic_asset(dfa):
    locale.setlocale(locale.LC_TIME, 'es_ES')

    # Convertir la columna de fecha a tipo datetime si no está en ese formato
    dfa['datetrx'] = pd.to_datetime(dfa['datetrx'])

    # Seleccionar solo los últimos 30 días
    ultimos_30_dias = dfa[dfa['datetrx'] >= dfa['datetrx'].max() - pd.Timedelta(days=29)]

    # Agrupar por fecha y contar el número de ocurrencias de cada tipo de flota
    recuento_flota_por_fecha = ultimos_30_dias.groupby(ultimos_30_dias['datetrx'].dt.date).size()

    # Convertir el índice a un objeto DatetimeIndex
    recuento_flota_por_fecha.index = pd.to_datetime(recuento_flota_por_fecha.index)
    
    # Estilo del gráfico
    plt.style.use('ggplot')
    plt.figure(figsize=(12, 6))
    plt.plot(recuento_flota_por_fecha.index, recuento_flota_por_fecha.values, marker='o', linestyle='-', label='Activos', linewidth=2)

    # Agregar etiquetas de datos
    for i, txt in enumerate(recuento_flota_por_fecha.values):
        plt.annotate(txt, (recuento_flota_por_fecha.index[i], recuento_flota_por_fecha.values[i]))
        
    # Calcular la línea de tendencia usando regresión lineal
    x_values = range(len(recuento_flota_por_fecha))
    slope, intercept, _, _, _ = linregress(x_values, recuento_flota_por_fecha.values)
    trendline = [slope * x + intercept for x in x_values]
    
    plt.plot(recuento_flota_por_fecha.index, trendline, color='red', linestyle='--', label='Línea de Tendencia')

    #plt.title('Recuento Total de Flota por Día (Últimos 30 días)')
    plt.ylabel('Cantidad de equipos')

    # Obtener las abreviaturas de los meses para las fechas de los últimos 30 días
    abreviaturas_fechas = recuento_flota_por_fecha.index.strftime('%d-%b').str.upper()

    # Mostrar todas las fechas en el eje x con abreviaturas de meses escritas en español
    plt.xticks(recuento_flota_por_fecha.index, abreviaturas_fechas, rotation=90)

    # Mostrar el gráfico
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    return plt.gcf()