import dash
from dash import dash_table
from dash import dcc, html
from dash.dependencies import Input, Output
from dash_bootstrap_components import themes
import plotly.express as px

from bdd import connection_bdd, data_for_chart,data_for_mechanic_table,data_for_table, update_data
from style import style_detail_data, style_table

# Procesar datos
df = connection_bdd()
fleet_counts = data_for_chart(df)
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
app.layout = html.Div(
    children=[
        # Div Cabecera
        html.Div([
            
            # Logo
            html.Div([
                html.Img(src='https://tsm.cl/wp-content/uploads/2022/03/logoTSM2021-06.png', style={'height': '50px'}),
            ], style={'position': 'absolute', 'top': 0, 'left': 0}),

            # Título
            html.Div([
                html.H1('Mantenimiento (OT)', style={'color': 'white', 'line-height': '60px', 'font-family': 'Helvetica', 'padding': '2%'}),
            ],style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'left', 'height': '60px', 'width': '60%', 'position': 'absolute', 'left': '10%'}),

            # Total de registros
            html.Div([
                html.P(id='total_registros', style={**style_letter}),
            ],style={**style_data, 'right': '35%'}),

            # Total de registros en estado Procesado
            html.Div([
                html.P(id='total_registros_procesado',style={**style_letter})
            ],style={**style_data,'right': '18%'}),

            # Total de registros en estado Borrador
            html.Div([
                html.P(id='total_registros_borrador',style={**style_letter})
            ],style = {**style_data,'right': '1%'}),
        
        ],style={'background-color': '#2C3E50', 'height': '60px', 'width': '100%', 'position': 'relative'}),

        # Division Datos
        html.Div([
            
            # Tabla OT 
            html.Div([
                html.H3('OT Abiertas', style={'textAlign': 'center', 'font-family': 'Helvetica', 'font-size': 20}),
                tabla_ot,
                dcc.Loading(id="loading-icon-ot", children=[dash_table.DataTable()])
            ],style={'border-radius': '5px', 'box-shadow': '2px 2px 2px lightgrey', 'width': '60%', 'display': 'inline-block', 'backgroundColor': '#FFFFFF', 'margin': '5px'}),
            
            # Division para el gráfico y la otra tabla mecanicos.
            html.Div([
                
                # Tabla Mecanicos
                html.Div([
                    html.H3('Registros por Mecánico', style={'textAlign': 'center', 'font-family': 'Helvetica', 'font-size': 20}),
                    tabla_cantidad_taller,
                ],style= {'border-radius': '5px', 'box-shadow': '2px 2px 2px lightgrey', 'width': '100%', 'display': 'inline-block', 'backgroundColor': '#FFFFFF', 'margin': '5px'}),
                
                # Grafico Flotas
                html.Div([
                    dcc.Graph(
                        id='grafico-ejemplo',
                        figure=px.line(fleet_counts,
                                        x='flota',
                                        y='count',  # La altura de las barras es el conteo de filas por valor en 'fleet'
                                        title='Patentes por Flota',
                                        labels={'count': 'Cantidad', 'flota': 'Flota'},
                                    ),
                    ),
                ],style={'width': '100%', 'border-radius': '5px', 'box-shadow': '2px 2px 2px lightgrey', 'margin': '5px'}),
            
            ],style={'width': '40%', 'display': 'inline-block',}),
        
        ],style={'display': 'flex','width': '99%'}),
        
        # Pie de pagina
        html.Footer([
            html.H2('®2023 Transporte Santa Maria SpA.', style={'color': 'white', 'textAlign': 'center', 'line-height': '20px', 'font-family': 'Helvetica','font-size': 14}),
            html.H3('Todos los derechos reservados.', style={'color': 'white', 'textAlign': 'center', 'font-family': 'Helvetica','font-size': 12,'top': 0}),
        ],style={ 'box-shadow': '2px 2px 2px lightgrey','display': 'inline-block','background-color': '#2C3E50','width': '100%', 'position': 'center'}),
              
        # Intervalo de actualizacion  
        dcc.Interval(
            id='interval-component',
            interval= 10 * 1000,  # en milisegundos
            n_intervals=0
        ),
    ],style={'backgroundColor': '#EDEDED','width': '100%'}  # Establecer el color de fondo de la página completa
)

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