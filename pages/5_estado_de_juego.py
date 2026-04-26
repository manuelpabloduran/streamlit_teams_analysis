import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from preprocessing import normalize_columns

st.set_page_config(layout="wide")
st.title("Estado de Juego")

_PARQUET = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'preprocessed_SSD_25-26.parquet')

STATE_COLORS = {
    'Ganando':   '#2ECC71',
    'Empate':    '#F1C40F',
    'Perdiendo': '#E74C3C',
}
STATE_ORDER = ['Ganando', 'Empate', 'Perdiendo']

# ─── Data ────────────────────────────────────────────────────────────────────

@st.cache_data
def load_data():
    df = pd.read_parquet(_PARQUET)
    df = normalize_columns(df)
    # Filter to actual play periods only
    df = df[df['period_name'].isin(['FirstHalf', 'SecondHalf'])].copy()
    # Ensure DtGame is datetime.date
    df['DtGame'] = pd.to_datetime(
        df['DtGame'].astype(str).str.replace('Z$', '', regex=True), errors='coerce'
    ).dt.date
    return df


df = load_data()

# ─── Filters ─────────────────────────────────────────────────────────────────

st.markdown("---")
with st.expander("Filtros", expanded=True):
    teams = sorted(df['TeamName'].dropna().unique())

    col1, col2, col3, col4 = st.columns([2, 2, 2, 2])

    with col1:
        selected_team = st.selectbox("Equipo", teams)

    with col2:
        all_rivals = sorted(
            df[df['TeamName'] == selected_team]['RivalName'].dropna().unique()
        )
        selected_rivals = st.multiselect("Rival", all_rivals, default=[])

    with col3:
        selected_results = st.multiselect(
            "Resultado del partido",
            options=['Ganó', 'Empató', 'Perdió'],
            default=[],
        )

    with col4:
        selected_periods = st.multiselect(
            "Período",
            options=['Primera mitad', 'Segunda mitad'],
            default=[],
        )

    all_dates = sorted(df[df['TeamName'] == selected_team]['DtGame'].dropna().unique())
    if len(all_dates) >= 2:
        date_range = st.slider(
            "Rango de fechas",
            min_value=all_dates[0],
            max_value=all_dates[-1],
            value=(all_dates[0], all_dates[-1]),
        )
    else:
        date_range = (all_dates[0], all_dates[-1]) if all_dates else (None, None)

# ─── Filter data ─────────────────────────────────────────────────────────────

team_match_ids = df[df['TeamName'] == selected_team]['matchId'].unique()
df_matches = df[df['matchId'].isin(team_match_ids)].copy()

# Apply rival filter
if selected_rivals:
    valid_matches = df_matches[
        (df_matches['TeamName'] == selected_team) &
        (df_matches['RivalName'].isin(selected_rivals))
    ]['matchId'].unique()
    df_matches = df_matches[df_matches['matchId'].isin(valid_matches)].copy()

# Apply date filter
if date_range[0] is not None:
    team_rows = df_matches[df_matches['TeamName'] == selected_team]
    valid_dates = team_rows[
        (team_rows['DtGame'] >= date_range[0]) &
        (team_rows['DtGame'] <= date_range[1])
    ]['matchId'].unique()
    df_matches = df_matches[df_matches['matchId'].isin(valid_dates)].copy()

# Apply resultado final filter
if selected_results:
    # Compute final score per match per team
    final_scores = (
        df_matches.groupby(['matchId', 'TeamName'])
        .agg(gf=('goles_equipo', 'max'), gc=('goles_rival', 'max'))
        .reset_index()
    )
    def _result_label(row):
        if row['gf'] > row['gc']:
            return 'Ganó'
        elif row['gf'] == row['gc']:
            return 'Empató'
        return 'Perdió'
    final_scores['resultado'] = final_scores.apply(_result_label, axis=1)
    team_results = final_scores[final_scores['TeamName'] == selected_team]
    valid_result_matches = team_results[
        team_results['resultado'].isin(selected_results)
    ]['matchId'].unique()
    df_matches = df_matches[df_matches['matchId'].isin(valid_result_matches)].copy()

