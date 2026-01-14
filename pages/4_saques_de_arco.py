import streamlit as st
import pandas as pd
import numpy as np
from utils.plots import plot_goal_kicks, plot_goal_kicks_effectiveness
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title('Saques de Arco')

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
    df = pd.read_csv('goal_kicks.csv')
    saques_arco = df[df.qualifiers.str.contains('GoalKick') == True]
    saques_arco['DtGame'] = saques_arco['__archivo_origen'].apply(lambda x: x.split(' ')[0])
    team_ids = pd.read_json('team_ids.json')
    # Añadir nombres de equipo
    saques_arco = saques_arco.merge(team_ids, left_on="teamId", right_on="homeTeamId", how="left").drop(columns=["homeTeamId"])
    if 'equipo vs' in saques_arco.columns:
        saques_arco = saques_arco.merge(team_ids, left_on='equipo vs', right_on='homeTeamId', suffixes=['', '_vs']).rename(columns={'homeTeamName_vs': 'equipo_vs_name'}).drop(columns=['homeTeamId'])
    else:
        saques_arco['equipo_vs_name'] = saques_arco.get('homeTeamName', None)
    if 'fecha' not in saques_arco.columns and 'DtGame' in saques_arco.columns:
        saques_arco['fecha'] = pd.to_datetime(saques_arco['DtGame'], errors='coerce').dt.date
    else:
        saques_arco['fecha'] = pd.to_datetime(saques_arco['DtGame'], errors='coerce').dt.date
    saques_arco['estado_partido'] = np.where(
        saques_arco['estado partdo'] == 'Gana Visita',
        'Gana_' + saques_arco['equipo_vs_name'],
        np.where(
            saques_arco['estado partdo'] == 'Gana Local',
            'Gana_' + saques_arco['homeTeamName'],
            'Empate'
        )
    )
    return saques_arco

df = load_and_preprocess_data()

minute_options = ["0-15", "16-30", "31-45", "46-60", "61-75", "76+"]

with st.expander("Filtros", expanded=True):

    min_date, max_date = df['fecha'].min(), df['fecha'].max()
    date_range = st.date_input("Rango de fechas", value=(min_date, max_date))

    teams = sorted(df['equipo_vs_name'].dropna().unique())
    team_choice = st.selectbox('Equipo:', ['Todos'] + teams)

    minute_choice = st.multiselect('Minutos:', minute_options, default=minute_options)

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
    filtered = filtered[filtered['homeTeamName'] == team_choice]

filtered = filter_if_selected(filtered, 'outcome_type', outcome_choice)

if minute_choice and set(minute_choice) != set(minute_options):
    filtered = filtered[parse_minute_ranges(filtered['minute'], minute_choice)]

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

# ---------------- Plots ----------------

st.subheader('Distribución de Saques de Arco')

saques_arco_stats = df.groupby('homeTeamName', as_index=False).agg({'endX':'mean', 'outcome_value':'sum','outcome_type':'count'})
saques_arco_stats['% de efectividad'] = (saques_arco_stats['outcome_value'] / saques_arco_stats['outcome_type']) * 100

m_col1, m_col2, m_col3 = st.columns(3)
final_total = int(filtered.shape[0])
m_col1.metric("Total saques de arco", final_total)
distancia_prom = float(filtered.endX.mean())
m_col2.metric("Distancia promedio donde terminan", round(distancia_prom,2))
efectividad = filtered[filtered['outcome_value'] == 1].shape[0] / filtered.shape[0] * 100
m_col3.metric("% efectividad", round(efectividad,2))

fig = px.scatter(
    saques_arco_stats,
    x='endX',
    y='% de efectividad',
    size_max=100,
    title='Saques de arco: distancia promedio vs efectividad entre los equipos de la liga',
    labels={
        'endX': 'Distancia promedio (m)',
        '% de efectividad': '% de efectividad'
    },
    hover_name='homeTeamName',
    hover_data={
        'endX': True,
        '% de efectividad': True,
        'homeTeamName': False  # ya está en hover_name
    }
)

team_for_plot = None if team_choice == 'Todos' else team_choice

# 👇 Reemplaza todo el if largo por una sola línea
fig_scatter = plot_goal_kicks_effectiveness(saques_arco_stats, team_for_plot)

st.plotly_chart(fig_scatter, use_container_width=True)


st.subheader('Zonas de terminación de saques de arco')

with st.status("Procesando mapa de saques de arco...", expanded=False) as status:
    fig = plot_goal_kicks(
        filtered,
        team_name=team_for_plot  # será None cuando 'Todos' esté seleccionado
    )
    status.update(label="Mapa generado", state="complete")

if fig:
    st.pyplot(fig, use_container_width=True)
else:
    st.info("No hay datos suficientes para el mapa.")