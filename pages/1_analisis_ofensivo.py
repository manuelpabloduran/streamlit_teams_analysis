import streamlit as st
import pandas as pd
import numpy as np
from utils.plots import plot_team_progression_with_hist, plot_offensive_sequences, plot_player_xg_xgot, plot_goals_sunburst, plot_offensive_dashboard, plot_goal_actions_bar, plot_pass_matrix, plot_pass_xg_matrix, plot_area_entries_team
from streamlit_plotly_events import plotly_events

st.set_page_config(layout="wide")

st.title('Análisis Ofensivo')

# --- Carga y Preparación de Datos ---
@st.cache_data

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

# --- Conversión y filtro de fecha ---
df['DtGame'] = pd.to_datetime(df['DtGame']).dt.date
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
        # Aseguramos que el df se filtre por el rango de fechas
        df = df[(df['DtGame'] >= start_date) & (df['DtGame'] <= end_date)]
    
    col1, col2, col3, col4 = st.columns([2, 2, 2, 1.5])
    
    with col1:
        teams = sorted(df['TeamName'].unique())
        team_name = st.selectbox('Selecciona un equipo:', teams)

    # Hacemos una copia del dataframe para aplicar los filtros de la página
    df_page_filtered = df[df['TeamName'] == team_name].copy()

    with col2:
        players = sorted(df_page_filtered['NaPlayer'].dropna().unique())
        player_name = st.selectbox('Selección de Jugador', ["Todos"] + players)

    with col3:
        play_type_map = {
            "Regular_play": "Jugada Regular",
            "Set_piece": "Balón parado",
            "Penalty": "Penalti",
            "Fast_break": "Transición rápida",
            "From_corner": "Corner",
            "Free_kick": "Balón parado",
            "Throw-in_set_piece": "Saque de banda"
        }
        
        # Mapeamos los valores originales a los nombres amigables para el filtro
        available_play_types = sorted(df_page_filtered['play_type'].dropna().unique())
        mapped_options = {play_type_map.get(pt, pt): pt for pt in available_play_types}
        
        # Creamos una lista de opciones únicas para mostrar en el selectbox
        display_options = sorted(list(set(mapped_options.keys())))
        
        play_type_display = st.selectbox('Filtrar por tipo de jugada', ["Todos"] + display_options)

    with col4:
        goal_only_filter = st.checkbox('Solo posesiones con gol')

# Aplicar filtros al dataframe
if player_name != "Todos":
    df_page_filtered = df_page_filtered[df_page_filtered['NaPlayer'] == player_name]

if goal_only_filter:
    goal_posesiones = df_page_filtered[df_page_filtered['NaEventType'] == 'Goal']['Posesion'].unique()
    df_page_filtered = df_page_filtered[df_page_filtered['Posesion'].isin(goal_posesiones)]

if play_type_display != "Todos":
    # Mapeo inverso: encontrar las claves originales para el valor amigable seleccionado
    original_values_to_filter = [k for k, v in play_type_map.items() if v == play_type_display]
    
    # Si no se encuentra en el mapa (porque es un valor original), usarlo directamente
    if not original_values_to_filter:
        original_values_to_filter = [play_type_display]

    play_type_posesiones = df_page_filtered[df_page_filtered['play_type'].isin(original_values_to_filter)]['Posesion'].unique()
    df_page_filtered = df_page_filtered[df_page_filtered['Posesion'].isin(play_type_posesiones)]

# --- Cálculo de Estadísticas ---
st.markdown("---")
st.subheader("Estadísticas Generales")

# Filtrar eventos de tiro
shot_events = ['Attempt Saved', 'Miss', 'Post', 'Goal']
df_shots = df_page_filtered[df_page_filtered['NaEventType'].isin(shot_events)].copy()

# Calcular estadísticas
total_goals = int(df_page_filtered[df_page_filtered['NaEventType'] == 'Goal'].shape[0])
total_shots = int(df_shots.shape[0])
total_xg = df_shots['xg'].sum()
total_xgot = df_shots['xgot'].sum()

