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
    df = pd.read_csv('laliga2_10-1-26.csv')
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

# ---------------- Filtros ----------------

filtered = df

filtered = filtered[(filtered['fecha'] >= date_range[0]) & (filtered['fecha'] <= date_range[1])]
df_no_team = filtered.copy()
if team_choice != 'Todos':
    filtered = filtered[filtered['equipo_vs_name'] == team_choice]

if intensity_choice != 'Todos':
    filtered = filtered[filtered['intensity'] == intensity_choice]

filtered = filter_if_selected(filtered, 'outcome_type', outcome_choice)

if minute_choice and set(minute_choice) != set(minute_options):
    filtered = filtered[parse_minute_ranges(filtered['minute'], minute_choice)]

if tercio_choice and set(tercio_choice) != set(tercio_options):
    filtered = filtered[parse_tercio(filtered['positionX'], tercio_choice)]

# Estado del partido
if 'estado_partido' in filtered.columns and estado_choice:
    ep = filtered['estado_partido'].astype(str).str.lower().str.strip()

    if team_choice != 'Todos':
        team = team_choice.lower()
        mask = False

        if f'gana_{team}' in [s.lower() for s in estado_choice]:
            mask |= ep.str.contains('gana') & ep.str.contains(team)
        if 'empate' in [s.lower() for s in estado_choice]:
            mask |= ep == 'empate'
        if 'pierde' in [s.lower() for s in estado_choice]:
            mask |= (~(ep.str.contains('gana') & ep.str.contains(team))) & (ep != 'empate')

        filtered = filtered[mask]
    else:
        filtered = filtered[filtered['estado_partido'].isin(estado_choice)]

# ---------------- Resultados ----------------

m_col1, m_col2, m_col3, m_col4 = st.columns(4)
final_total = int(filtered.shape[0])
m_col1.metric("Total presiones", final_total)
alta = filtered[filtered.intensity == 'high'].shape[0] / final_total * 100
m_col2.metric("Presiones altas intensidad", round(alta,2))
media = filtered[filtered.intensity == 'medium'].shape[0] / final_total * 100
m_col3.metric("Presiones media intensidad", round(media,2))
baja = filtered[filtered.intensity == 'low'].shape[0] / final_total * 100
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

fig = px.scatter(
    scatter_df,
    x='shirtNumber_pressures',
    y='shirtNumber_total',
    size_max=100,
    title='Presiones: realizadas vs recibidas entre los equipos de la liga',
    labels={
        'shirtNumber_pressures': 'Presiones realizadas',
        'shirtNumber_total': 'Presiones recibidas'
    },
    hover_name='equipo_vs_name',
    hover_data={
        'shirtNumber_pressures': True,
        'shirtNumber_total': True,
        'equipo_vs_name': False  # ya está en hover_name
    }
)

# 👇 Reemplaza todo el if largo por una sola línea
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

with st.status("Procesando mapa de presiones...", expanded=False) as status:
    fig = plot_pressure_kde(
        filtered,
        filter_col='equipo_vs_name',
        team_name=team_for_plot,
        show_zones=True,
        title_suffix=title_suffix
    )
    status.update(label="Mapa generado", state="complete")

if fig:
    st.pyplot(fig, use_container_width=True)
else:
    st.info("No hay datos suficientes para el mapa.")
