import streamlit as st
import pandas as pd
import numpy as np
from utils.plots import (
    plot_team_progression_with_hist, 
    plot_offensive_sequences, 
    plot_goals_sunburst, 
    plot_offensive_dashboard, 
    plot_goal_actions_bar,
    plot_xg_actions_bar,
    plot_area_entries_team, 
    plot_rival_half_entries_team, 
    plot_area_entry_passes, 
    plot_area_entry_by_corridor, 
    plot_distribution_comparison, 
    plot_area_entry_drives, 
    plot_area_entry_drives_by_corridor
)
from streamlit_plotly_events import plotly_events

st.set_page_config(layout="wide")

st.title('Análisis Defensivo')

# --- Carga y Preparación de Datos ---
@st.cache_data
def load_data():
    df = pd.read_csv('possessions_with_shots.csv')
    
    # Corrección de goles en propia puerta
    own_goal_condition = (df['NaEventType'] == 'Goal') & (df['own_goal'].notna())
    df['TeamName'] = np.where(
        own_goal_condition,
        np.where(df['TeamName'] == df['NaHomeTeam'], df['NaAwayTeam'], df['NaHomeTeam']),
        df['TeamName']
    )
    df['IdTeam'] = np.where(
        own_goal_condition,
        np.where(df['IdTeam'] == df['IdHomeTeam'], df['IdAwayTeam'], df['IdHomeTeam']),
        df['IdTeam']
    )

    # --- Cálculo de variables adicionales (a nivel de evento) ---
    df['dx'] = df['end_x'] - df['x']
    df['dy'] = df['end_y'] - df['y']
    df['Angle'] = np.arctan2(df['dy'], df['dx']).mod(2 * np.pi)

    # --- Cálculo de variables adicionales (a nivel de posesión) ---
    possession_duration = df.groupby('Posesion')['time_seconds'].transform(lambda x: x.max() - x.min())
    possession_counts = df.groupby('Posesion')['time_seconds'].transform('count')
    df['possession_duration'] = possession_duration.where(possession_counts > 1, np.nan)
    df['possession_duration'] = df['possession_duration'].clip(upper=100)
    df['possession_xg'] = df.groupby('Posesion')['xg'].transform('sum')
    df['possession_xg'] = df['possession_xg'].clip(upper=1)

    df['iniciacion_area'] = np.where(((df["x"] >= 84) & (df["y"] <= 81) & (df["y"] >= 19)), 1, 0)
    df['finalizacion_area'] = np.where(((df["end_x"] >= 84) & (df["end_y"] <= 81) & (df["end_y"] >= 19)), 1, 0)
    df['pase_peligroso_al_area'] = np.where(((df["iniciacion_area"] == 0) & (df["end_x"] >= 84) & (df["end_y"] <= 81) & (df["end_y"] >= 19)), 1, 0)

    df['cutback'] = np.where(((df["NaEventType"]=="Pass") & (df["finalizacion_area"]==1) & (df["x"]>80) & (df["y"]<=37) & (df["Angle"]>1.57) & (df["Angle"]<3.14)) | ((df["NaEventType"]=="Pass") & (df["finalizacion_area"]==1) & (df["chipped"].isna()) & (df["Outcome"]==1) & (df["x"]>80) & (df["y"]>=63) & (df["Angle"]>3.14) & (df["Angle"]<4.71)), 1, 0)
    df['dividido'] = np.where(((df["NaEventType"]=="Pass") & (df["finalizacion_area"]==1) & (df["x"]>80) & (df["y"]<=37) & (df["Angle"]>0) & (df["Angle"]<1.57)) | ((df["NaEventType"]=="Pass") & (df["finalizacion_area"]==1) & (df["chipped"].isna()) & (df["Outcome"]==1) & (df["x"]>80) & (df["y"]>=63) & (df["Angle"]>4.71) & (df["Angle"]<6.28)), 1, 0)

    df['DtGame'] = pd.to_datetime(df['DtGame']).dt.date
    return df

df = load_data()

# --- Filtros ---
min_date = df['DtGame'].min()
max_date = df['DtGame'].max()

