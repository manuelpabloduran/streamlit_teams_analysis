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

df_analisis_progreso = load_data('possessions_with_shots.csv')
teams = sorted(df_analisis_progreso['TeamName'].unique())

# --- Creación de DataFrames de estadísticas (Placeholder) ---
# Debes reemplazar esto con tu lógica de cálculo real a partir de df_analisis_progreso
stats = pd.DataFrame(index=teams)
stats['avg_pasillos'] = np.nan
stats['width'] = np.nan
stats['duration'] = np.nan
stats['n_events'] = np.nan

pasillos_keys = list(pasillos_y.keys())
conteo_inicio = pd.DataFrame(columns=pasillos_keys, index=teams).fillna(0)
conteo_fin = pd.DataFrame(columns=pasillos_keys, index=teams).fillna(0)
# --- Fin de Placeholders ---


st.header('Análisis de Progresión por Equipo')

# Selección de equipo
team_name = st.selectbox('Selecciona un equipo:', teams)
competition_id = 0 # Ya no se usa para filtrar, se pasa un valor dummy

if team_name:
    st.write(f"Mostrando análisis para **{team_name}**")
    
    # Generar y mostrar el gráfico
    fig = plot_team_progression_with_hist(
        df_analisis_progreso=df_analisis_progreso,
        team_name=team_name,
        competition_id=competition_id,
        conteo_inicio=conteo_inicio,
        conteo_fin=conteo_fin,
        stats=stats
    )

    if fig:
        st.pyplot(fig)
    else:
        st.warning(f"No hay datos de progresión para {team_name} en la competición seleccionada.")
