import os
import streamlit as st
import pandas as pd
import numpy as np
from utils.plots import plot_pressure_kde, highlight_team_scatter
from preprocessing import add_pressures
import plotly.express as px
import plotly.graph_objects as go


st.set_page_config(layout="wide")
st.title('Presiones')

# ---------------- Helpers ----------------

def filter_if_selected(df, col, values):
    if col in df.columns and values:
        return df[df[col].isin(values)]
    return df


def parse_minute_ranges(series, ranges):
    minutes = pd.to_numeric(series.astype(str).str.extract(r'(\d+)')[0], errors='coerce')
    mask = pd.Series(False, index=series.index)
    for r in ranges:
        if r == '0-15':   mask |= minutes.between(0, 15)
        if r == '16-30':  mask |= minutes.between(16, 30)
        if r == '31-45':  mask |= minutes.between(31, 45)
        if r == '46-60':  mask |= minutes.between(46, 60)
        if r == '61-75':  mask |= minutes.between(61, 75)
        if r == '76+':    mask |= minutes >= 76
    return mask


def parse_tercio(posx, tercios):
    posx = pd.to_numeric(posx, errors='coerce')
    mask = pd.Series(False, index=posx.index)
    for t in tercios:
        if t == 'Primer tercio':   mask |= posx.between(0, 33.5)
        if t == 'Tercio medio':    mask |= posx.between(33.5, 67)
        if t == 'Último tercio':   mask |= posx.between(67, 100)
    return mask


# ---------------- Data ----------------

@st.cache_data
def load_and_preprocess_data():
    _path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'preprocessed_SSD_25-26.parquet')
    df = pd.read_parquet(_path)
    df = add_pressures(df)
    if 'fecha' not in df.columns and 'DtGame' in df.columns:
        df['fecha'] = pd.to_datetime(df['DtGame']).dt.date
    return df

df = load_and_preprocess_data()
# ---------------- UI ----------------

minute_options = ["0-15", "16-30", "31-45", "46-60", "61-75", "76+"]
tercio_options = ['Primer tercio', 'Tercio medio', 'Último tercio']

with st.expander("Filtros", expanded=True):

    min_date, max_date = df['fecha'].min(), df['fecha'].max()
    date_range = st.date_input("Rango de fechas", value=(min_date, max_date))

    teams = sorted(df['equipo_vs_name'].dropna().unique())
    team_choice = st.selectbox('Equipo:', ['Todos'] + teams)

    # Player filter
    player_col = 'jugador' if 'jugador' in df.columns else ('NaPlayer' if 'NaPlayer' in df.columns else None)
    if player_col:
        if team_choice != 'Todos':
            player_options = sorted(df[df['equipo_vs_name'] == team_choice][player_col].dropna().unique())
        else:
            player_options = sorted(df[player_col].dropna().unique())
        player_choice = st.multiselect('Jugadores:', player_options)
    else:
        player_choice = []

    intensity_options = sorted(df['intensity'].dropna().unique())
    intensity_choice = st.selectbox('Intensidad:', ['Todos'] + intensity_options)

    minute_choice = st.multiselect('Minutos:', minute_options, default=minute_options)
    tercio_choice = st.multiselect('Tercio:', tercio_options, default=tercio_options)

    outcome_options = sorted(df['outcome_type'].dropna().unique()) if 'outcome_type' in df.columns else []
    outcome_choice = st.multiselect('Outcome:', outcome_options, default=outcome_options)

    if 'estado_partido' in df.columns:
        if team_choice != 'Todos':
            estado_choice = st.multiselect(
                'Estado:',
                [f'Gana_{team_choice}', 'Empate', 'Pierde'],
                default=[f'Gana_{team_choice}', 'Empate', 'Pierde']
            )
        else:
            estado_choice = st.multiselect(
                'Estado:',
                sorted(df['estado_partido'].dropna().unique()),
                default=sorted(df['estado_partido'].dropna().unique())
            )
    else:
        estado_choice = []

    # BallRecovery filters
    col_prev, col_next = st.columns(2)
    with col_prev:
        filter_prev_ballrecovery = st.checkbox('Solo si previous_event = BallRecovery')
    with col_next:
        filter_next_ballrecovery = st.checkbox('Solo si next_event_posesion = BallRecovery')

# ---------------- Filtros ----------------

# Aplicar filtros comunes (sin filtro de equipo aún)
filtered_base = df
filtered_base = filtered_base[(filtered_base['fecha'] >= date_range[0]) & (filtered_base['fecha'] <= date_range[1])]
df_no_team = filtered_base.copy()

if intensity_choice != 'Todos':
    filtered_base = filtered_base[filtered_base['intensity'] == intensity_choice]

filtered_base = filter_if_selected(filtered_base, 'outcome_type', outcome_choice)

if minute_choice and set(minute_choice) != set(minute_options):
    filtered_base = filtered_base[parse_minute_ranges(filtered_base['minute'], minute_choice)]