st.markdown("---")
with st.expander("Filtros y Estadísticas", expanded=True):
    date_range = st.slider(
        "Selecciona un rango de fechas",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )
    if len(date_range) == 2:
        start_date, end_date = date_range
        df = df[(df['DtGame'] >= start_date) & (df['DtGame'] <= end_date)]

    col1, col2, col3 = st.columns([2, 2, 2])
    
    with col1:
        # Usamos RivalName para el análisis defensivo
        teams = sorted(df['RivalName'].unique())
        team_name = st.selectbox('Selecciona un equipo para analizar su defensa:', teams)

    # Hacemos una copia del dataframe para aplicar los filtros de la página
    df_page_filtered = df[df['RivalName'] == team_name].copy()

    with col2:
        play_types = sorted(df_page_filtered['play_type'].dropna().unique())
        play_type_name = st.selectbox('Selección de tipo de jugada', ["Todos"] + play_types)

    with col3:
        goal_only_filter = st.checkbox('Solo posesiones con gol recibido')

    col4, col5 = st.columns(2)
    with col4:
        possession_xg_filter = st.slider(
            'Filtro por xG de la Posesión del Rival',
            min_value=0.0,
            max_value=1.0,
            value=(0.0, 1.0),
            step=0.05
        )
    with col5:
        possession_duration_filter = st.slider(
            'Filtro por Duración de la Posesión del Rival (segundos)',
            min_value=0,
            max_value=100,
            value=(0, 100),
            step=1
        )

# Aplicar filtros al dataframe
if play_type_name != "Todos":
    poss_with_play_type = df_page_filtered[df_page_filtered['play_type'] == play_type_name]['Posesion'].unique()
    df_page_filtered = df_page_filtered[df_page_filtered['Posesion'].isin(poss_with_play_type)]

if goal_only_filter:
    goal_posesiones = df_page_filtered[df_page_filtered['NaEventType'] == 'Goal']['Posesion'].unique()
    df_page_filtered = df_page_filtered[df_page_filtered['Posesion'].isin(goal_posesiones)]

if possession_xg_filter:
    df_page_filtered = df_page_filtered[
        (df_page_filtered['possession_xg'] >= possession_xg_filter[0]) &
        (df_page_filtered['possession_xg'] <= possession_xg_filter[1])
    ]

if possession_duration_filter:
    df_page_filtered = df_page_filtered[
        ((df_page_filtered['possession_duration'] >= possession_duration_filter[0]) &
        (df_page_filtered['possession_duration'] <= possession_duration_filter[1])) |
        (df_page_filtered['possession_duration'].isna())
    ]

# --- Estadísticas Defensivas ---
st.markdown("---")
st.subheader("Estadísticas Defensivas (Acciones del Rival)")

shot_events = ['Attempt Saved', 'Miss', 'Post', 'Goal']
df_shots = df_page_filtered[df_page_filtered['NaEventType'].isin(shot_events)].copy()

total_goals_conceded = int(df_page_filtered[df_page_filtered['NaEventType'] == 'Goal'].shape[0])
total_shots_conceded = int(df_shots.shape[0])
total_xg_conceded = df_shots['xg'].sum()
total_xgot_conceded = df_shots['xgot'].sum()

xg_per_shot_conceded = total_xg_conceded / total_shots_conceded if total_shots_conceded > 0 else 0
xgot_per_shot_conceded = total_xgot_conceded / total_shots_conceded if total_shots_conceded > 0 else 0

m_col1, m_col2, m_col3, m_col4 = st.columns(4)
m_col1.metric("Goles Recibidos", f"{total_goals_conceded}")
m_col2.metric("Tiros Recibidos", f"{total_shots_conceded}")
m_col3.metric("xG Recibido", f"{total_xg_conceded:.2f}")
m_col4.metric("xG por Tiro Recibido", f"{xg_per_shot_conceded:.2f}")
m_col5, m_col6, _, _ = st.columns(4)
m_col5.metric("xGOT Recibido", f"{total_xgot_conceded:.2f}")
m_col6.metric("xGOT por Tiro Recibido", f"{xgot_per_shot_conceded:.2f}")

st.markdown("---")
st.header("Análisis de Amenazas Recibidas")

