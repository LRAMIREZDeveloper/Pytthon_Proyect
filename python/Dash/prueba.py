import dash
from dash.dependencies import Input, Output
from dash_bootstrap_components import themes

from bdd import connection_bdd, data_fleet,data_for_mechanic_table,data_for_table, update_data
from style import style_detail_data, style_table, style_fromData

# Procesar datos
df = connection_bdd()
fleet_counts = data_fleet(df)
tabla_mecanicos_data = data_for_mechanic_table(df)
tabla_data = data_for_table(df)

# Estilo definido de los datos.
style_data, _ = style_detail_data()
_, style_letter = style_detail_data()

# Estilo definido de las tablas.
tabla_ot,_ = style_table(df)
_, tabla_cantidad_taller =  style_table(df)

# Inicializar la aplicación Dash con estilo de Bootstrap
app = dash.Dash(__name__, external_stylesheets=[themes.BOOTSTRAP])

# Diseño del tablero
app.layout = style_fromData(style_letter,tabla_ot,tabla_cantidad_taller,style_data,fleet_counts)

# Lógica de actualización en tiempo real
@app.callback(
    [Output('grafico-ejemplo', 'figure'),
     Output('tabla-datos', 'data'),
     Output('tabla-mecanicos', 'data'),
     Output('total_registros', 'children'),
     Output('total_registros_procesado', 'children'),
     Output('total_registros_borrador', 'children')],
    Input('interval-component', 'n_intervals')
)

def update_callback(n):
    return update_data(n)

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run_server(debug=True)