# Evitar división por cero
xg_per_shot = total_xg / total_shots if total_shots > 0 else 0
xgot_per_shot = total_xgot / total_shots if total_shots > 0 else 0

xg_conversion = total_xgot - total_xg
avg_xg_conversion = xgot_per_shot - xg_per_shot

# Mostrar estadísticas en columnas
m_col1, m_col2, m_col3, m_col4 = st.columns(4)
m_col1.metric("Goles Totales", f"{total_goals}")
m_col2.metric("Tiros Totales", f"{total_shots}")
m_col3.metric("xG Acumulado", f"{total_xg:.2f}")
m_col4.metric("xG por Tiro", f"{xg_per_shot:.2f}")

m_col5, m_col6, m_col7, m_col8 = st.columns(4)
m_col5.metric("xGOT Acumulado", f"{total_xgot:.2f}")
m_col6.metric("xGOT por Tiro", f"{xgot_per_shot:.2f}")
m_col7.metric("xG Conversion (Total)", f"{xg_conversion:.2f}")
m_col8.metric("xG Conversion (Promedio)", f"{avg_xg_conversion:.2f}")

# --- Inicio del Análisis con el DF ya filtrado ---

# 1. Excluir posesiones con córners
posesiones_con_corner = df_page_filtered[df_page_filtered['corner_taken'].notna()]['Posesion'].unique()
df_sin_corners = df_page_filtered[~df_page_filtered['Posesion'].isin(posesiones_con_corner)]

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