# Apply period filter
if selected_periods:
    period_map = {'Primera mitad': 'FirstHalf', 'Segunda mitad': 'SecondHalf'}
    period_values = [period_map[p] for p in selected_periods]
    df_matches = df_matches[df_matches['period_name'].isin(period_values)].copy()

df_team = df_matches[df_matches['TeamName'] == selected_team].copy()

# ─── Helpers ─────────────────────────────────────────────────────────────────

_REVERSE_STATE = {'Ganando': 'Perdiendo', 'Perdiendo': 'Ganando', 'Empate': 'Empate'}

SHOT_EVENTS = {'Goal', 'SavedShot', 'MissedShots'}


def compute_state_intervals(df_all, team):
    """
    For each match, build (matchId, date, rival, start_sec, end_sec, state) intervals
    from the team's perspective using goal events as change-points.
    """
    records = []
    match_ids = df_all['matchId'].unique()

    for match_id in match_ids:
        match = df_all[df_all['matchId'] == match_id]
        goals = (
            match[match['NaEventType'] == 'Goal']
            .sort_values('time_seconds')
        )
        match_start = match['time_seconds'].min()
        match_end   = match['time_seconds'].max()

        rival = (
            match[match['TeamName'] == team]['RivalName'].iloc[0]
            if not match[match['TeamName'] == team].empty
            else "?"
        )
        date = (
            match[match['TeamName'] == team]['DtGame'].iloc[0]
            if not match[match['TeamName'] == team].empty
            else None
        )

        prev_time  = match_start
        prev_state = 'Empate'

        for _, goal_row in goals.iterrows():
            t = goal_row['time_seconds']
            duration = max(0, t - prev_time)
            records.append({
                'matchId':      match_id,
                'date':         date,
                'rival':        rival,
                'start_sec':    prev_time,
                'end_sec':      t,
                'duration_sec': duration,
                'estado':       prev_state,
            })
            # Determine new state from team's perspective
            scorer_state = goal_row['estado_partido']
            if goal_row['TeamName'] == team:
                new_state = scorer_state
            else:
                new_state = _REVERSE_STATE.get(scorer_state, 'Empate')

            prev_time  = t
            prev_state = new_state

        # Final segment
        records.append({
            'matchId':      match_id,
            'date':         date,
            'rival':        rival,
            'start_sec':    prev_time,
            'end_sec':      match_end,
            'duration_sec': max(0, match_end - prev_time),
            'estado':       prev_state,
        })

    return pd.DataFrame(records)


# ─── Computations ────────────────────────────────────────────────────────────

intervals_df = compute_state_intervals(df_matches, selected_team)
total_seconds = intervals_df['duration_sec'].sum()

state_summary = (
    intervals_df.groupby('estado')['duration_sec']
    .sum()
    .reindex(STATE_ORDER, fill_value=0)
    .reset_index()
)
state_summary['pct'] = state_summary['duration_sec'] / total_seconds * 100 if total_seconds > 0 else 0
state_summary['minutos'] = state_summary['duration_sec'] / 60

# xG / shots / goals by game state (team's perspective)
shots_team = df_team[df_team['NaEventType'].isin(SHOT_EVENTS)].copy()
xg_by_state = (
    shots_team.groupby('estado_partido')
    .agg(xG=('xg', 'sum'), Tiros=('NaEventType', 'count'), Goles=('isGoal', 'sum'))
    .reindex(STATE_ORDER, fill_value=0)
    .reset_index()
    .rename(columns={'estado_partido': 'estado'})
)
xg_by_state['xG_por_tiro'] = (xg_by_state['xG'] / xg_by_state['Tiros'].replace(0, np.nan)).round(3)
xg_by_state['Conv_%']      = (xg_by_state['Goles'] / xg_by_state['Tiros'].replace(0, np.nan) * 100).round(1)
xg_by_state['xG'] = xg_by_state['xG'].round(2)