if team_name:
    st.write(f"Mostrando análisis defensivo para **{team_name}** (acciones de sus rivales)")

    # Sunburst en una fila propia
    st.subheader("Goles Recibidos por Tipo de Jugada")
    fig_sunburst, _ = plot_goals_sunburst(df_page_filtered, team_name, filter_col='RivalName')
    if fig_sunburst:
        st.plotly_chart(fig_sunburst, use_container_width=True)
    else:
        st.warning(f"No hay datos de goles recibidos para {team_name}.")

    # Gráficos de acciones en dos columnas
    col_actions1, col_actions2 = st.columns(2)

    with col_actions1:
        st.subheader("Características de las Posesiones con Gol Recibido")
        fig_actions = plot_goal_actions_bar(df_page_filtered, team_name, filter_col='RivalName')
        if fig_actions:
            st.plotly_chart(fig_actions, use_container_width=True)
        else:
            st.warning(f"No se pudo generar el gráfico de acciones en goles recibidos para {team_name}.")

    with col_actions2:
        st.subheader("xG Acumulado del Rival por Tipo de Acción")
        fig_xg_actions = plot_xg_actions_bar(df_page_filtered, team_name, filter_col='RivalName')
        if fig_xg_actions:
            st.plotly_chart(fig_xg_actions, use_container_width=True)
        else:
            st.warning(f"No se pudo generar el gráfico de xG por acción para {team_name}.")


    st.subheader("Mapa de Goles y Tiros a Puerta Recibidos")
    fig_dashboard = plot_offensive_dashboard(df_page_filtered, team_name, filter_col='RivalName')
    if fig_dashboard:
        st.pyplot(fig_dashboard, use_container_width=True)
    else:
        st.warning(f"No se pudo generar el dashboard de finalización para {team_name}.")

    st.header("Análisis de Progresión del Rival")

    col_entries1, col_entries2 = st.columns(2)

    with col_entries1:
        st.subheader("Ingresos del Rival a Campo Propio")
        fig_rival_half_entries, _, _ = plot_rival_half_entries_team(df_page_filtered, team_name, filter_col='RivalName')
        if fig_rival_half_entries:
            st.pyplot(fig_rival_half_entries, use_container_width=True)
        else:
            st.warning("No se pudo generar el gráfico de ingresos a campo rival.")
    
    with col_entries2:
        st.subheader("Ingresos del Rival al Área Propia")
        fig_area_entries, _, _ = plot_area_entries_team(df_page_filtered, team_name, filter_col='RivalName')
        if fig_area_entries:
            st.pyplot(fig_area_entries, use_container_width=True)
        else:
            st.warning("No se pudo generar el gráfico de entradas al área del rival.")

    col_entry1, col_entry2 = st.columns(2)
    with col_entry1:
        st.subheader("Entradas al Área Propia por Pases del Rival")
        fig_entry_passes = plot_area_entry_passes(df_page_filtered, team_name, filter_col='RivalName')
        if fig_entry_passes:
            st.pyplot(fig_entry_passes, use_container_width=True)
        else:
            st.warning("No se pudo generar el gráfico de pases de entrada al área del rival.")

    with col_entry2:
        st.subheader("Entradas al Área Propia por Pasillo de Origen del Rival")
        fig_entry_corridor, _ = plot_area_entry_by_corridor(df_page_filtered, team_name, filter_col='RivalName')
        if fig_entry_corridor:
            st.pyplot(fig_entry_corridor, use_container_width=True)
        else:
            st.warning("No se pudo generar el gráfico de entradas al área por pasillo del rival.")
            
    st.markdown("---")
    st.subheader("Entradas al Área Propia por Conducción del Rival")
    col_drive1, col_drive2 = st.columns(2)
    with col_drive1:
        fig_drive_entries, _ = plot_area_entry_drives(df_page_filtered, team_name, filter_col='RivalName')
        if fig_drive_entries:
            st.pyplot(fig_drive_entries, use_container_width=True)
        else:
            st.warning("No se pudo generar el gráfico de conducciones de entrada al área del rival.")

    with col_drive2:
        fig_drive_corridor, _ = plot_area_entry_drives_by_corridor(df_page_filtered, team_name, filter_col='RivalName')
        if fig_drive_corridor:
            st.pyplot(fig_drive_corridor, use_container_width=True)
        else:
            st.warning("No se pudo generar el gráfico de conducciones al área por pasillo del rival.")
else:
    st.info("Selecciona un equipo para comenzar el análisis defensivo.")
