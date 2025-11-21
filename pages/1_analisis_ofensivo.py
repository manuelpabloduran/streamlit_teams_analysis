import streamlit as st
import pandas as pd
import numpy as np
from utils.plots import plot_team_progression_with_hist, plot_offensive_sequences

st.title('Análisis Ofensivo')

# --- Carga y Preparación de Datos ---
@st.cache_data
def load_and_prepare_data(url):
    df = pd.read_csv(url)
    # !!! IMPORTANTE: Reemplaza 'location_x' y 'location_y' con los nombres de columna correctos para las coordenadas de eventos en tu CSV.
    if 'location_x' in df.columns and 'location_y' in df.columns:
        df = df.rename(columns={'location_x': 'x', 'location_y': 'y'})
    else:
        if 'x' not in df.columns: df['x'] = np.nan
        if 'y' not in df.columns: df['y'] = np.nan
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
    else: # y > 79
        return 'Pasillo Exterior Izquierdo'

df = load_and_prepare_data('possessions_with_shots.csv')
teams = sorted(df['TeamName'].unique())

# 1. Excluir posesiones con córners
posesiones_con_corner = df[df['corner_taken'].notna()]['Posesion'].unique()
df_sin_corners = df[~df['Posesion'].isin(posesiones_con_corner)]

# 2. Filtrar por eventos deseados y en campo rival
eventos_deseados = [
    'Pass', 'Take On', 'Ball recovery', 'BallDrive', 'Ball touch', 
    'Tackle', 'Interception', 'Blocked Pass', 'Offside Pass'
]
df_filtrado = df_sin_corners[
    (df_sin_corners['NaEventType'].isin(eventos_deseados)) &
    (df_sin_corners['x'] > 50)
].copy()

# 3. Asignar pasillos y ordenar eventos
df_filtrado['pasillo'] = df_filtrado['y'].apply(asignar_pasillo)
df_filtrado = df_filtrado.sort_values(by=['Posesion', 'time_seconds'])

# 4. Calcular estadísticas
grouped = df_filtrado.groupby('Posesion')
inicio_events = grouped.first()
fin_events = grouped.last()

# Calcular promedios por equipo
stats_df = grouped.agg(
    TeamName=('TeamName', 'first'),
    avg_pasillos=('pasillo', 'nunique'),
    duration=('time_seconds', lambda x: x.max() - x.min()),
    n_events=('time_seconds', 'count'),
    width=('y', lambda x: x.max() - x.min())
).groupby('TeamName').mean()

# 5. Calcular conteos de inicio y fin por pasillo
column_order = [
    'Pasillo Exterior Izquierdo', 'Pasillo Interior Izquierdo', 'Pasillo Central', 
    'Pasillo Interior Derecho', 'Pasillo Exterior Derecho'
]

def get_counts(df_events):
    counts = df_events.groupby(['TeamName', 'pasillo']).size().unstack(fill_value=0)
    # Asegurar que todas las columnas de pasillos existan
    for col in column_order:
        if col not in counts.columns:
            counts[col] = 0
    return counts[column_order]

conteo_inicio_liga = get_counts(inicio_events)
conteo_fin_liga = get_counts(fin_events)

# --- Interfaz de Streamlit ---
st.header('Análisis de Progresión por Equipo')

# Selección de equipo
team_name = st.selectbox('Selecciona un equipo:', teams)

if team_name:
    st.write(f"Mostrando análisis para **{team_name}**")
    
    st.header("Análisis de progresión por pasillo en campo rival")
    col1, col2 = st.columns(2)

    with col1:
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
            st.caption("Ingresos y finalizaciones por pasillo en campo rival")
        else:
            st.warning(f"No hay datos de progresión para {team_name}.")

    with col2:
        fig_sequences = plot_offensive_sequences(df_filtrado, team_name)
        if fig_sequences:
            st.pyplot(fig_sequences)
            st.caption("Secuencias típicas entre pasillos en campo rival")
        else:
            st.warning(f"No hay datos de secuencias ofensivas para {team_name}.")
