from dash import dash_table


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
        page_size=30,
        page_action='native',
        page_current=0,
        style_table={'maxHeight': '1000px', 'overflowY': 'auto', 'width': '98%', 'margin': '5px',
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