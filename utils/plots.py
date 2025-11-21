import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from mplsoccer import Pitch

# Definición de pasillos_y para plot_team_progression_with_hist
pasillos_y = {
    'Carril Central': (40, 60),
    'Pasillo Interior Izquierdo': (60, 80),
    'Pasillo Interior Derecho': (20, 40),
    'Banda Izquierda': (80, 100),
    'Banda Derecha': (0, 20)
}

def plot_shot_map(df):
    fig = px.scatter(
        df,
        x='shot_start_x',
        y='shot_start_y',
        color='shot_outcome_name',
        hover_data=['player_name', 'shot_statsbomb_xg'],
        title='Mapa de Tiros'
    )
    fig.add_shape(
        type='rect',
        x0=120, y0=0, x1=102, y1=80,
        line=dict(color='white')
    )
    fig.add_shape(
        type='rect',
        x0=120, y0=18, x1=114, y1=62,
        line=dict(color='white')
    )
    fig.add_shape(
        type='rect',
        x0=120, y0=30, x1=108, y1=50,
        line=dict(color='white')
    )
    fig.update_layout(
        xaxis_title='Largo del Campo',
        yaxis_title='Ancho del Campo',
        plot_bgcolor='green',
        xaxis=dict(range=[0, 120]),
        yaxis=dict(range=[0, 80])
    )
    return fig

def plot_shot_quality(df):
    fig = px.histogram(
        df,
        x='shot_statsbomb_xg',
        nbins=20,
        title='Distribución de Calidad de Tiro (xG)'
    )
    fig.update_layout(
        xaxis_title='xG (Goles Esperados)',
        yaxis_title='Cantidad de Tiros'
    )
    return fig

def plot_possession_duration(df):
    df_shot = df[df['shot_outcome_name'].notna()]
    fig = px.histogram(
        df_shot,
        x='possession_duration',
        nbins=30,
        title='Distribución de Duración de Posesión con Tiro'
    )
    fig.update_layout(
        xaxis_title='Duración de la Posesión (segundos)',
        yaxis_title='Cantidad de Posesiones'
    )
    return fig

def plot_defensive_actions(df):
    # This is a placeholder for a more complex defensive plot.
    # For now, we will plot the origin of opponent shots.
    fig = px.density_heatmap(
        df,
        x='shot_start_x',
        y='shot_start_y',
        z='shot_statsbomb_xg',
        histfunc='avg',
        title='Mapa de Calor de xG de Tiros del Rival'
    )
    fig.add_shape(
        type='rect',
        x0=0, y0=0, x1=18, y1=80,
        line=dict(color='white')
    )
    fig.add_shape(
        type='rect',
        x0=0, y0=18, x1=6, y1=62,
        line=dict(color='white')
    )
    fig.add_shape(
        type='rect',
        x0=0, y0=30, x1=12, y1=50,
        line=dict(color='white')
    )
    fig.update_layout(
        xaxis_title='Largo del Campo',
        yaxis_title='Ancho del Campo',
        plot_bgcolor='green',
        xaxis=dict(range=[0, 120]),
        yaxis=dict(range=[0, 80])
    )
    return fig

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
def plot_team_progression_with_hist(df_analisis_progreso, team_name, competition_id, conteo_inicio, conteo_fin, stats, bins_x=np.linspace(50, 95, 25), bins_y=np.linspace(5, 95, 25)):
    team_events = df_analisis_progreso[
        (df_analisis_progreso['TeamName'] == team_name) &
        (df_analisis_progreso['IdCompetition'] == competition_id)
    ]
    if team_events.empty:
        print(f'Sin eventos para {team_name} en competición {competition_id}')
        return None

    y_mean = team_events['y'].mean()
    if np.isnan(y_mean):
        y_mean = 50

    pitch = Pitch(pitch_type='opta', line_zorder=2, pitch_color='#22312b')
    fig, axs = pitch.jointgrid(
        figheight=12,
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


