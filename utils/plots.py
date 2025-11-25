import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from mplsoccer import Pitch
import streamlit as st
from scipy.interpolate import make_interp_spline
from collections import defaultdict

# Definición de pasillos_y para plot_team_progression_with_hist
pasillos_y = {
    'Pasillo Central': (40, 60),
    'Pasillo Interior Izquierdo': (60, 80),
    'Pasillo Interior Derecho': (20, 40),
    'Pasillo Exterior Izquierdo': (80, 100),
    'Pasillo Exterior Derecho': (0, 20)
}

def plot_xg_scatter(df):
    """
    Crea un gráfico de dispersión de xG a favor vs xG en contra.
    """
    # Calcular xG a favor por equipo
    xg_favor = df.groupby('TeamName')['xg'].sum().reset_index()
    xg_favor.rename(columns={'xg': 'xG_Favor', 'TeamName': 'Equipo'}, inplace=True)

    # Calcular xG en contra por equipo
    xg_contra = df.groupby('RivalName')['xg'].sum().reset_index()
    xg_contra.rename(columns={'xg': 'xG_Contra', 'RivalName': 'Equipo'}, inplace=True)

    # Unir los dataframes
    df_xg = pd.merge(xg_favor, xg_contra, on='Equipo')

    # Crear el gráfico de dispersión para xG
    fig_xg = px.scatter(df_xg, x='xG_Contra', y='xG_Favor', text='Equipo',
                        title='xG a Favor vs. xG en Contra por Equipo')
    fig_xg.update_traces(textposition='top center')
    return fig_xg

def plot_xgot_scatter(df):
    """
    Crea un gráfico de dispersión de xGOT a favor vs xGOT en contra.
    """
    # Calcular xGOT a favor por equipo
    xgot_favor = df.groupby('TeamName')['xgot'].sum().reset_index()
    xgot_favor.rename(columns={'xgot': 'xGOT_Favor', 'TeamName': 'Equipo'}, inplace=True)

    # Calcular xGOT en contra por equipo
    xgot_contra = df.groupby('RivalName')['xgot'].sum().reset_index()
    xgot_contra.rename(columns={'xgot': 'xGOT_Contra', 'RivalName': 'Equipo'}, inplace=True)

    # Unir los dataframes
    df_xgot = pd.merge(xgot_favor, xgot_contra, on='Equipo')

    # Crear el gráfico de dispersión para xGOT
    fig_xgot = px.scatter(df_xgot, x='xGOT_Contra', y='xGOT_Favor', text='Equipo',
                          title='xGOT a Favor vs. xGOT en Contra por Equipo')
    fig_xgot.update_traces(textposition='top center')
    return fig_xgot

