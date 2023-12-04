import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px

def connection_bdd():
    # Conectar a la base de datos PostgreSQL usando SQLAlchemy
    engine = create_engine('postgresql://api:Api2022@192.168.1.29:5432/tsm')

    # Cargar datos desde la base de datos
    query_ot = """ 
    SELECT
        now()::date - ot.datetrx AS Dias,
        ot.documentno AS Documento,
        cb.name AS Mecanico,
        a.value AS Patente,
        ot.description AS Description,
            ltrim(d.name::text, 'Orden de Trabajo'::text)::character varying(60) AS Tipo_OT,
            ot.datetrx AS Fecha,
            CASE
                WHEN ot.docstatus::text = 'CO'::text THEN 'Completo'::text
                WHEN ot.docstatus::text = 'DR'::text THEN 'Borrador'::text
                WHEN ot.docstatus::text = 'PR'::text THEN 'En proceso'::text
                ELSE 'Anulado'::text
            END AS Estado,
            f.name AS Flota,
            ( SELECT rl.name
            FROM adempiere.ad_ref_list rl
            WHERE rl.value::text = org.base::text AND rl.ad_reference_id = 1000197::numeric) AS Ubicacion
    FROM adempiere.mp_ot ot
        JOIN adempiere.c_doctype d ON d.c_doctype_id = ot.c_doctype_id
        JOIN adempiere.a_asset a ON a.a_asset_id = ot.a_asset_id
        LEFT JOIN adempiere.ad_org og ON og.ad_org_id = a.ad_orgref_id
        LEFT JOIN adempiere.c_projectofb f ON f.c_projectofb_id = og.c_projectofb_id
        LEFT JOIN adempiere.ad_org org ON org.ad_org_id = ot.ad_org_id
        LEFT JOIN adempiere.mp_ot_typejobs tj ON tj.mp_ot_typejobs_id = ot.mp_ot_typejobs_id
        LEFT JOIN adempiere.c_bpartner cb ON ot.c_bpartner_id = cb.c_bpartner_id
        LEFT JOIN adempiere.c_bpartner cbp ON ot.c_bpartner_id2 = cbp.c_bpartner_id
    WHERE ot.ad_client_id = 1000000::numeric AND ot.datetrx >= '2020-12-01'::date AND (ot.docstatus::text <> ALL (ARRAY['CO'::character varying::text, 'CL'::character varying::text, 'VO'::character varying::text, 'AN'::character varying::text])) AND ot.c_doctype_id <> 1000107::numeric
    ORDER BY Dias
    """
    df = pd.read_sql(query_ot, engine)
    
    return df

def data_fleet(df):
    fleet_counts = df['flota'].value_counts().reset_index()
    fleet_counts.columns = ['flota', 'count']
    return fleet_counts

def data_mechanic_table(df):
    tabla_mecanicos = df['mecanico'].value_counts().reset_index()
    tabla_mecanicos.columns = ['Mecánico', 'Asignadas']
    return tabla_mecanicos.to_dict('records')

def data_table(df):
    return df.to_dict('records')

def update_data(n):
    # Actualizar datos desde la base de datos
    df = connection_bdd()

    # Procesar datos
    fleet_counts = data_fleet(df)
    tabla_mecanicos_data = data_mechanic_table(df)
    tabla_data = data_table(df)

    # Actualizar el gráfico
    fig = px.line(fleet_counts,
                  x='flota',
                  y='count',
                  title='Patentes por Flota',
                  text='count',
                  labels={'count': 'Cantidad', 'flota': 'Flota'},
                  )
    
    # Cambiar el color de fondo de las barras
    fig.update_traces(line=dict(color='#2C3E50'), textposition='top center')

    # Centrar el título del gráfico
    fig.update_layout(
        title_x=0.5,
        xaxis=dict(tickfont=dict(size=10, family='Helvetica')),
        yaxis=dict(tickfont=dict(size=10, family='Helvetica')),
        title_font=dict(size=18, family='Helvetica')
    )

    # Obtener el total de registros
    total_registros = len(df)
    registros_en_proceso = len(df[df['estado'] == 'En proceso'])
    registros_borrador = len(df[df['estado'] == 'Borrador'])

    return (
        fig, tabla_data, tabla_mecanicos_data,
        f'OT Abiertas: {total_registros}',
        f'En Proceso:  {registros_en_proceso}',
        f'Borrador: {registros_borrador}'
    )