if team_name:
    st.write(f"Mostrando análisis para **{team_name}**")

    st.header("Estadísticas de Finalización")
    
    fig_players = plot_player_xg_xgot(df_page_filtered, team_name)
    if fig_players:
        st.plotly_chart(fig_players, use_container_width=True)
    else:
        st.warning(f"No se pudo generar el gráfico de xG/xGOT por jugador para {team_name}.")

    col_sun, col_actions = st.columns(2)

    with col_sun:
        fig_sunburst, df_goles_es = plot_goals_sunburst(df_page_filtered, team_name)
        if fig_sunburst:
            st.plotly_chart(fig_sunburst, use_container_width=True)
        else:
            st.warning(f"No hay datos de goles para {team_name}.")

    with col_actions:
        fig_actions = plot_goal_actions_bar(df_page_filtered, team_name)
        if fig_actions:
            st.plotly_chart(fig_actions, use_container_width=True)
        else:
            st.warning(f"No se pudo generar el gráfico de acciones en goles para {team_name}.")

    fig_dashboard = plot_offensive_dashboard(df_page_filtered, team_name)
    if fig_dashboard:
        st.pyplot(fig_dashboard, use_container_width=True)
    else:
        st.warning(f"No se pudo generar el dashboard de finalización para {team_name}.")

    st.header("Progresiones")

    col_matrix1, col_matrix2 = st.columns(2)

    with col_matrix1:
        st.subheader("Matriz de Pases - Progresión con Finalización")
        fig_pass_matrix_full = plot_pass_matrix(df_page_filtered, team_name, min_x=0)
        if fig_pass_matrix_full:
            st.pyplot(fig_pass_matrix_full, use_container_width=True)
        else:
            st.warning(f"No se pudo generar la matriz de pases para {team_name}.")

    with col_matrix2:
        st.subheader("Matriz de Pases (Último Tercio)")
        fig_pass_matrix_final_third = plot_pass_matrix(df_page_filtered, team_name, min_x=66.66)
        if fig_pass_matrix_final_third:
            st.pyplot(fig_pass_matrix_final_third, use_container_width=True)
        else:
            st.warning(f"No se pudo generar la matriz de pases en último tercio para {team_name}.")

    st.markdown("---")
    st.header("Pases Clave (xG)")
    
    col_xg_matrix1, col_xg_matrix2 = st.columns(2)

    with col_xg_matrix1:
        st.subheader("xG Chain - Todo el campo")
        fig_pass_xg_matrix_full = plot_pass_xg_matrix(df_page_filtered, team_name, min_x=0)
        if fig_pass_xg_matrix_full:
            st.pyplot(fig_pass_xg_matrix_full, use_container_width=True)
        else:
            st.warning(f"No se pudo generar la matriz de pases de xG para {team_name}.")

    with col_xg_matrix2:
        st.subheader("xG Chain - Último Tercio")
        fig_pass_xg_matrix_final_third = plot_pass_xg_matrix(df_page_filtered, team_name, min_x=66.66)
        if fig_pass_xg_matrix_final_third:
            st.pyplot(fig_pass_xg_matrix_final_third, use_container_width=True)
        else:
            st.warning(f"No se pudo generar la matriz de pases de xG en último tercio para {team_name}.")

    st.markdown("---")
    st.header("Entradas al Área Rival")
    fig_area_entries, _, _ = plot_area_entries_team(df_page_filtered, team_name)
    if fig_area_entries:
        st.pyplot(fig_area_entries, use_container_width=True)
    else:
        st.warning(f"No se pudo generar el gráfico de entradas al área para {team_name}.")

    with st.expander("Análisis de progresión por pasillo en campo rival", expanded=False):
        # Para esta sección, usamos un dataframe filtrado solo por equipo, no por los otros filtros.
        df_progression_analysis = df[df['TeamName'] == team_name]
        
        # 1. Excluir posesiones con córners
        prog_posesiones_con_corner = df_progression_analysis[df_progression_analysis['corner_taken'].notna()]['Posesion'].unique()
        prog_df_sin_corners = df_progression_analysis[~df_progression_analysis['Posesion'].isin(prog_posesiones_con_corner)]

        # 2. Filtrar por eventos deseados y en campo rival
        prog_df_filtrado = prog_df_sin_corners[
            (prog_df_sin_corners['NaEventType'].isin(eventos_deseados)) &
            (prog_df_sin_corners['x'] > 50)
        ].copy()

        # 3. Asignar pasillos y ordenar eventos
        prog_df_filtrado['pasillo'] = prog_df_filtrado['y'].apply(asignar_pasillo)
        prog_df_filtrado = prog_df_filtrado.sort_values(by=['Posesion', 'time_seconds'])

        # 4. Calcular estadísticas
        prog_grouped = prog_df_filtrado.groupby('Posesion')
        prog_inicio_events = prog_grouped.first()
        prog_fin_events = prog_grouped.last()

        prog_stats_df = prog_grouped.agg(
            TeamName=('TeamName', 'first'),
            avg_pasillos=('pasillo', 'nunique'),
            duration=('time_seconds', lambda x: x.max() - x.min()),
            n_events=('time_seconds', 'count'),
            width=('y', lambda x: x.max() - x.min())
        ).groupby('TeamName').mean()

        # 5. Calcular conteos de inicio y fin por pasillo
        prog_conteo_inicio_liga = get_counts(prog_inicio_events)
        prog_conteo_fin_liga = get_counts(prog_fin_events)

        # Generar y mostrar el gráfico de progresión
        fig = plot_team_progression_with_hist(
            df_analisis_progreso=prog_df_filtrado,
            team_name=team_name,
            conteo_inicio=prog_conteo_inicio_liga,
            conteo_fin=prog_conteo_fin_liga,
            stats=prog_stats_df
        )

        if fig:
            st.pyplot(fig, use_container_width=True)
            st.caption("Ingresos y finalizaciones por pasillo en campo rival")
        else:
            st.warning(f"No hay datos de progresión para {team_name}.")

        # Generar y mostrar el gráfico de secuencias
        fig_sequences = plot_offensive_sequences(prog_df_filtrado, team_name)
        if fig_sequences:
            st.pyplot(fig_sequences, use_container_width=True)
            st.caption("Secuencias típicas entre pasillos en campo rival")
        else:
            st.warning(f"No hay datos de secuencias ofensivas para {team_name}.")