# Visualización con histogramas para un equipo específico
def plot_team_progression_with_hist(df_analisis_progreso, team_name, conteo_inicio, conteo_fin, stats, bins_x=np.linspace(50, 95, 25), bins_y=np.linspace(5, 95, 25)):
    team_events = df_analisis_progreso[
        (df_analisis_progreso['TeamName'] == team_name)
    ]
    if team_events.empty:
        print(f'Sin eventos para {team_name}')
        return None

    y_mean = team_events['y'].mean()
    if np.isnan(y_mean):
        y_mean = 50

    pitch = Pitch(pitch_type='opta', line_zorder=2, pitch_color='#22312b')
    fig, axs = pitch.jointgrid(
        figheight=8,
        left=None,
        bottom=0.07,
        marginal=0.12,
        space=0,
        grid_width=0.9,
        title_height=0,
        axis=False,
        endnote_height=0,
        grid_height=0.82
    )
    fig.set_facecolor('#22312b')
    fig.suptitle(team_name, fontsize=18, color='white', y=0.99)
    ax_pitch = axs['pitch']
    for key in ('top', 'right'):
        ax_aux = axs[key]
        ax_aux.set_facecolor('#22312b')
        ax_aux.tick_params(colors='white', labelsize=10)
        for spine in ax_aux.spines.values():
            spine.set_visible(False)
    axs['left'].axis('off')

    x_hist_data = team_events.loc[team_events['x'] > 50, 'x']
    if x_hist_data.empty:
        x_hist_data = team_events['x']

    sns.histplot(
        x=x_hist_data,
        bins=bins_x,
        ax=axs['top'],
        element='step',
        color='#9f9f9f',
        linewidth=1.5
    )
    sns.histplot(
        y=team_events['y'],
        bins=bins_y,
        ax=axs['right'],
        element='step',
        color='#9f9f9f',
        linewidth=1.5
    )

    axs['top'].set_xlim(0, 105)
    axs['top'].set_ylabel('')
    axs['top'].tick_params(labelbottom=False)

    axs['right'].set_xlabel('')
    axs['right'].tick_params(labelleft=False, labelright=False)
    axs['right'].set_ylim(0, 100)

    pitch.draw(ax=ax_pitch)
    # El nombre del equipo se controla desde la cabecera del gráfico

    avg_pasillos = width = duration = avg_events = np.nan
    if team_name in stats.index:
        team_stats = stats.loc[team_name]
        avg_pasillos = team_stats['avg_pasillos']
        width = team_stats['width']
        duration = team_stats['duration']
        avg_events = team_stats['n_events']

    pasillos_text = f'Pasillos:\n{avg_pasillos:.1f}' if not np.isnan(avg_pasillos) else 'Pasillos:\n-'
    ax_pitch.text(25, 50, pasillos_text, ha='center', va='center', fontsize=15, color='white', alpha=0.9)

    if team_name in conteo_inicio.index:
        counts_inicio = conteo_inicio.loc[team_name]
        max_inicio = counts_inicio.max() or 1
        for pasillo, (y_start, y_end) in pasillos_y.items():
            if pasillo in counts_inicio:
                alpha = counts_inicio[pasillo] / max_inicio if max_inicio else 0
                ax_pitch.add_patch(plt.Rectangle((50, y_start), 25, y_end - y_start, facecolor='blue', alpha=alpha, zorder=1))

    if team_name in conteo_fin.index:
        counts_fin = conteo_fin.loc[team_name]
        max_fin = counts_fin.max() or 1
        for pasillo, (y_start, y_end) in pasillos_y.items():
            if pasillo in counts_fin:
                alpha = counts_fin[pasillo] / max_fin if max_fin else 0
                ax_pitch.add_patch(plt.Rectangle((75, y_start), 25, y_end - y_start, facecolor='red', alpha=alpha, zorder=1))

    if not np.isnan(width):
        y_center = y_mean if not np.isnan(y_mean) else 50
        half_width = width / 2
        y_start = max(0, y_center - half_width)
        y_end = min(100, y_center + half_width)
        ax_pitch.plot([102, 102], [y_start, y_end], color='green', linewidth=15)
        width_label = f"Ancho: {width:.1f} m".replace('.', ',')
        ax_pitch.text(103, y_center, width_label, color='white', fontsize=13, rotation=90, ha='left', va='center')
    if not np.isnan(duration):
        max_duration = stats['duration'].max() if not stats.empty else 0
        scaled_duration = (duration / max_duration) * 80 if max_duration else 0
        ax_pitch.plot([52, 10 + scaled_duration], [-5, -5], color='green', linewidth=20)
    if not np.isnan(avg_events):
        ax_pitch.text(50, -7, f'Acciones Promedio: {avg_events:.1f}', ha='left', va='top', fontsize=14, color='white')

    ax_pitch.set_xlim(0, 105)
    ax_pitch.set_ylim(-10, 110)
    ax_pitch.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
    
    return fig