if tercio_choice and set(tercio_choice) != set(tercio_options):
    filtered_base = filtered_base[parse_tercio(filtered_base['positionX'], tercio_choice)]

# Estado del partido
if 'estado_partido' in filtered_base.columns and estado_choice:
    ep = filtered_base['estado_partido'].astype(str).str.lower().str.strip()

    if team_choice != 'Todos':
        team = team_choice.lower()
        mask = False

        if f'gana_{team}' in [s.lower() for s in estado_choice]:
            mask |= ep.str.contains('gana') & ep.str.contains(team)
        if 'empate' in [s.lower() for s in estado_choice]:
            mask |= ep == 'empate'
        if 'pierde' in [s.lower() for s in estado_choice]:
            mask |= (~(ep.str.contains('gana') & ep.str.contains(team))) & (ep != 'empate')

        filtered_base = filtered_base[mask]
    else:
        filtered_base = filtered_base[filtered_base['estado_partido'].isin(estado_choice)]

# Player filter
if player_choice and player_col:
    filtered_base = filtered_base[filtered_base[player_col].isin(player_choice)]

# BallRecovery filters
if filter_prev_ballrecovery and 'previous_event' in filtered_base.columns:
    filtered_base = filtered_base[filtered_base['previous_event'] == 'BallRecovery']

if filter_next_ballrecovery and 'next_event_posesion' in filtered_base.columns:
    filtered_base = filtered_base[filtered_base['next_event_posesion'] == 'BallRecovery']

# Filtro de equipo separado por tipo de mapa
if team_choice != 'Todos':
    filtered_recibidas = filtered_base[filtered_base['equipo_vs_name'] == team_choice]
    filtered_realizadas = filtered_base[filtered_base['TeamName'] == team_choice]
else:
    filtered_recibidas = filtered_base
    filtered_realizadas = filtered_base

# Para métricas usamos recibidas (comportamiento original)
filtered = filtered_recibidas

# ---------------- Resultados ----------------

m_col1, m_col2, m_col3, m_col4 = st.columns(4)
final_total = int(filtered.shape[0])
m_col1.metric("Total presiones", final_total)
alta = filtered[filtered.intensity == 'high'].shape[0] / final_total * 100 if final_total else 0
m_col2.metric("Presiones altas intensidad", round(alta,2))
media = filtered[filtered.intensity == 'medium'].shape[0] / final_total * 100 if final_total else 0
m_col3.metric("Presiones media intensidad", round(media,2))
baja = filtered[filtered.intensity == 'low'].shape[0] / final_total * 100 if final_total else 0
m_col4.metric("Presiones baja intensidad", round(baja,2))

scatter_df = (
    df_no_team
    .groupby(['equipo_vs_name'], as_index=False)['shirtNumber'].count()
    .merge(
        df_no_team.groupby(['homeTeamName'], as_index=False)['shirtNumber'].count(),
        left_on='equipo_vs_name',
        right_on='homeTeamName',
        suffixes=('_pressures', '_total')
    )
)

fig_scatter = highlight_team_scatter(scatter_df, team_choice)

st.plotly_chart(fig_scatter, use_container_width=True)

# ---------------- Mapa ----------------

title_suffix = ''
if estado_choice:
    if team_choice != 'Todos':
        parts = []
        if f'Gana_{team_choice}' in estado_choice: parts.append('Gana')
        if 'Empate' in estado_choice: parts.append('Empate')
        if 'Pierde' in estado_choice: parts.append('Pierde')
        if parts:
            title_suffix = ' (' + ', '.join(parts) + ')'
    else:
        title_suffix = ' (' + ', '.join(estado_choice) + ')'

team_for_plot = None if team_choice == 'Todos' else team_choice

map_col1, map_col2 = st.columns(2)

with map_col1:
    with st.status("Procesando mapa de presiones recibidas...", expanded=False) as status:
        fig_recibidas = plot_pressure_kde(
            filtered_recibidas,
            team_name=team_for_plot,
            show_zones=True,
            title_suffix=title_suffix,
            title_label="Presiones recibidas"
        )
        status.update(label="Mapa generado", state="complete")

    if fig_recibidas:
        st.pyplot(fig_recibidas, use_container_width=True)
    else:
        st.info("No hay datos suficientes para el mapa.")

with map_col2:
    with st.status("Procesando mapa de presiones realizadas...", expanded=False) as status:
        fig_realizadas = plot_pressure_kde(
            filtered_realizadas,
            team_name=team_for_plot,
            show_zones=True,
            title_suffix=title_suffix,
            title_label="Presiones realizadas"
        )
        status.update(label="Mapa generado", state="complete")

    if fig_realizadas:
        st.pyplot(fig_realizadas, use_container_width=True)
    else:
        st.info("No hay datos suficientes para el mapa.")
