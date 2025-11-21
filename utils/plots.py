import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def plot_shot_map(df):
    fig = px.scatter(
        df,
        x='shot_start_x',
        y='shot_start_y',
        color='shot_outcome_name',
        hover_data=['player_name', 'shot_statsbomb_xg'],
        title='Mapa de Tiros'
    )
    fig.add_shape(
        type='rect',
        x0=120, y0=0, x1=102, y1=80,
        line=dict(color='white')
    )
    fig.add_shape(
        type='rect',
        x0=120, y0=18, x1=114, y1=62,
        line=dict(color='white')
    )
    fig.add_shape(
        type='rect',
        x0=120, y0=30, x1=108, y1=50,
        line=dict(color='white')
    )
    fig.update_layout(
        xaxis_title='Largo del Campo',
        yaxis_title='Ancho del Campo',
        plot_bgcolor='green',
        xaxis=dict(range=[0, 120]),
        yaxis=dict(range=[0, 80])
    )
    return fig

def plot_shot_quality(df):
    fig = px.histogram(
        df,
        x='shot_statsbomb_xg',
        nbins=20,
        title='Distribución de Calidad de Tiro (xG)'
    )
    fig.update_layout(
        xaxis_title='xG (Goles Esperados)',
        yaxis_title='Cantidad de Tiros'
    )
    return fig

def plot_possession_duration(df):
    df_shot = df[df['shot_outcome_name'].notna()]
    fig = px.histogram(
        df_shot,
        x='possession_duration',
        nbins=30,
        title='Distribución de Duración de Posesión con Tiro'
    )
    fig.update_layout(
        xaxis_title='Duración de la Posesión (segundos)',
        yaxis_title='Cantidad de Posesiones'
    )
    return fig

def plot_defensive_actions(df):
    # This is a placeholder for a more complex defensive plot.
    # For now, we will plot the origin of opponent shots.
    fig = px.density_heatmap(
        df,
        x='shot_start_x',
        y='shot_start_y',
        z='shot_statsbomb_xg',
        histfunc='avg',
        title='Mapa de Calor de xG de Tiros del Rival'
    )
    fig.add_shape(
        type='rect',
        x0=0, y0=0, x1=18, y1=80,
        line=dict(color='white')
    )
    fig.add_shape(
        type='rect',
        x0=0, y0=18, x1=6, y1=62,
        line=dict(color='white')
    )
    fig.add_shape(
        type='rect',
        x0=0, y0=30, x1=12, y1=50,
        line=dict(color='white')
    )
    fig.update_layout(
        xaxis_title='Largo del Campo',
        yaxis_title='Ancho del Campo',
        plot_bgcolor='green',
        xaxis=dict(range=[0, 120]),
        yaxis=dict(range=[0, 80])
    )
    return fig

def plot_xg_scatter(df):
    """
    Crea un gráfico de dispersión de xG a favor vs xG en contra.
    """
    # Calcular xG a favor por equipo
    xg_favor = df.groupby('TeamName')['xg'].sum().reset_index()
    xg_favor.rename(columns={'xg': 'xG_Favor', 'TeamName': 'Equipo'}, inplace=True)

    # Calcular xG en contra por equipo
    xg_contra = df.groupby('RivalName')['xg'].sum().reset_index()
    xg_contra.rename(columns={'xg': 'xG_Contra', 'RivalName': 'Equipo'}, inplace=True)

    # Unir los dataframes
    df_xg = pd.merge(xg_favor, xg_contra, on='Equipo')

    # Crear el gráfico de dispersión para xG
    fig_xg = px.scatter(df_xg, x='xG_Contra', y='xG_Favor', text='Equipo',
                        title='xG a Favor vs. xG en Contra por Equipo')
    fig_xg.update_traces(textposition='top center')
    return fig_xg

def plot_xgot_scatter(df):
    """
    Crea un gráfico de dispersión de xGOT a favor vs xGOT en contra.
    """
    # Calcular xGOT a favor por equipo
    xgot_favor = df.groupby('TeamName')['xgot'].sum().reset_index()
    xgot_favor.rename(columns={'xgot': 'xGOT_Favor', 'TeamName': 'Equipo'}, inplace=True)

    # Calcular xGOT en contra por equipo
    xgot_contra = df.groupby('RivalName')['xgot'].sum().reset_index()
    xgot_contra.rename(columns={'xgot': 'xGOT_Contra', 'RivalName': 'Equipo'}, inplace=True)

    # Unir los dataframes
    df_xgot = pd.merge(xgot_favor, xgot_contra, on='Equipo')

    # Crear el gráfico de dispersión para xGOT
    fig_xgot = px.scatter(df_xgot, x='xGOT_Contra', y='xGOT_Favor', text='Equipo',
                          title='xGOT a Favor vs. xGOT en Contra por Equipo')
    fig_xgot.update_traces(textposition='top center')
    return fig_xgot