def plot_offensive_sequences(df_filtrado, team_name):
    """
    Crea un Bumpy Chart de las secuencias ofensivas por pasillos para un equipo específico.
    """

    df_team = df_filtrado[df_filtrado['TeamName'] == team_name].copy()

    if 'pasillo' not in df_team.columns:
        st.error("La columna 'pasillo' no se encontró en los datos.")
        return None

    df_team = df_team.sort_values(by=['Posesion', 'time_seconds'])

    def remove_consecutive_duplicates(seq_list):
        if not seq_list:
            return []
        res = [seq_list[0]]
        for i in range(1, len(seq_list)):
            if seq_list[i] != seq_list[i-1]:
                res.append(seq_list[i])
        return res

    sequences = df_team.groupby('Posesion')['pasillo'].apply(list)
    sequences = sequences[sequences.str.len() > 1]
    sequences_cleaned = sequences.apply(remove_consecutive_duplicates)

    for i, seq in sequences_cleaned.items():
        if len(seq) == 1:
            sequences_cleaned[i] = [seq[0], seq[0]]

    sequence_counts = sequences_cleaned.value_counts()

    if sequence_counts.empty:
        return None

    start_counts = defaultdict(int)
    end_counts = defaultdict(int)

    for seq, count in sequence_counts.items():
        if len(seq) > 0:
            start_counts[seq[0]] += count
            end_counts[seq[-1]] += count

    pasillo_y_map = {
        'Pasillo Exterior Izquierdo': 89.5,
        'Pasillo Interior Izquierdo': 71,
        'Pasillo Central': 50,
        'Pasillo Interior Derecho': 29,
        'Pasillo Exterior Derecho': 10.5
    }

    corridor_colors = {
        'Pasillo Exterior Izquierdo': '#ff6666',
        'Pasillo Interior Izquierdo': '#ffcc66',
        'Pasillo Central': '#ffff66',
        'Pasillo Interior Derecho': '#66ff66',
        'Pasillo Exterior Derecho': '#66ffff'
    }

    pitch = Pitch(pitch_type='opta', pitch_color='#22312b', line_color='white', line_zorder=1)
    fig, ax = pitch.draw(figsize=(15, 10))
    fig.set_facecolor('#22312b')

    for pasillo, y_val in pasillo_y_map.items():
        y_start = y_val - 10.5
        y_end = y_val + 10.5
        ax.fill_between(x=[0, 100], y1=y_start, y2=y_end, color='gray', alpha=0.1, zorder=0)
        
        pasillo_name = pasillo.replace('Pasillo ', '')
        ax.text(48, y_val, pasillo_name, ha='right', va='center', color='white', fontsize=10, alpha=0.7)
        
        start_count = start_counts.get(pasillo, 0)
        ax.text(48, y_val - 5, f'({start_count} inician)', ha='right', va='center', color='white', fontsize=8, alpha=0.7)

        end_count = end_counts.get(pasillo, 0)
        ax.text(102, y_val, f'({end_count} finalizan)', ha='left', va='center', color='white', fontsize=8, alpha=0.7)

    max_count = sequence_counts.max()
    min_count = sequence_counts.min()

    for seq, count in sequence_counts.items():
        if len(seq) < 2:
            continue

        norm_count = np.sqrt((count - min_count) / (max_count - min_count)) if max_count > min_count else 1.0
        
        linewidth = 1 + norm_count * 5
        alpha = 0.3 + norm_count * 0.7

        y_coords = [pasillo_y_map[p] for p in seq]
        x_coords = np.linspace(50, 100, len(seq))
        
        start_pasillo = seq[0]
        line_color = corridor_colors.get(start_pasillo, 'white')

        if len(x_coords) > 2:
            spline = make_interp_spline(x_coords, y_coords, k=2)
            x_smooth = np.linspace(x_coords.min(), x_coords.max(), 200)
            y_smooth = spline(x_smooth)
            ax.plot(x_smooth, y_smooth, color=line_color, linewidth=linewidth, alpha=alpha, zorder=2)
        else:
            ax.plot(x_coords, y_coords, color=line_color, linewidth=linewidth, alpha=alpha, zorder=2)

        ax.scatter(x_coords, y_coords, color=line_color, s=25, alpha=alpha, zorder=3, ec='black', lw=0.5)

    ax.set_title(f'Secuencias Ofensivas por Pasillos - {team_name}', color='white', fontsize=20, pad=20)
    ax.set_xlim(45, 105)
    
    return fig

def plot_player_xg_xgot(df, team_name):
    """
    Crea un gráfico de barras agrupadas de xG y xGOT por jugador para un equipo específico.
    """
    df_equipo = df[df['TeamName'] == team_name]

    if df_equipo.empty:
        st.warning(f"⚠️ No hay datos para el equipo {team_name}.")
        return None

    shot_summary = (
        df_equipo[df_equipo['NaEventType'].isin(['Attempt Saved', 'Miss', 'Post', 'Goal'])]
        .groupby('NaPlayer', as_index=False)
        .agg(
            xg_sum=('xg', 'sum'),
            xgot_sum=('xgot', 'sum'),
            shots=('NaEventType', 'size')
        )
    )

    if shot_summary.empty:
        st.warning(f"⚠️ No hay tiros para {team_name} con los filtros actuales.")
        return None

    shot_summary['player_label'] = (
        shot_summary['NaPlayer'] + ' (' + shot_summary['shots'].astype(int).astype(str) + ' tiros)'
    )

    shot_summary = shot_summary.sort_values('xgot_sum', ascending=True)
    shot_summary = shot_summary[shot_summary['xg_sum'] > 0]

    if shot_summary.empty:
        st.warning(f"⚠️ No hay jugadores con xG > 0 para {team_name}.")
        return None

    fig = go.Figure()

    fig.add_bar(
        name='xG',
        x=shot_summary['xg_sum'],
        y=shot_summary['player_label'],
        orientation='h',
        customdata=np.stack([shot_summary['shots']], axis=-1),
        hovertemplate=(
            'Jugador: %{y}<br>' +
            'xG: %{x:.2f}<br>' +
            'Tiros: %{customdata[0]}<extra></extra>'
        )
    )

    fig.add_bar(
        name='xGOT',
        x=shot_summary['xgot_sum'],
        y=shot_summary['player_label'],
        orientation='h',
        customdata=np.stack([shot_summary['shots']], axis=-1),
        hovertemplate=(
            'Jugador: %{y}<br>' +
            'xGOT: %{x:.2f}<br>' +
            'Tiros: %{customdata[0]}<extra></extra>'
        )
    )

    fig.update_layout(
        barmode='group',
        xaxis_title='Total',
        yaxis_title='Jugador',
        title=f'{team_name} – xG y xGOT por jugador',
        template='plotly_white',
    )

    return fig