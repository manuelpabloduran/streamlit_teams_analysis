import os
import streamlit as st
import pandas as pd
import numpy as np
from preprocessing import preprocess_data
from utils.plots import plot_throw_ins_map, plot_throw_ins_by_tercio, plot_possession_path
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title('Laterales')

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


# ---------------- Data ----------------

@st.cache_data
def load_data():
    _path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'preprocessed_SSD_25-26.parquet')
    df = pd.read_parquet(_path)
    df = preprocess_data(df)
    return df


df_full = load_data()

laterales = df_full[df_full['qualifiers'].astype(str).str.contains('ThrowIn', na=False)].copy()

# Tercio basado en x (campo atacante normalizado 0→100)
laterales['tercio'] = pd.cut(
    laterales['x'],
    bins=[0, 33.5, 67, 100],
    labels=['Primer tercio', 'Tercio medio', 'Último tercio'],
    include_lowest=True,
)

# ---------------- UI ----------------

minute_options = ["0-15", "16-30", "31-45", "46-60", "61-75", "76+"]

st.markdown("---")
with st.expander("Filtros", expanded=True):

    min_date = laterales['DtGame'].min()
    max_date = laterales['DtGame'].max()
    date_range = st.slider(
        "Seleccioná un rango de fechas",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    col1, col2, col3, col4 = st.columns([2, 2, 2, 2])

    teams = sorted(laterales['TeamName'].dropna().unique())

    with col1:
        team_choice = st.selectbox('Equipo:', ['Todos'] + teams)

    with col2:
        minute_choice = st.multiselect('Minutos:', minute_options, default=minute_options)

    with col3:
        tercio_options = ['Primer tercio', 'Tercio medio', 'Último tercio']
        tercio_choice = st.multiselect('Tercio:', tercio_options, default=tercio_options)

    with col4:
        if 'estado_partido' in laterales.columns:
            estado_opts = sorted(laterales['estado_partido'].dropna().unique())
            estado_choice = st.multiselect('Estado del partido:', estado_opts, default=estado_opts)
        else:
            estado_choice = []

# ---------------- Filtrado ----------------

filtered = laterales.copy()
filtered = filtered[
    (filtered['DtGame'] >= date_range[0]) &
    (filtered['DtGame'] <= date_range[1])
]
df_no_team = filtered.copy()

if team_choice != 'Todos':
    filtered = filtered[filtered['TeamName'] == team_choice]

if tercio_choice and set(tercio_choice) != set(tercio_options):
    filtered   = filtered[filtered['tercio'].isin(tercio_choice)]
    df_no_team = df_no_team[df_no_team['tercio'].isin(tercio_choice)]

if minute_choice and set(minute_choice) != set(minute_options):
    filtered   = filtered[parse_minute_ranges(filtered['minute'], minute_choice)]
    df_no_team = df_no_team[parse_minute_ranges(df_no_team['minute'], minute_choice)]

if estado_choice:
    filtered   = filter_if_selected(filtered,   'estado_partido', estado_choice)
    df_no_team = filter_if_selected(df_no_team, 'estado_partido', estado_choice)

# ---------------- Métricas ----------------

total = int(filtered.shape[0])
efectivos = int((filtered['Outcome'] == 1).sum()) if total else 0
xg_poss_mean = filtered['possession_xg'].mean() if total else 0.0

m1, m2, m3 = st.columns(3)
m1.metric("Total laterales", total)
m2.metric("% lateral completado", f"{efectivos / total * 100:.1f}%" if total else "–")
m3.metric("xG promedio de posesión", f"{xg_poss_mean:.3f}" if total else "–")

# ---------------- Distribución por tercio ----------------

st.subheader("Distribución por tercio")

tercio_counts = (
    filtered['tercio']
    .value_counts()
    .reindex(['Primer tercio', 'Tercio medio', 'Último tercio'], fill_value=0)
)
TERCIO_COLORS = {'Primer tercio': '#E74C3C', 'Tercio medio': '#F1C40F', 'Último tercio': '#2ECC71'}

fig_tercio_pie = go.Figure(go.Pie(
    labels=tercio_counts.index.tolist(),
    values=tercio_counts.values.tolist(),
    marker_colors=[TERCIO_COLORS[t] for t in tercio_counts.index],
    hole=0.4,
    textinfo='label+percent+value',
))
fig_tercio_pie.update_layout(
    height=300,
    margin=dict(l=0, r=0, t=10, b=0),
    showlegend=True,
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
)
st.plotly_chart(fig_tercio_pie, use_container_width=True)

# ---------------- Mapa de laterales ----------------

st.subheader("Mapa de origen de laterales")

team_for_plot = None if team_choice == 'Todos' else team_choice

with st.status("Generando mapa...", expanded=False) as status:
    fig_map = plot_throw_ins_map(filtered, team_name=team_for_plot)
    status.update(label="Mapa generado", state="complete")

if fig_map:
    st.pyplot(fig_map, use_container_width=True)
else:
    st.info("No hay datos suficientes para el mapa.")

# ---------------- Comparativa por equipo ----------------

st.subheader("Comparativa entre equipos por tercio")

fig_count, fig_xg, fig_ef = plot_throw_ins_by_tercio(df_no_team)

if fig_count:
    st.plotly_chart(fig_count, use_container_width=True)
if fig_xg:
    st.plotly_chart(fig_xg, use_container_width=True)
if fig_ef:
    st.plotly_chart(fig_ef, use_container_width=True)

# ---------------- xG de posesión por equipo y tercio ----------------

st.subheader("xG promedio de posesión por tercio (tabla)")

xg_table = (
    df_no_team
    .groupby(['TeamName', 'tercio'])['possession_xg']
    .mean()
    .unstack('tercio')
    .round(3)
    .reindex(columns=['Primer tercio', 'Tercio medio', 'Último tercio'])
)

if team_choice != 'Todos' and team_choice in xg_table.index:
    # Highlight row for selected team
    st.dataframe(
        xg_table.style.highlight_between(
            subset=pd.IndexSlice[[team_choice], :],
            color='#d4edda',
            axis=None,
        ),
        use_container_width=True,
    )
else:
    st.dataframe(xg_table, use_container_width=True)

# ---------------- Visor de posesiones ----------------

st.markdown("---")
st.subheader("Posesiones con lateral y remate")

SHOT_EVENTS = {'Goal', 'SavedShot', 'MissedShots'}

lat_keys  = set(filtered['Posesion_key'].dropna().unique())
shot_keys = set(
    df_full[df_full['NaEventType'].isin(SHOT_EVENTS)]['Posesion_key'].dropna().unique()
)
qualifying_keys = sorted(lat_keys & shot_keys)

if not qualifying_keys:
    st.info("No hay posesiones con lateral y remate para los filtros seleccionados.")
else:
    poss_meta = (
        laterales[laterales['Posesion_key'].isin(qualifying_keys)]
        .sort_values('time_seconds')
        .groupby('Posesion_key')
        .first()
        .reset_index()
        [['Posesion_key', 'TeamName', 'RivalName', 'DtGame', 'minute', 'tercio']]
    )
    xg_by_poss = (
        df_full[df_full['Posesion_key'].isin(qualifying_keys)]
        .groupby('Posesion_key')['xg']
        .sum()
        .reset_index()
        .rename(columns={'xg': 'total_xg'})
    )
    poss_meta = poss_meta.merge(xg_by_poss, on='Posesion_key', how='left')

    poss_labels = {
        row['Posesion_key']: (
            f"{row['TeamName']} vs {row['RivalName']}  |  "
            f"{row['DtGame']}  |  min {row['minute']}  |  "
            f"{row['tercio']}  |  xG: {row['total_xg']:.2f}"
        )
        for _, row in poss_meta.iterrows()
    }

    selected_key = st.selectbox(
        'Seleccioná una posesión:',
        options=list(poss_labels.keys()),
        format_func=lambda k: poss_labels.get(k, k),
    )

    if selected_key:
        df_poss = df_full[df_full['Posesion_key'] == selected_key].copy()
        with st.status("Dibujando posesión...", expanded=False) as status:
            fig_poss = plot_possession_path(df_poss)
            status.update(label="Listo", state="complete")

        if fig_poss:
            st.pyplot(fig_poss, use_container_width=True)
        else:
            st.info("No hay datos suficientes para esta posesión.")
