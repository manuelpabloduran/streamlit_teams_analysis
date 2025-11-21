import streamlit as st
import pandas as pd
import numpy as np
from utils.plots import plot_team_progression_with_hist, pasillos_y

st.title('Análisis Ofensivo')

# --- Carga de Datos (Placeholder) ---
# En una aplicación real, cargarías tus datos aquí.
# Por ahora, crearemos datos de ejemplo para que el gráfico funcione.
@st.cache_data
def load_data():
    # df_analisis_progreso
    teams = ['Racing de Santander', 'Real Zaragoza', 'Levante UD']
    competitions = {102: 'La Liga Hypermotion'}
    data = []
    for team in teams:
        for _ in range(100):
            data.append({
                'TeamName': team,
                'IdCompetition': 102,
                'x': np.random.uniform(0, 100),
                'y': np.random.uniform(0, 100)
            })
    df_analisis_progreso = pd.DataFrame(data)

    # stats
    stats_data = {
        'avg_pasillos': [2.5, 3.1, 2.8],
        'width': [45.2, 50.1, 48.5],
        'duration': [8.5, 10.2, 9.1],
        'n_events': [15.3, 12.1, 14.0]
    }
    stats = pd.DataFrame(stats_data, index=teams)

    # conteo_inicio y conteo_fin
    pasillos_keys = list(pasillos_y.keys())
    conteo_inicio_data = {team: {pasillo: np.random.randint(0, 20) for pasillo in pasillos_keys} for team in teams}
    conteo_fin_data = {team: {pasillo: np.random.randint(0, 15) for pasillo in pasillos_keys} for team in teams}
    conteo_inicio = pd.DataFrame.from_dict(conteo_inicio_data, orient='index')
    conteo_fin = pd.DataFrame.from_dict(conteo_fin_data, orient='index')

    return df_analisis_progreso, stats, conteo_inicio, conteo_fin, teams, competitions

df_analisis_progreso, stats, conteo_inicio, conteo_fin, teams, competitions = load_data()
# --- Fin Carga de Datos ---


st.header('Análisis de Progresión por Equipo')

# Selección de equipo
team_name = st.selectbox('Selecciona un equipo:', teams)
competition_id = 102 # Fijo para el ejemplo

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
