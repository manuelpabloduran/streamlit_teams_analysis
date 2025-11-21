import streamlit as st
import pandas as pd
import numpy as np
from utils.plots import plot_team_progression_with_hist, pasillos_y

st.title('Análisis Ofensivo')

# --- Carga de Datos ---
@st.cache_data
def load_data(url):
    df = pd.read_csv(url)
    # Asumiendo que el CSV tiene columnas 'x' e 'y' para la progresión.
    # Si los nombres son diferentes (ej. 'start_x', 'start_y'), ajústalos aquí.
    # Si no existen, el gráfico no mostrará los puntos de eventos.
    if 'x' not in df.columns:
        df['x'] = np.nan
    if 'y' not in df.columns:
        df['y'] = np.nan
    if 'IdCompetition' not in df.columns:
        df['IdCompetition'] = 0 # Placeholder si no existe
    return df

# Definir la función para asignar pasillos
def asignar_pasillo(y):
    if y < 21:
        return 'Pasillo Exterior Derecho'
    elif 21 <= y <= 37:
        return 'Pasillo Interior Derecho'
    elif 37 < y < 63:
        return 'Pasillo Central'
    elif 63 <= y <= 79:
        return 'Pasillo Interior Izquierdo'
    else: # y > 81
        return 'Pasillo Exterior Izquierdo'

df = load_data('possessions_with_shots.csv')
teams = sorted(df['TeamName'].unique())

# Preparar datos para el análisis de inicio/fin
df_analisis_progreso = df[df['x'] > 50].copy()
df_analisis_progreso['pasillo'] = df_analisis_progreso['y'].apply(asignar_pasillo)
df_analisis_progreso = df_analisis_progreso.sort_values(by=['Posesion', 'time_seconds'])

# Reordenar las columnas para una mejor visualización
column_order = [
    'Pasillo Exterior Izquierdo', 
    'Pasillo Interior Izquierdo', 
    'Pasillo Central', 
    'Pasillo Interior Derecho', 
    'Pasillo Exterior Derecho'
]

# 1. Excluir posesiones con córners
posesiones_con_corner = df[df['corner_taken'].notna()]['Posesion'].unique()
df_sin_corners = df[~df['Posesion'].isin(posesiones_con_corner)]

# 2. Filtrar por los NaEventType deseados
eventos_deseados = [
    'Pass', 'Take On', 'Ball recovery', 'BallDrive', 'Ball touch', 
    'Tackle', 'Interception', 'Blocked Pass', 'Offside Pass'
]
df_filtrado = df_sin_corners[df_sin_corners['NaEventType'].isin(eventos_deseados)].copy()

# Función para procesar un dataframe de una competición
def procesar_competicion(df_comp):
    # Aplicar filtro de campo rival (x > 50)
    df_rival = df_comp[df_comp['x'] > 50].copy()
    # Asignar pasillos
    df_rival['pasillo'] = df_rival['y'].apply(asignar_pasillo)
    # Contar ocurrencias
    conteo = df_rival.groupby(['TeamName', 'pasillo']).size().unstack(fill_value=0)
    # Reordenar y asegurar columnas
    for col in column_order:
        if col not in conteo.columns:
            conteo[col] = 0
    return conteo[column_order]

# 3. Separar por competición y procesar
conteo_liga = procesar_competicion(df_filtrado)

# Agrupar por posesión para obtener primer/último evento y estadísticas
grouped = df_filtrado.groupby('Posesion')
inicio_events = grouped.first()
fin_events = grouped.last()

# Calcular estadísticas por posesión
possession_stats = grouped.agg(
    TeamName=('TeamName', 'first'),
    IdCompetition=('IdCompetition', 'first'),
    avg_pasillos=('pasillo', 'nunique'),
    duration=('time_seconds', lambda x: x.max() - x.min()),
    n_events=('time_seconds', 'count'),
    width=('y', lambda x: x.max() - x.min())
)

# Calcular promedios por equipo
stats_df = possession_stats.groupby('TeamName').agg({
    'IdCompetition': 'first',
    'avg_pasillos': 'mean',
    'duration': 'mean',
    'n_events': 'mean',
    'width': 'mean'
}).reset_index()

# Separar estadísticas por competición
stats_df = stats_df.set_index('TeamName')

# Función para obtener los conteos de inicio y fin por competición
def get_start_end_counts(df_start_events, df_end_events):
    df_start_comp = df_start_events.copy()
    df_end_comp = df_end_events.copy()
    
    conteo_inicio = df_start_comp.groupby(['TeamName', 'pasillo']).size().unstack(fill_value=0)
    conteo_fin = df_end_comp.groupby(['TeamName', 'pasillo']).size().unstack(fill_value=0)
    
    for col in column_order:
        if col not in conteo_inicio.columns:
            conteo_inicio[col] = 0
        if col not in conteo_fin.columns:
            conteo_fin[col] = 0
            
    return conteo_inicio[column_order], conteo_fin[column_order]

# Obtener conteos para ambas ligas
conteo_inicio_liga, conteo_fin_liga = get_start_end_counts(inicio_events, fin_events)



st.header('Análisis de Progresión por Equipo')

# Selección de equipo
team_name = st.selectbox('Selecciona un equipo:', teams)

if team_name:
    st.write(f"Mostrando análisis para **{team_name}**")
    
    # Generar y mostrar el gráfico
    fig = plot_team_progression_with_hist(
        df_analisis_progreso=df_filtrado,
        team_name=team_name,
        conteo_inicio=conteo_inicio_liga,
        conteo_fin=conteo_fin_liga,
        stats=stats_df
    )

    if fig:
        st.pyplot(fig)
    else:
        st.warning(f"No hay datos de progresión para {team_name} en la competición seleccionada.")
