import streamlit as st
import pandas as pd
import numpy as np
from preprocessing import preprocess_data
from utils.plots import plot_goal_kicks, plot_goal_kicks_effectiveness, plot_possession_path
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


# ---------------- Data ----------------

@st.cache_data
def load_data():
    df = pd.read_parquet('preprocessed_SSD_25-26.parquet')
    df = preprocess_data(df)
    # DtGame ya es date tras preprocess_data; Posesion_key ya existe tras normalize_columns
    return df

df_full = load_data()
saques_arco = df_full[df_full['qualifiers'].str.contains('GoalKick', na=False)].copy()

# ---------------- UI ----------------

minute_options = ["0-15", "16-30", "31-45", "46-60", "61-75", "76+"]

with st.expander("Filtros", expanded=True):

    min_date = saques_arco['DtGame'].min()
    max_date = saques_arco['DtGame'].max()
    date_range = st.slider(
        "Selecciona un rango de fechas",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    teams = sorted(saques_arco['TeamName'].dropna().unique())
    team_choice = st.selectbox('Equipo:', ['Todos'] + teams)

    minute_choice = st.multiselect('Minutos:', minute_options, default=minute_options)

    outcome_options = sorted(saques_arco['outcome_type'].dropna().unique()) if 'outcome_type' in saques_arco.columns else []
    outcome_choice = st.multiselect('Outcome:', outcome_options, default=outcome_options)

    if 'estado_partido' in saques_arco.columns:
        if team_choice != 'Todos':
            estado_choice = st.multiselect(
                'Estado:',
                [f'Gana_{team_choice}', 'Empate', 'Pierde'],
                default=[f'Gana_{team_choice}', 'Empate', 'Pierde']
            )
        else:
            estado_choice = st.multiselect(
                'Estado:',
                sorted(saques_arco['estado_partido'].dropna().unique()),
                default=sorted(saques_arco['estado_partido'].dropna().unique())
            )
    else:
        estado_choice = []

# ---------------- Filtros ----------------

filtered = saques_arco.copy()
filtered = filtered[(filtered['DtGame'] >= date_range[0]) & (filtered['DtGame'] <= date_range[1])]
df_no_team = filtered.copy()

if team_choice != 'Todos':
    filtered = filtered[filtered['TeamName'] == team_choice]

filtered = filter_if_selected(filtered, 'outcome_type', outcome_choice)
df_no_team = filter_if_selected(df_no_team, 'outcome_type', outcome_choice)

if minute_choice and set(minute_choice) != set(minute_options):
    filtered   = filtered[parse_minute_ranges(filtered['minute'], minute_choice)]
    df_no_team = df_no_team[parse_minute_ranges(df_no_team['minute'], minute_choice)]

# Estado del partido
def apply_estado_filter(df, team_choice, estado_choice):
    if 'estado_partido' not in df.columns or not estado_choice:
        return df
    ep = df['estado_partido'].astype(str).str.lower().str.strip()
    if team_choice != 'Todos':
        team = team_choice.lower()
        mask = pd.Series(False, index=df.index)
        if f'gana_{team}' in [s.lower() for s in estado_choice]:
            mask |= ep.str.contains('gana') & ep.str.contains(team)
        if 'empate' in [s.lower() for s in estado_choice]:
            mask |= ep == 'empate'
        if 'pierde' in [s.lower() for s in estado_choice]:
            mask |= (~(ep.str.contains('gana') & ep.str.contains(team))) & (ep != 'empate')
        return df[mask]
    else:
        return df[df['estado_partido'].isin(estado_choice)]

filtered   = apply_estado_filter(filtered,   team_choice, estado_choice)
df_no_team = apply_estado_filter(df_no_team, team_choice, estado_choice)

# ---------------- Plots ----------------

st.subheader('Distribución de Saques de Arco')

# Columnas normalizadas: end_x (era endX), Outcome (era outcome_value)
saques_arco_stats = df_no_team.groupby('TeamName', as_index=False).agg(
    end_x=('end_x', 'mean'),
    Outcome=('Outcome', 'sum'),
    n_total=('Outcome', 'count')
)
saques_arco_stats['% de efectividad'] = (
    saques_arco_stats['Outcome'] / saques_arco_stats['n_total'] * 100
)

m_col1, m_col2, m_col3 = st.columns(3)
final_total = int(filtered.shape[0])
m_col1.metric("Total saques de arco", final_total)
distancia_prom = float(filtered['end_x'].mean()) if final_total else 0.0
m_col2.metric("Distancia promedio donde terminan", round(distancia_prom, 2))
efectividad = (
    filtered[filtered['Outcome'] == 1].shape[0] / final_total * 100
    if final_total else 0.0
)
m_col3.metric("% efectividad", round(efectividad, 2))

team_for_plot = None if team_choice == 'Todos' else team_choice

fig_scatter = plot_goal_kicks_effectiveness(saques_arco_stats, team_for_plot)
st.plotly_chart(fig_scatter, use_container_width=True)

st.subheader('Zonas de terminación de saques de arco')

with st.status("Procesando mapa de saques de arco...", expanded=False) as status:
    fig = plot_goal_kicks(filtered, team_name=team_for_plot)
    status.update(label="Mapa generado", state="complete")

if fig:
    st.pyplot(fig, use_container_width=True)
else:
    st.info("No hay datos suficientes para el mapa.")

# ---------------- Visor de posesiones ----------------

st.subheader('Posesiones con saque de arco y remate')

gk_keys = set(filtered['Posesion_key'].dropna().unique())
shot_keys = set(df_full[df_full['xg'].notna() & (df_full['xg'] > 0)]['Posesion_key'].dropna().unique())
qualifying_keys = sorted(gk_keys & shot_keys)

if not qualifying_keys:
    st.info("No hay posesiones con saque de arco y remate para los filtros seleccionados.")
else:
    poss_meta = (
        saques_arco[saques_arco['Posesion_key'].isin(qualifying_keys)]
        .sort_values('time_seconds')
        .groupby('Posesion_key')
        .first()
        .reset_index()
        [['Posesion_key', 'TeamName', 'RivalName', 'DtGame', 'minute']]
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
            f"xG: {row['total_xg']:.2f}"
        )
        for _, row in poss_meta.iterrows()
    }

    selected_key = st.selectbox(
        'Seleccioná una posesión:',
        options=list(poss_labels.keys()),
        format_func=lambda k: poss_labels.get(k, k)
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
