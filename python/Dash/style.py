from dash import dash_table
from dash import dash_table
from dash import dcc, html
import plotly.express as px


def style_detail_data():
    style_data = {
    'height': '40px',
    'background-color': '#2C3E50',
    'border-radius': '10px',
    'width': '15%',
    'top': '15%',
    'position': 'absolute',
    'border': '1px solid white',
    'font-family': 'Helvetica',
    'font-size': '30px',
    'margin': '0',
    'line-height': '40px',
    'text-align': 'center',
    'color': '#FFFFFF',
    }

    style_letter = {
    'color': '#FFFFFF', 
    'font-family': 'Helvetica', 
    'font-size': '30px', 
    'line-height': '40px', 
    'text-align': 'center'
    }
    
    return style_data, style_letter


def style_table(df):
    # Definir las tablas
    tabla_ot = dash_table.DataTable(
        id='tabla-datos',
        columns=[{'name': col, 'id': col} for col in df.columns],
        data=df.to_dict('records'),
        page_size=38,
        page_action='native',
        page_current=0,
        style_table={'maxHeight': '1120px', 'overflowY': 'auto', 'width': '98%', 'margin': '5px',
                    'textAlign': 'center', 'border': '1px solid #ddd', 'box-shadow': '2px 2px 2px lightgrey'},
        style_header={'backgroundColor': '#2C3E50', 'color': 'white', 'fontWeight': 'bold',
                    'position': 'sticky', 'top': 0},
        style_cell={'textAlign': 'left', 'font-family': 'Helvetica', 'font-size': 10},
        # Configuración para pintar las filas en base a la columna 'dias'
        style_data_conditional=[
            {
                'if': {'filter_query': '{dias} >= 10'},
                'backgroundColor': '#8B0000',
                'color': 'white'
            }
        ]
    )

    tabla_cantidad_taller = dash_table.DataTable(
        id='tabla-mecanicos',
        style_table={'maxHeight': '800px', 'overflowY': 'auto', 'width': '98%', 'margin': '5px',
                    'textAlign': 'center', 'border': '1px solid #ddd', 'box-shadow': '2px 2px 2px lightgrey'},
        style_header={'backgroundColor': '#2C3E50', 'color': 'white', 'fontWeight': 'bold',
                    'position': 'sticky', 'top': 0},
        style_cell={'textAlign': 'left', 'font-family': 'Helvetica', 'font-size': 11},
        style_data_conditional=[
            {
                'if': {'filter_query': '{Asignadas} >= 5'},
                'backgroundColor': '#8B0000',
                'color': 'white'
            }
        ]
    
    
    )
    
    return tabla_ot, tabla_cantidad_taller


def style_fromData(style_letter,tabla_ot,tabla_cantidad_taller,style_data,fleet_counts):
    data = html.Div(
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
    
    return data