# xG against by game state (rival shots when our team is in a state)
# Rival events: TeamName != selected_team, estado_partido reversed
df_rival = df_matches[df_matches['TeamName'] != selected_team].copy()
df_rival['estado_equipo'] = df_rival['estado_partido'].map(_REVERSE_STATE)
shots_rival = df_rival[df_rival['NaEventType'].isin(SHOT_EVENTS)].copy()
xg_against = (
    shots_rival.groupby('estado_equipo')
    .agg(xG_contra=('xg', 'sum'), Tiros_contra=('NaEventType', 'count'), Goles_contra=('isGoal', 'sum'))
    .reindex(STATE_ORDER, fill_value=0)
    .reset_index()
    .rename(columns={'estado_equipo': 'estado'})
)
xg_against['xG_contra'] = xg_against['xG_contra'].round(2)

n_matches = df_matches['matchId'].nunique()

# ─── Layout ──────────────────────────────────────────────────────────────────

st.markdown(f"### {selected_team} — {n_matches} partidos")

# ── KPI row ──────────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)
for col, estado in zip([col1, col2, col3], STATE_ORDER):
    row = state_summary[state_summary['estado'] == estado]
    pct  = row['pct'].values[0]  if len(row) else 0
    mins = row['minutos'].values[0] if len(row) else 0
    color = STATE_COLORS[estado]
    col.markdown(
        f"""
        <div style="background:{color}22;border-left:4px solid {color};
                    padding:12px 16px;border-radius:6px">
          <div style="font-size:0.85rem;color:#888">{estado.upper()}</div>
          <div style="font-size:2rem;font-weight:700;color:{color}">{pct:.1f}%</div>
          <div style="font-size:0.8rem;color:#666">{mins:.0f} min totales</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("---")

# ── Stacked % time bar ────────────────────────────────────────────────────────
fig_pct = go.Figure()
for estado in STATE_ORDER:
    row = state_summary[state_summary['estado'] == estado]
    pct = row['pct'].values[0] if len(row) else 0
    fig_pct.add_trace(go.Bar(
        name=estado,
        x=[pct],
        y=[selected_team],
        orientation='h',
        marker_color=STATE_COLORS[estado],
        text=f"{pct:.1f}%",
        textposition='inside',
        hovertemplate=f"{estado}: {pct:.1f}%<extra></extra>",
    ))
fig_pct.update_layout(
    barmode='stack',
    height=80,
    margin=dict(l=0, r=0, t=0, b=0),
    showlegend=True,
    legend=dict(orientation='h', yanchor='bottom', y=1.1, xanchor='right', x=1),
    xaxis=dict(showticklabels=False, showgrid=False, range=[0, 100]),
    yaxis=dict(showticklabels=False),
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
)
st.plotly_chart(fig_pct, use_container_width=True)

# ── xG por estado ─────────────────────────────────────────────────────────────
st.subheader("xG ofensivo y defensivo por estado de juego")

col_off, col_def = st.columns(2)

with col_off:
    st.markdown("**A favor** (cuando el equipo está en ese estado)")
    fig_xg = go.Figure()
    for metric, label in [('xG', 'xG'), ('Goles', 'Goles')]:
        fig_xg.add_trace(go.Bar(
            name=label,
            x=xg_by_state['estado'],
            y=xg_by_state[metric],
            marker_color=[STATE_COLORS[s] for s in xg_by_state['estado']],
            opacity=0.9 if metric == 'xG' else 0.6,
            text=xg_by_state[metric].round(2),
            textposition='outside',
        ))
    fig_xg.update_layout(
        barmode='overlay',
        height=300,
        margin=dict(l=0, r=0, t=10, b=0),
        showlegend=True,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        yaxis_title='xG / Goles',
    )
    st.plotly_chart(fig_xg, use_container_width=True)

    # Mini stats table
    display = xg_by_state[['estado', 'xG', 'Tiros', 'Goles', 'xG_por_tiro', 'Conv_%']].copy()
    display.columns = ['Estado', 'xG', 'Tiros', 'Goles', 'xG/Tiro', 'Conv %']
    st.dataframe(display.set_index('Estado'), use_container_width=True)

with col_def:
    st.markdown("**En contra** (xG que genera el rival cuando el equipo está en ese estado)")
    fig_xga = go.Figure()
    fig_xga.add_trace(go.Bar(
        name='xG contra',
        x=xg_against['estado'],
        y=xg_against['xG_contra'],
        marker_color=[STATE_COLORS[s] for s in xg_against['estado']],
        opacity=0.85,
        text=xg_against['xG_contra'].round(2),
        textposition='outside',
    ))
    fig_xga.add_trace(go.Bar(
        name='Goles contra',
        x=xg_against['estado'],
        y=xg_against['Goles_contra'],
        marker_color=[STATE_COLORS[s] for s in xg_against['estado']],
        opacity=0.55,
        text=xg_against['Goles_contra'],
        textposition='outside',
    ))
    fig_xga.update_layout(
        barmode='overlay',
        height=300,
        margin=dict(l=0, r=0, t=10, b=0),
        showlegend=True,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        yaxis_title='xG / Goles',
    )
    st.plotly_chart(fig_xga, use_container_width=True)

    display2 = xg_against[['estado', 'xG_contra', 'Tiros_contra', 'Goles_contra']].copy()
    display2.columns = ['Estado', 'xG', 'Tiros', 'Goles']
    st.dataframe(display2.set_index('Estado'), use_container_width=True)

# ── xG normalizado por minuto en ese estado ──────────────────────────────────
st.subheader("xG por cada 90 minutos en ese estado")

xg_norm = xg_by_state.merge(
    state_summary[['estado', 'minutos']], on='estado', how='left'
)
xg_norm['xG_p90'] = (xg_norm['xG'] / xg_norm['minutos'].replace(0, np.nan) * 90).round(2)
xg_against_norm = xg_against.merge(
    state_summary[['estado', 'minutos']], on='estado', how='left'
)
xg_against_norm['xGc_p90'] = (xg_against_norm['xG_contra'] / xg_against_norm['minutos'].replace(0, np.nan) * 90).round(2)

fig_norm = go.Figure()
fig_norm.add_trace(go.Bar(
    name='xG a favor / 90',
    x=xg_norm['estado'],
    y=xg_norm['xG_p90'],
    marker_color=[STATE_COLORS[s] for s in xg_norm['estado']],
    text=xg_norm['xG_p90'],
    textposition='outside',
))
fig_norm.add_trace(go.Bar(
    name='xG en contra / 90',
    x=xg_against_norm['estado'],
    y=xg_against_norm['xGc_p90'],
    marker_color=['#95a5a6'] * len(xg_against_norm),
    text=xg_against_norm['xGc_p90'],
    textposition='outside',
    opacity=0.8,
))
fig_norm.update_layout(
    barmode='group',
    height=320,
    margin=dict(l=0, r=0, t=10, b=0),
    showlegend=True,
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    yaxis_title='xG por 90 min en ese estado',
)
st.plotly_chart(fig_norm, use_container_width=True)

# ── Match timeline ─────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("Timeline por partido")
st.caption("Cada barra representa un partido. El color muestra el estado del equipo minuto a minuto.")

# Build per-match label
match_labels = {}
for match_id in df_matches['matchId'].unique():
    sub = df_matches[df_matches['matchId'] == match_id]
    team_sub = sub[sub['TeamName'] == selected_team]
    if team_sub.empty:
        continue
    rival   = team_sub['RivalName'].iloc[0]
    date    = str(team_sub['DtGame'].iloc[0])
    goals_f = sub[(sub['TeamName'] == selected_team) & (sub['NaEventType'] == 'Goal')].shape[0]
    goals_a = sub[(sub['TeamName'] != selected_team) & (sub['NaEventType'] == 'Goal')].shape[0]
    match_labels[match_id] = f"{date} vs {rival} ({goals_f}-{goals_a})"

# Sort matches by date
sorted_match_ids = sorted(
    match_labels.keys(),
    key=lambda m: str(df_matches[df_matches['matchId'] == m]['DtGame'].iloc[0]),
)

fig_timeline = go.Figure()

for i, match_id in enumerate(sorted_match_ids):
    label = match_labels.get(match_id, match_id)
    match_ivls = intervals_df[intervals_df['matchId'] == match_id].copy()

    if match_ivls.empty:
        continue

    # Convert seconds to minutes for display
    match_ivls['start_min'] = match_ivls['start_sec'] / 60
    match_ivls['dur_min']   = match_ivls['duration_sec'] / 60

    for _, row in match_ivls.iterrows():
        if row['dur_min'] <= 0:
            continue
        color = STATE_COLORS.get(row['estado'], '#888')
        fig_timeline.add_trace(go.Bar(
            x=[row['dur_min']],
            y=[label],
            base=[row['start_min']],
            orientation='h',
            marker_color=color,
            showlegend=False,
            hovertemplate=(
                f"{label}<br>"
                f"Estado: {row['estado']}<br>"
                f"Desde: {row['start_min']:.0f}' hasta {(row['start_min']+row['dur_min']):.0f}'<br>"
                f"Duración: {row['dur_min']:.0f} min"
                "<extra></extra>"
            ),
        ))

    # Overlay goal markers
    match_goals_team = df_matches[
        (df_matches['matchId'] == match_id) &
        (df_matches['NaEventType'] == 'Goal') &
        (df_matches['TeamName'] == selected_team)
    ]
    match_goals_rival = df_matches[
        (df_matches['matchId'] == match_id) &
        (df_matches['NaEventType'] == 'Goal') &
        (df_matches['TeamName'] != selected_team)
    ]

    if not match_goals_team.empty:
        fig_timeline.add_trace(go.Scatter(
            x=match_goals_team['time_seconds'] / 60,
            y=[label] * len(match_goals_team),
            mode='markers',
            marker=dict(symbol='triangle-up', size=12, color='white', line=dict(color='black', width=1.5)),
            showlegend=False,
            hovertemplate="Gol de " + selected_team + " min %{x:.0f}'<extra></extra>",
        ))

    if not match_goals_rival.empty:
        fig_timeline.add_trace(go.Scatter(
            x=match_goals_rival['time_seconds'] / 60,
            y=[label] * len(match_goals_rival),
            mode='markers',
            marker=dict(symbol='triangle-down', size=12, color='black', line=dict(color='white', width=1.5)),
            showlegend=False,
            hovertemplate="Gol rival min %{x:.0f}'<extra></extra>",
        ))

# Legend patches
for estado, color in STATE_COLORS.items():
    fig_timeline.add_trace(go.Bar(
        x=[None], y=[None], orientation='h',
        name=estado, marker_color=color, showlegend=True,
    ))
fig_timeline.add_trace(go.Scatter(
    x=[None], y=[None], mode='markers',
    marker=dict(symbol='triangle-up', size=12, color='white', line=dict(color='black', width=1.5)),
    name='Gol propio', showlegend=True,
))
fig_timeline.add_trace(go.Scatter(
    x=[None], y=[None], mode='markers',
    marker=dict(symbol='triangle-down', size=12, color='black', line=dict(color='white', width=1.5)),
    name='Gol rival', showlegend=True,
))

n_matches_visible = len(sorted_match_ids)
fig_timeline.update_layout(
    barmode='overlay',
    height=max(400, n_matches_visible * 32 + 80),
    margin=dict(l=0, r=0, t=10, b=30),
    xaxis=dict(title="Minuto", range=[0, None], dtick=10),
    yaxis=dict(autorange='reversed'),
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    legend=dict(orientation='h', yanchor='bottom', y=1.01, xanchor='right', x=1),
)

st.plotly_chart(fig_timeline, use_container_width=True)
