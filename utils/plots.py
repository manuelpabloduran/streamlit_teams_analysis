import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from mplsoccer import Pitch, VerticalPitch
import streamlit as st
from scipy.interpolate import make_interp_spline
from collections import defaultdict
import matplotlib.patheffects as pe
from matplotlib.lines import Line2D
import matplotlib.patheffects as path_effects

# Definición de pasillos_y para plot_team_progression_with_hist
pasillos_y = {
    'Pasillo Central': (40, 60),
    'Pasillo Interior Izquierdo': (60, 80),
    'Pasillo Interior Derecho': (20, 40),
    'Pasillo Exterior Izquierdo': (80, 100),
    'Pasillo Exterior Derecho': (0, 20)
}

zone_areas_full = {
    'zone_1':{
        'y_lower_bound': 78.9, 'y_upper_bound': 100,
        'x_lower_bound': 83, 'x_upper_bound': 100,
    },
    'zone_2':{
        'y_lower_bound': 0, 'y_upper_bound': 21.1,
        'x_lower_bound': 83, 'x_upper_bound': 100,
    },
    'zone_3':{
        'y_lower_bound': 78.9, 'y_upper_bound': 100,
        'x_lower_bound': 66.5, 'x_upper_bound': 83,
    },
    'zone_4':{
        'y_lower_bound': 0, 'y_upper_bound': 21.1,
        'x_lower_bound': 66.5, 'x_upper_bound': 83,
    },
    'zone_5':{
        'y_lower_bound': 21.1, 'y_upper_bound': 36.8,
        'x_lower_bound': 83, 'x_upper_bound': 100,
    },
    'zone_6':{
        'y_lower_bound': 63.2, 'y_upper_bound': 78.9,
        'x_lower_bound': 83, 'x_upper_bound': 100,
    },
    'zone_7':{
        'y_lower_bound': 36.8, 'y_upper_bound': 63.2,
        'x_lower_bound': 83, 'x_upper_bound': 100,
    },
    'zone_8':{
        'y_lower_bound': 36.8, 'y_upper_bound': 63.2,
        'x_lower_bound': 66.5, 'x_upper_bound': 83,
    },
    'zone_9':{
        'y_lower_bound': 21.1, 'y_upper_bound': 36.8,
        'x_lower_bound': 66.5, 'x_upper_bound': 83,
    },
    'zone_10':{
        'y_lower_bound': 63.2, 'y_upper_bound': 78.9,
        'x_lower_bound': 66.5, 'x_upper_bound': 83,
    },
    'zone_11':{
        'y_lower_bound': 36.8, 'y_upper_bound': 63.2,
        'x_lower_bound': 66.5, 'x_upper_bound': 83,
    },
    'zone_12':{
        'y_lower_bound': 78.9, 'y_upper_bound': 100,
        'x_lower_bound': 50, 'x_upper_bound': 66.5,
    },
    'zone_13':{
        'y_lower_bound': 0, 'y_upper_bound': 21.1,
        'x_lower_bound': 50, 'x_upper_bound': 66.5,
    },
    'zone_14':{
        'y_lower_bound': 21.1, 'y_upper_bound': 36.8,
        'x_lower_bound': 50, 'x_upper_bound': 66.5,
    },
    'zone_15':{
        'y_lower_bound': 36.8, 'y_upper_bound': 63.2,
        'x_lower_bound': 50, 'x_upper_bound': 66.5,
    },
    'zone_16':{
        'y_lower_bound': 63.2, 'y_upper_bound': 78.9,
        'x_lower_bound': 50, 'x_upper_bound': 66.5,
    },
    'zone_17':{
        'y_lower_bound': 0, 'y_upper_bound': 21.1,
        'x_lower_bound': 33.5, 'x_upper_bound': 50,
    },
    'zone_18':{
        'y_lower_bound': 21.1, 'y_upper_bound': 36.8,
        'x_lower_bound': 33.5, 'x_upper_bound': 50,
    },
    'zone_19':{
        'y_lower_bound': 36.8, 'y_upper_bound': 63.2,
        'x_lower_bound': 33.5, 'x_upper_bound': 50,
    },
    'zone_20':{
        'y_lower_bound': 63.2, 'y_upper_bound': 78.9,
        'x_lower_bound': 33.5, 'x_upper_bound': 50,
    },
    'zone_21':{
        'y_lower_bound': 78.9, 'y_upper_bound': 100,
        'x_lower_bound': 33.5, 'x_upper_bound': 50,
    },
    'zone_22': {'y_lower_bound': 0,    'y_upper_bound': 21.1, 'x_lower_bound': 0,     'x_upper_bound': 16.75},
    'zone_23': {'y_lower_bound': 0,    'y_upper_bound': 21.1, 'x_lower_bound': 16.75, 'x_upper_bound': 33.5},

    'zone_24': {'y_lower_bound': 21.1, 'y_upper_bound': 36.8, 'x_lower_bound': 0,     'x_upper_bound': 16.75},
    'zone_25': {'y_lower_bound': 21.1, 'y_upper_bound': 36.8, 'x_lower_bound': 16.75, 'x_upper_bound': 33.5},

    'zone_26': {'y_lower_bound': 36.8, 'y_upper_bound': 63.2, 'x_lower_bound': 0,     'x_upper_bound': 16.75},
    'zone_27': {'y_lower_bound': 36.8, 'y_upper_bound': 63.2, 'x_lower_bound': 16.75, 'x_upper_bound': 33.5},

    'zone_28': {'y_lower_bound': 63.2, 'y_upper_bound': 78.9, 'x_lower_bound': 0,     'x_upper_bound': 16.75},
    'zone_29': {'y_lower_bound': 63.2, 'y_upper_bound': 78.9, 'x_lower_bound': 16.75, 'x_upper_bound': 33.5},

    'zone_30': {'y_lower_bound': 78.9, 'y_upper_bound': 100,  'x_lower_bound': 0,     'x_upper_bound': 16.75},
    'zone_31': {'y_lower_bound': 78.9, 'y_upper_bound': 100,  'x_lower_bound': 16.75, 'x_upper_bound': 33.5},
}

def assign_shot_zone_press(x,y):
    '''
    This function returns the zone based on the x & y coordinates of the shot
    taken.
    Args:
        - x (float): the x position of the shot based on a vertical grid.
        - y (float): the y position of the shot based on a vertical grid.
    '''

    global zone_areas_full

    # Conditions

    for zone in zone_areas_full:
        if (x >= zone_areas_full[zone]['x_lower_bound']) & (x <= zone_areas_full[zone]['x_upper_bound']):
            if (y >= zone_areas_full[zone]['y_lower_bound']) & (y <= zone_areas_full[zone]['y_upper_bound']):
                return zone

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
def plot_team_progression_with_hist(df_analisis_progreso, team_name, conteo_inicio, conteo_fin, stats, filter_col='TeamName', bins_x=np.linspace(50, 95, 25), bins_y=np.linspace(5, 95, 25)):
    team_events = df_analisis_progreso[
        (df_analisis_progreso[filter_col] == team_name)
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


def plot_pressure_kde(df, filter_col=None, team_name=None, cmap='OrRd', levels=100, fill=True, bandwidth=None, scatter_on_fail=True, show_zones=True, facecolor="#EFE9E6", zone_color="#ab2a3e", title_suffix=''):
    """
    Plotea un mapa de densidad (KDE) de las posiciones de presión usando mplsoccer.Pitch.

    Ahora incluye la rejilla por zonas (como en `test.ipynb`) y rellena cada zona
    proporcionalmente al número de presiones que cayeron en ella.

    Parámetros adicionales:
    - show_zones: si True rellena las zonas definidas en `zone_areas` con alpha proporcional.
    - facecolor: color de fondo de la cancha (p.ej. '#EFE9E6').
    - zone_color: color base para el relleno de zonas.
    """
    if df is None or df.empty:
        return None

    df_plot = df.copy()
    if team_name and filter_col:
        df_plot = df_plot[df_plot[filter_col] == team_name]

    if df_plot.empty:
        return None

    # Asegurar que ambas columnas existan
    if 'positionX' not in df_plot.columns or 'positionY' not in df_plot.columns:
        return None

    # Drop rows with NA in either positionX or positionY so x and y align
    df_plot = df_plot.dropna(subset=['positionX', 'positionY']).copy()

    if df_plot.empty:
        return None

    x = pd.to_numeric(df_plot['positionX'], errors='coerce')
    y = pd.to_numeric(df_plot['positionY'], errors='coerce')

    mask = x.notna() & y.notna()
    x = x[mask]
    y = y[mask]

    if x.empty or y.empty:
        return None

    # Compute zone membership if needed
    zones_series = df_plot.apply(lambda r: assign_shot_zone_press(r['positionX'], r['positionY']), axis=1)
    df_plot = df_plot.assign(_zone=zones_series.values)

    pitch = Pitch(pitch_type='opta')
    fig, ax = pitch.draw(figsize=(8, 6))
    ax.set_facecolor(facecolor)

    # dibujar cortes y líneas de zona (misma estética que ejemplo)
    ax.plot([16.75, 16.75], [0, 100], ls=':', color='black')   # nuevo corte banda izquierda
    ax.plot([33.5, 33.5], [0, 100], ls='-', lw=2, color='black')
    ax.plot([50, 50], [0, 100], ls=':', color='black')
    ax.plot([66.5, 66.5], [0, 100], ls=':', color='black')
    ax.plot([83, 83], [0, 100], ls=':', color='black')

    ax.plot([33.5, 100], [21.1,21.1], ls=':', color='black')
    ax.plot([33.5, 100], [36.8,36.8], ls=':', color='black')
    ax.plot([33.5, 100], [63.2,63.2], ls=':', color='black')
    ax.plot([33.5, 100], [78.9,78.9], ls=':', color='black')

    # Try to draw KDE in the background
    plotted_kde = False
    kde_kwargs = {'levels': levels, 'fill': fill, 'zorder': -1, 'thresh': 0}
    if bandwidth is not None:
        kde_kwargs['bw_method'] = bandwidth

    try:
        pitch.kdeplot(x, y, ax=ax, cmap=cmap, **kde_kwargs)
        plotted_kde = True
    except Exception:
        try:
            sns.kdeplot(x=x, y=y, ax=ax, cmap=cmap, fill=fill, levels=levels)
            plotted_kde = True
        except Exception:
            plotted_kde = False

    # If KDE failed, show scatter points as fallback
    if not plotted_kde and scatter_on_fail:
        ax.scatter(x, y, c='red', s=18, alpha=0.6, zorder=1)

    # If requested, fill zones proportionally
    if show_zones:
        # count per zone
        counts = df_plot['_zone'].value_counts()
        if not counts.empty:
            max_value = counts.max()
            for zone in zone_areas_full:
                if zone in counts.index:
                    shot_count = counts[zone]
                    shot_pct = shot_count / max_value if max_value else 0
                    x_lim = [zone_areas_full[zone]['x_lower_bound'], zone_areas_full[zone]['x_upper_bound']]
                    y1 = zone_areas_full[zone]['y_lower_bound']
                    y2 = zone_areas_full[zone]['y_upper_bound']
                    ax.fill_between(
                        x=x_lim,
                        y1=y1, y2=y2,
                        color=zone_color, alpha=(shot_pct),
                        zorder=0, ec='None')

                    # text styling similar to example
                    if shot_pct > 0.075:
                        color_text = 'white'
                        fore_color ='black'
                    else:
                        color_text = 'black'
                        fore_color = 'white'

                    if shot_pct > 0.025:
                        x_pos = x_lim[0] + abs(x_lim[0] - x_lim[1]) / 2
                        y_pos = y1 + abs(y1 - y2) / 2
                        text_ = ax.annotate(
                            xy=(x_pos, y_pos),
                            text=f'{shot_count}',
                            ha='center',
                            va='center',
                            color=color_text,
                            weight='bold',
                            size=10
                        )
                        text_.set_path_effects([pe.Stroke(linewidth=1.5, foreground=fore_color), pe.Normal()])

    # Title
    title = "Mapa de Presiones"
    if team_name:
        title += f" - {team_name}"
    if title_suffix:
        title += f" {title_suffix}"
    try:
        DC_to_FC = ax.transData.transform
        FC_to_NFC = fig.transFigure.inverted().transform
        DC_to_NFC = lambda x: FC_to_NFC(DC_to_FC(x))
        title_x, title_y = DC_to_NFC((50, 108))
        fig.text(title_x, title_y, title, ha='center', va='center', fontsize=16)
    except Exception:
        fig.suptitle(title, fontsize=16)

    # Ajustes visuales
    ax.set_xlim(0, 105)
    ax.set_ylim(-5, 105)

    # Invertir eje X

    # Dirección de juego (flecha)
    ax.annotate(
        'Dirección de juego',
        xy=(70, -3),
        xytext=(90, -3),
        arrowprops=dict(
            arrowstyle='->',
            lw=2,
            color='black'
        ),
        ha='center',
        va='center',
        fontsize=10,
        color='black',
        zorder=5
    )

    ax.invert_xaxis()

    return fig

def highlight_team_scatter(scatter_df, team_choice):
    fig = px.scatter(
        scatter_df,
        x='shirtNumber_pressures',
        y='shirtNumber_total',
        size_max=100,
        title='Presiones: realizadas vs recibidas',
        labels={
            'shirtNumber_pressures': 'Presiones realizadas',
            'shirtNumber_total': 'Presiones recibidas'
        },
        hover_name='homeTeamName',
        hover_data={
            'shirtNumber_pressures': True,
            'shirtNumber_total': True,
            'equipo_vs_name': False
        }
    )

    fig.update_traces(
        hovertemplate=
            "<b>%{hovertext}</b><br>" +
            "Presiones realizadas: %{x}<br>" +
            "Presiones recibidas: %{y}<extra></extra>"
    )

    if team_choice == 'Todos':
        return fig

    fig.update_traces(
        selector=dict(mode='markers'),
        marker=dict(opacity=0.3)
    )

    df_team = scatter_df[scatter_df['equipo_vs_name'] == team_choice]

    if df_team.empty:
        return fig

    fig.add_trace(
        go.Scatter(
            x=df_team['shirtNumber_pressures'],
            y=df_team['shirtNumber_total'],
            mode='markers',
            name=team_choice,
            text=df_team['equipo_vs_name'],
            hovertemplate=
                "<b>%{text}</b><br>" +
                "Presiones realizadas: %{x}<br>" +
                "Presiones recibidas: %{y}<extra></extra>",
            marker=dict(
                size=16,
                color='red',
                opacity=0.9,
                line=dict(width=1, color='black')
            )
        )
    )

    x_ref = scatter_df['shirtNumber_pressures'].mean()
    y_ref = scatter_df['shirtNumber_total'].mean()

    fig.add_vline(
        x=x_ref,
        line_width=2,
        line_dash="dash",
        line_color="gray",
        annotation_text="Prom. presiones realizadas",
        annotation_position="top"
    )

    fig.add_hline(
        y=y_ref,
        line_width=2,
        line_dash="dash",
        line_color="gray",
        annotation_text="Prom. presiones recibidas",
        annotation_position="right"
    )

    return fig

def plot_goal_kicks(saques_arco, team_name, facecolor="#EFE9E6"):

    saques_arco['zone_area'] = [assign_shot_zone_press(x,y) for x,y in zip(saques_arco['endX'], saques_arco['endY'])]
    data = saques_arco.groupby(['homeTeamName', 'zone_area']).apply(lambda x: x.shape[0]).reset_index()
    data.rename(columns={0:'num_shots'}, inplace=True)
    total_shots = data.groupby(['homeTeamName'])['num_shots'].sum().reset_index()
    total_shots.rename(columns={'num_shots':'total_shots'}, inplace=True)

    data = pd.merge(data, total_shots, on='homeTeamName', how='left')
    data['pct_shots'] = data['num_shots']/data['total_shots']

    pitch = Pitch(pitch_type='opta')
    fig, ax = pitch.draw(figsize=(8, 6))
    ax.set_facecolor(facecolor)

    ax.set_facecolor(facecolor)
    ax.plot([16.75, 16.75], [0, 100], ls=':', color='black')   # nuevo corte banda izquierda
    ax.plot([33.5, 33.5], [0, 100], ls='-', lw=2, color='black')
    ax.plot([50, 50], [0, 100], ls=':', color='black')
    ax.plot([66.5, 66.5], [0, 100], ls=':', color='black')
    ax.plot([83, 83], [0, 100], ls=':', color='black')

    ax.plot([33.5, 100], [21.1,21.1], ls=':', color='black')
    ax.plot([33.5, 100], [36.8,36.8], ls=':', color='black')
    ax.plot([33.5, 100], [63.2,63.2], ls=':', color='black')
    ax.plot([33.5, 100], [78.9,78.9], ls=':', color='black')
    # soportar caso: todos los equipos
    if team_name is None:
        plot_df = data.groupby('zone_area').agg({'num_shots':'sum','total_shots':'sum'}).reset_index()
        plot_df['pct_shots'] = plot_df['num_shots'] / plot_df['total_shots']
    else:
        plot_df = data[data['homeTeamName'] == team_name].reset_index(drop=True)
    
    # si no hay datos, devolver None para que la página muestre mensaje apropiado
    if plot_df.empty:
        return None
    
    print(plot_df)

    max_value = plot_df['pct_shots'].max()
    
    for zone in plot_df['zone_area']:
        shot_pct = plot_df[plot_df['zone_area'] == zone]['pct_shots'].iloc[0]
        x_lim = [zone_areas_full[zone]['x_lower_bound'], zone_areas_full[zone]['x_upper_bound']]
        y1 = zone_areas_full[zone]['y_lower_bound']
        y2 = zone_areas_full[zone]['y_upper_bound']
        ax.fill_between(
            x=x_lim, 
            y1=y1, y2=y2, 
            color='#ab2a3e', alpha=(shot_pct/max_value),
            zorder=0, ec='None')
        if shot_pct > 0.075:
                color_text = 'white'
                fore_color ='black'
        else:
                color_text = 'black'
                fore_color = 'white'
        if shot_pct > 0.015:
            x_pos = x_lim[0] + abs(x_lim[0] - x_lim[1])/2
            y_pos = y1 + abs(y1 - y2)/2
            text_ = ax.annotate(
                xy=(x_pos, y_pos),
                text=f'{shot_pct:.0%}',
                ha='center',
                va='center',
                color=color_text,
                weight='bold',
                size=12
            )
            text_.set_path_effects(
                [path_effects.Stroke(linewidth=1.5, foreground=fore_color), path_effects.Normal()]
            )
    
    ax.text(50, 108, team_name,
            ha='center', va='center', fontsize=24)
    
    # -- Transformation functions
    DC_to_FC = ax.transData.transform
    FC_to_NFC = fig.transFigure.inverted().transform
    # -- Take data coordinates and transform them to normalized figure coordinates
    DC_to_NFC = lambda x: FC_to_NFC(DC_to_FC(x))
    ax_coords = DC_to_NFC((12,101))
    ax_size = 0.1

    return fig


def plot_goal_kicks_effectiveness(saques_arco, team_name=None):
    """Genera un scatter donde X = distancia promedio de terminación (endX)
    y Y = % de efectividad por equipo para saques de arco.

    Parámetros:
    - saques_arco: DataFrame con al menos las columnas `endX` y `outcome_value` (o `outcome_type`).
    - team_name: nombre de equipo para resaltar (opcional). Si es `None` o 'Todos', muestra todos.

    Devuelve: figura plotly o None si no hay datos.
    """

    if saques_arco is None or saques_arco.empty:
        return None

    df = saques_arco.copy()

    # Normalizar team_name cuando viene como 'Todos'
    if team_name == 'Todos':
        team_name = None

    # Determinar columna de equipo disponible
    if 'homeTeamName' in df.columns:
        team_col = 'homeTeamName'
    elif 'teamName' in df.columns:
        team_col = 'teamName'
    else:
        # no hay columna de equipo
        return None

    # Asegurar columnas necesarias
    if 'endX' not in df.columns:
        return None

    if 'outcome_value' not in df.columns:
        # intentar inferir outcome_value a partir de outcome_type (Goal = 1)
        if 'outcome_type' in df.columns:
            df['outcome_value'] = np.where(df['outcome_type'] == 'Goal', 1, 0)
        else:
            df['outcome_value'] = 0

    print("teamCol", team_col)

    # Preparar la figura
    fig = px.scatter(
        df,
        x='endX',
        y='% de efectividad',
        size='outcome_type',
        hover_name=team_col,
        hover_data={
            'endX': ':.2f',
            '% de efectividad': ':.2f',
            'outcome_type': True,
            team_col: False
        },
        labels={
            'endX': 'Distancia promedio de terminación',
            '% de efectividad': '% de efectividad',
            'outcome_type': 'Total saques'
        },
        title='Saques de Arco — Distancia vs % de efectividad'
    )

    fig.update_traces(marker=dict(opacity=0.7, line=dict(width=0.5, color='black')))

    # Resaltar equipo si se indica
    if team_name:
        if team_name in df[team_col].values:
            others = df[df[team_col] != team_name]
            sel = df[df[team_col] == team_name]
            # atenuar otros
            fig.update_traces(selector=dict(mode='markers'), marker=dict(opacity=0.25))
            # añadir traza destacada
            fig.add_trace(
                go.Scatter(
                    x=sel['endX'],
                    y=sel['% de efectividad'],
                    mode='markers+text',
                    text=team_name,
                    textposition='top center',
                    marker=dict(size=sel['outcome_type'] / 4, color='red', opacity=0.95, line=dict(width=1, color='black')),
                    hoverinfo='text'
                )
            )
    fig.update_xaxes(title_text='Distancia promedio de terminación (m)')
    fig.update_yaxes(title_text='% de efectividad')

    x_ref = df['endX'].mean()
    y_ref = df['% de efectividad'].mean()

    fig.add_vline(
        x=x_ref,
        line_width=2,
        line_dash="dash",
        line_color="gray",
        annotation_text="Prom. distancia",
        annotation_position="top"
    )

    fig.add_hline(
        y=y_ref,
        line_width=2,
        line_dash="dash",
        line_color="gray",
        annotation_text="Prom. saques totales",
        annotation_position="right"
    )

    return fig


def plot_offensive_sequences(df_filtrado, team_name, filter_col='TeamName'):
    """
    Crea un Bumpy Chart de las secuencias ofensivas por pasillos para un equipo específico.
    """

    df_team = df_filtrado[df_filtrado[filter_col] == team_name].copy()

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

def plot_player_xg_xgot(df, team_name, filter_col='TeamName'):
    """
    Crea un gráfico de barras agrupadas de xG y xGOT por jugador para un equipo específico.
    """
    df_equipo = df[df[filter_col] == team_name]

    if df_equipo.empty:
        st.warning(f"⚠️ No hay datos para el equipo {team_name}.")
        return None

    shot_summary = (
        df_equipo[(df_equipo['NaEventType'].isin(['Attempt Saved', 'Miss', 'Post', 'Goal']))]
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
        height=max(400, 25 * len(shot_summary))  # 25 px por jugador aprox
    )

    # Forzar que se vean todas las etiquetas del eje Y
    fig.update_yaxes(
        tickmode='linear',
        dtick=1,          # un tick por categoría
        automargin=True   # deja margen para que entren los nombres largos
)

    return fig

import plotly.express as px
import streamlit as st

def plot_goals_sunburst(
    df,
    team_name="Racing de Santander",
    filter_col='TeamName',
    metric='goals',  # 'goals', 'shots' o 'xg_sum'
    shot_events=None,
    xg_col='xg'
):
    """
    Sunburst por tipo de jugada, ubicación y parte del cuerpo (en español),
    con opción de:
      - goals  -> nº de goles
      - shots  -> nº de tiros totales (Attempt Saved, Miss, Post, Goal)
      - xg_sum -> suma de xG

    Devuelve: fig, df_filtrado
    """
    # --- Valores por defecto ---
    if shot_events is None:
        shot_events = ['Attempt Saved', 'Miss', 'Post', 'Goal']

    # --- Filtro base por equipo y que no sea gol en propia puerta ---
    base_mask = (df[filter_col] == team_name) & (df['own_goal'] != -1) & (~df['xg'].isna())

    if metric == 'goals':
        df_sub = df[base_mask & (df['NaEventType'] == 'Goal')].copy()
        valor_label = "Goles"
        titulo_metric = "Goles"
    elif metric == 'shots':
        df_sub = df[base_mask & (df['NaEventType'].isin(shot_events))].copy()
        valor_label = "Tiros"
        titulo_metric = "Tiros totales"
    elif metric == 'xg_sum':
        df_sub = df[base_mask & (df['NaEventType'].isin(shot_events))].copy()
        valor_label = "xG"
        titulo_metric = "xG acumulado"
    else:
        st.error("❌ 'metric' debe ser 'goals', 'shots' o 'xg_sum'.")
        return None

    if df_sub.empty:
        st.warning(f"⚠️ No hay eventos para {team_name} con el filtro seleccionado ({titulo_metric}).")
        return None

    # --- Diccionarios de mapeo a español ---
    play_type_map = {
        "Regular_play": "Jugada Regular",
        "Set_piece": "Balón parado",
        "Penalty": "Penalti",
        "Fast_break": "Transición rápida",
        "From_corner": "Corner",
        "Free_kick": "Balón parado",
        "Throw-in_set_piece": "Saque de banda"
    }

    shot_location_map = {
        "Box": "Área",
        "Small_box": "Área Pequeña",
        "Out_of_box": "Fuera del área"
    }

    shot_part_map = {
        "Right_footed": "Pie derecho",
        "Left_footed": "Pie izquierdo",
        "Head": "Cabeza",
        "Other Body Part": "Otro",
    }

    # 🎨 Colores FIJOS por tipo de jugada (en español)
    play_type_colors = {
        "Jugada Regular":   "#00A651",  # verde Racing
        "Balón parado":     "#F5C242",  # dorado/amarillo
        "Penalti":          "#E53935",  # rojo
        "Transición rápida":"#1E88E5",  # azul
        "Corner":           "#8E24AA",  # violeta
        "Saque de banda":   "#757575",  # gris
    }

    required_cols = ['play_type', 'possession_type', 'shot_location']
    if not all(col in df_sub.columns for col in required_cols):
        st.error(f"El dataframe no contiene las columnas necesarias: {required_cols}")
        return None

    if metric == 'xg_sum' and xg_col not in df_sub.columns:
        st.error(f"El dataframe no contiene la columna de xG especificada: '{xg_col}'")
        return None

    # --- Crear columnas "lindas" en español ---
    def _nice(col, mapping):
        # 1) aplicar diccionario
        # 2) si no existe en dict, reemplazar "_" por espacio y capitalizar
        return (
            df_sub[col]
            .map(mapping)
            .fillna(
                df_sub[col]
                .fillna("Otro")  # por si viniera NaN
                .str.replace("_", " ")
                .str.strip()
                .str.capitalize()
            )
        )

    df_sub['play_type_es'] = _nice('play_type', play_type_map)
    df_sub['possession_type_es'] = df_sub['possession_type'].fillna("Otro")  # por si viniera NaN
    df_sub['shot_location_es'] = _nice('shot_location', shot_location_map)


    # --- Agrupar según la métrica seleccionada ---
    if metric in ['goals', 'shots']:
        grouped = (
            df_sub
            .groupby(['play_type_es', 'possession_type_es', 'shot_location_es'], as_index=False)
            .size()
            .rename(columns={'size': 'valor_metric'})
        )
    else:  # xg_sum
        grouped = (
            df_sub
            .groupby(['play_type_es', 'possession_type_es', 'shot_location_es'], as_index=False)
            [xg_col].sum()
            .rename(columns={xg_col: 'valor_metric'})
        )

    # --- Sunburst ---
    fig = px.sunburst(
        grouped,
        path=['play_type_es', 'possession_type_es', 'shot_location_es'],
        values='valor_metric',
        color='play_type_es',
        color_discrete_map=play_type_colors
    )

    if metric in ['goals', 'shots']:
        value_format = '%{value:.0f}'
    else:  # xg_sum
        value_format = '%{value:.2f}'

    fig.update_traces(
        insidetextorientation='radial',
        texttemplate='%{label}<br>%{percentRoot:.1%}',
        hovertemplate=(
            '<b>%{label}</b><br>' +
            f'{valor_label}: {value_format}<br>' +
            'Porcentaje: %{percentRoot:.1%}<extra></extra>'
        )
    )


    fig.update_layout(
        title=f'{team_name} – {titulo_metric} por tipo de jugada, ubicación y parte del cuerpo',
        margin=dict(t=60, l=0, r=0, b=0),
        paper_bgcolor='#101820',
        plot_bgcolor='#101820',
        font_color='white'
    )

    return fig, df_sub


def plot_offensive_dashboard(df, team_name, filter_col='TeamName'):
    from PIL import Image
    import os

    df_equipo = df[df[filter_col] == team_name]
    # --- FILTRO GOLES A FAVOR ---
    df_goles = df_equipo[
        (df_equipo['NaEventType'] == 'Goal') &
        (df_equipo['own_goal'] != -1)
    ].copy()

    if df_goles.empty:
        st.warning(f"⚠️ No hay goles a favor para {team_name}.")
        return None

    # --- Marcamos si el gol fue de cabeza ---
    df_goles['is_header'] = df_goles['head_info'].notna() & (df_goles['head_info'] != '')

    # --- Escalar tamaño de burbuja según xGOT ---
    max_xgot = df_goles['xgot'].max() if df_goles['xgot'].max() > 0 else 1.0
    size_min = 20
    size_max = 100

    xgot_norm = df_goles['xgot'] / max_xgot
    marker_sizes = size_min + (size_max - size_min) * xgot_norm

    # ======================================================
    # FIGURA CON 2 COLUMNAS
    # ======================================================
    fig, (ax_pitch, ax_goal) = plt.subplots(
        1, 2, figsize=(16, 7)
    )
    fig.set_facecolor('#101820')

    # ======================================================
    # 1) IZQUIERDA: GOLES EN EL PITCH (últimos 30m)
    # ======================================================
    pitch = Pitch(
        pitch_type='opta',
        pitch_color='#22312b',
        line_color='white',
        linewidth=1.5
    )
    pitch.draw(ax=ax_pitch)

    mask_header = df_goles['is_header']
    df_head = df_goles[mask_header]
    df_foot = df_goles[~mask_header]

    sizes_head = marker_sizes[mask_header]
    sizes_foot = marker_sizes[~mask_header]

    # Goles de cabeza (azul)
    if not df_head.empty:
        pitch.scatter(
            df_head['x'], df_head['y'],
            s=sizes_head,
            edgecolors='white',
            linewidth=1.0,
            alpha=0.7,
            ax=ax_pitch,
            zorder=3,
            label='Cabeza',
            c='#2196F3'
        )

    # Goles no de cabeza (verde)
    if not df_foot.empty:
        pitch.scatter(
            df_foot['x'], df_foot['y'],
            s=sizes_foot,
            edgecolors='white',
            linewidth=1.0,
            alpha=0.7,
            ax=ax_pitch,
            zorder=3,
            label='Pie',
            c='#4CAF50'
        )

    ax_pitch.set_xlim(70, 100)
    ax_pitch.set_ylim(0, 100)

    if not df_head.empty or not df_foot.empty:
        ax_pitch.legend(
            loc='upper center',
            bbox_to_anchor=(0.5, 1.03),
            ncol=2,
            frameon=True,
            fontsize=9
        )

    ax_pitch.set_title(
        f'Ubicación de Goles',
        fontsize=14,
        color='white',
        pad=10
    )

    # ======================================================
    # 2) DERECHA: DISTRIBUCIÓN EN EL ARCO (GOAL MOUTH)
    # ======================================================
    y_post1 = 45.2
    y_post2 = 54.8
    z_min = 0
    z_max = 34.8

    goal_img_path = "images/goal_fondo_2.jpg"
    if os.path.exists(goal_img_path):
        goal_img = Image.open(goal_img_path)
        ax_goal.imshow(goal_img, extent=[y_post1, y_post2, z_min, z_max], aspect='auto')
    else:
        st.warning(f"Advertencia: No se encontró la imagen del arco en '{goal_img_path}'.")


    # Tiros a puerta: goles (mismos que df_goles) + Attempt Saved
    df_saved = df_equipo[(df_equipo['NaEventType'] == "Attempt Saved") & (df_equipo['blocked'] != -1)].copy()

    def scale_size(proba, min_size=50, max_size=300):
        return min_size + (max_size - min_size) * proba

    # Split goles en cabeza vs no cabeza para el arco
    df_goal_head = df_goles[df_goles['is_header']].copy()
    df_goal_foot = df_goles[~df_goles['is_header']].copy()

    if not df_goal_head.empty:
        df_goal_head['size'] = df_goal_head['xgot'].apply(scale_size)
    if not df_goal_foot.empty:
        df_goal_foot['size'] = df_goal_foot['xgot'].apply(scale_size)
    if not df_saved.empty:
        df_saved['size'] = df_saved['xgot'].apply(scale_size)

    # 🟦 Goles de cabeza (azul)
    if not df_goal_head.empty:
        ax_goal.scatter(
            df_goal_head['Goal_mouth_y_co-ordinate'],
            df_goal_head['Goal_mouth_z_co-ordinate'],
            color='#2196F3',
            label='Gol cabeza',
            s=df_goal_head['size'],
            edgecolors='black',
            alpha=0.6
        )

    # 🟩 Goles no de cabeza (verde)
    if not df_goal_foot.empty:
        ax_goal.scatter(
            df_goal_foot['Goal_mouth_y_co-ordinate'],
            df_goal_foot['Goal_mouth_z_co-ordinate'],
            color='#4CAF50',
            label='Gol pie/otro',
            s=df_goal_foot['size'],
            edgecolors='black',
            alpha=0.6
        )

    # 🟥 Tiros a puerta sin gol (Attempt Saved)
    if not df_saved.empty:
        ax_goal.scatter(
            df_saved['Goal_mouth_y_co-ordinate'],
            df_saved['Goal_mouth_z_co-ordinate'],
            color='#E53935',
            label='Tiro a puerta sin gol',
            s=df_saved['size'] * 1.1,
            edgecolors='black',
            alpha=0.6
        )

    ax_goal.set_xlim(y_post1, y_post2)
    ax_goal.set_ylim(z_min, z_max)
    ax_goal.set_xticks([])
    ax_goal.set_yticks([])

    ax_goal.set_title(
        'Distribución de tiros a puerta',
        fontsize=14,
        color='white',
        pad=10
    )
    
    # Solo mostrar la leyenda si hay algo que mostrar
    if not df_goal_head.empty or not df_goal_foot.empty or not df_saved.empty:
        ax_goal.legend()

    ax_goal.invert_xaxis()

    plt.tight_layout()

    return fig


def summarize_goal_possessions(df, team_name, filter_col='TeamName'):
    """
    Devuelve un DataFrame con un flag por tipo de acción
    para cada posesión que termina en gol.
    """
    # 1) Filtrar equipo
    df_team = df[df[filter_col] == team_name].copy()

    # 2) Posesiones que terminan en gol a favor
    df_goals = df_team[
        (df_team['NaEventType'] == 'Goal') &
        (df_team['own_goal'] != -1)
    ].copy()

    if df_goals.empty:
        raise ValueError(f"No hay goles para {team_name}")

    goal_possessions = df_goals['Posesion'].unique()

    # 3) Quedarnos solo con eventos de esas posesiones
    df_pos_gol = df_team[df_team['Posesion'].isin(goal_possessions)].copy()

    # 4) Función que marca si la posesión incluye cada acción
    def flag_actions(g):
        # por seguridad, usamos get con .get(col, SerieFalse) si quieres blindarlo
        return pd.Series({
            "Incluye Balón Largo": (g['long_ball'].notna() & g['chipped'].notna() & g['cross'].isna()).any(),
            "Incluye Balón Largo Raso": (g['long_ball'].notna() & g['chipped'].isna() & g['cross'].isna()).any(),
            "Pase a la profundidad": g['through_ball'].notna().any(),
            "Apoyo": g['lay_off'].notna().any(),
            "1 vs 1": (g['1_on_1'] == 1).any(),
            "A un toque": (g['First_Touch'] == -1).any(),
            "No asistido": (g['Individual_Play'] == 1).any(),
            "Cutback": (g['cutback'] == 1).any(),
            "Pase Dividido": (g['dividido'] == 1).any(),
            "Panenka": (g['Panenka'] == -1).any(),
            "Desviado": (g['Deflection'] == -1).any(),
            "Recuperación rápida tras pérdida": (g['counterpress_5s_flag'] == 1).any(),
            "Saque de Banda": (g['throw_in'] == -1).any(),
            "Saque de Falta": ((g['Set_piece'] == 1) | (g['Free_kick'] == 1)).any(),
            # Centros
            "Centro temprano": (
                (g['cross'].notna()) & (g['x'] < 75)
            ).any(),
            "Centro abierto": (
                (g['cross'].notna()) &
                (g['x'] >= 75) &
                g['out_swing'].notna() &
                g['chipped'].notna()
            ).any(),
            "Centro cerrado": (
                (g['cross'].notna()) &
                (g['x'] >= 75) &
                g['in_swinger'].notna() &
                g['chipped'].notna()
            ).any(),
            "Centro raso": (
                (g['cross'].notna()) &
                (g['x'] >= 75) &
                g['chipped'].isna()
            ).any(),
        })

    per_pos = df_pos_gol.groupby('Posesion').apply(flag_actions)

    # Nos aseguramos de tener booleanos
    per_pos = per_pos.astype(bool)

    return per_pos

def plot_goal_actions_bar(df, team_name="Racing de Santander", filter_col='TeamName'):
    try:
        per_pos = summarize_goal_possessions(df, team_name, filter_col=filter_col)
    except ValueError as e:
        st.warning(f"⚠️ {e}")
        return None

    # Conteo de posesiones (goles) que incluyen cada acción
    counts = per_pos.sum(axis=0)  # suma True = nº de posesiones
    counts = counts[counts > 0]   # nos quedamos solo con las que aparecen
    counts = counts.sort_values(ascending=True)

    if counts.empty:
        st.warning(f"⚠️ No hay acciones destacadas en los goles de {team_name}.")
        return None

    total_goals = len(per_pos)

    df_counts = counts.rename_axis("Acción").reset_index(name="n_goles")
    df_counts["pct"] = df_counts["n_goles"] / total_goals * 100

    fig = px.bar(
        df_counts,
        x="n_goles",
        y="Acción",
        orientation="h",
        text="n_goles",
        template="plotly_white",
    )

    fig.update_traces(
        hovertemplate=(
            "%{y}<br>" +
            "Goles: %{x} de " + str(total_goals) + "<br>" +
            "Porcentaje: %{customdata[0]:.1f}%<extra></extra>"
        ),
        customdata=df_counts[["pct"]].to_numpy(),
        textposition="outside"
    )

    fig.update_layout(
        title=f"{team_name} – Goles que incluyen cada tipo de acción\n"
              f"(sobre {total_goals} goles)",
        xaxis_title="Número de goles",
        yaxis_title="",
        margin=dict(l=120, r=30, t=80, b=30),
    )

    return fig


def plot_offensive_dashboard(df, team_name, filter_col='TeamName'):
    from PIL import Image
    import os

    df_equipo = df[df[filter_col] == team_name]
    # --- FILTRO GOLES A FAVOR ---
    df_goles = df_equipo[
        (df_equipo['NaEventType'] == 'Goal') &
        (df_equipo['own_goal'] != -1)
    ].copy()

    if df_goles.empty:
        st.warning(f"⚠️ No hay goles a favor para {team_name}.")
        return None

    # --- Marcamos si el gol fue de cabeza ---
    df_goles['is_header'] = df_goles['head_info'].notna() & (df_goles['head_info'] != '')

    # --- Escalar tamaño de burbuja según xGOT ---
    max_xgot = df_goles['xgot'].max() if df_goles['xgot'].max() > 0 else 1.0
    size_min = 20
    size_max = 100

    xgot_norm = df_goles['xgot'] / max_xgot
    marker_sizes = size_min + (size_max - size_min) * xgot_norm

    # ======================================================
    # FIGURA CON 2 COLUMNAS
    # ======================================================
    fig, (ax_pitch, ax_goal) = plt.subplots(
        1, 2, figsize=(16, 7)
    )
    fig.set_facecolor('#101820')

    # ======================================================
    # 1) IZQUIERDA: GOLES EN EL PITCH (últimos 30m)
    # ======================================================
    pitch = Pitch(
        pitch_type='opta',
        pitch_color='#22312b',
        line_color='white',
        linewidth=1.5
    )
    pitch.draw(ax=ax_pitch)

    mask_header = df_goles['is_header']
    df_head = df_goles[mask_header]
    df_foot = df_goles[~mask_header]

    sizes_head = marker_sizes[mask_header]
    sizes_foot = marker_sizes[~mask_header]

    # Goles de cabeza (azul)
    if not df_head.empty:
        pitch.scatter(
            df_head['x'], df_head['y'],
            s=sizes_head,
            edgecolors='white',
            linewidth=1.0,
            alpha=0.7,
            ax=ax_pitch,
            zorder=3,
            label='Cabeza',
            c='#2196F3'
        )

    # Goles no de cabeza (verde)
    if not df_foot.empty:
        pitch.scatter(
            df_foot['x'], df_foot['y'],
            s=sizes_foot,
            edgecolors='white',
            linewidth=1.0,
            alpha=0.7,
            ax=ax_pitch,
            zorder=3,
            label='Pie',
            c='#4CAF50'
        )

    ax_pitch.set_xlim(70, 100)
    ax_pitch.set_ylim(0, 100)

    if not df_head.empty or not df_foot.empty:
        ax_pitch.legend(
            loc='upper center',
            bbox_to_anchor=(0.5, 1.03),
            ncol=2,
            frameon=True,
            fontsize=9
        )

    ax_pitch.set_title(
        f'Ubicación de Goles',
        fontsize=14,
        color='white',
        pad=10
    )

    # ======================================================
    # 2) DERECHA: DISTRIBUCIÓN EN EL ARCO (GOAL MOUTH)
    # ======================================================
    y_post1 = 45.2
    y_post2 = 54.8
    z_min = 0
    z_max = 34.8

    goal_img_path = "images/goal_fondo_2.jpg"
    if os.path.exists(goal_img_path):
        goal_img = Image.open(goal_img_path)
        ax_goal.imshow(goal_img, extent=[y_post1, y_post2, z_min, z_max], aspect='auto')
    else:
        st.warning(f"Advertencia: No se encontró la imagen del arco en '{goal_img_path}'.")


    # Tiros a puerta: goles (mismos que df_goles) + Attempt Saved
    df_saved = df_equipo[(df_equipo['NaEventType'] == "Attempt Saved") & (df_equipo['blocked'] != -1)].copy()

    def scale_size(proba, min_size=50, max_size=300):
        return min_size + (max_size - min_size) * proba

    # Split goles en cabeza vs no cabeza para el arco
    df_goal_head = df_goles[df_goles['is_header']].copy()
    df_goal_foot = df_goles[~df_goles['is_header']].copy()

    if not df_goal_head.empty:
        df_goal_head['size'] = df_goal_head['xgot'].apply(scale_size)
    if not df_goal_foot.empty:
        df_goal_foot['size'] = df_goal_foot['xgot'].apply(scale_size)
    if not df_saved.empty:
        df_saved['size'] = df_saved['xgot'].apply(scale_size)

    # 🟦 Goles de cabeza (azul)
    if not df_goal_head.empty:
        ax_goal.scatter(
            df_goal_head['Goal_mouth_y_co-ordinate'],
            df_goal_head['Goal_mouth_z_co-ordinate'],
            color='#2196F3',
            label='Gol cabeza',
            s=df_goal_head['size'],
            edgecolors='black',
            alpha=0.6
        )

    # 🟩 Goles no de cabeza (verde)
    if not df_goal_foot.empty:
        ax_goal.scatter(
            df_goal_foot['Goal_mouth_y_co-ordinate'],
            df_goal_foot['Goal_mouth_z_co-ordinate'],
            color='#4CAF50',
            label='Gol pie/otro',
            s=df_goal_foot['size'],
            edgecolors='black',
            alpha=0.6
        )

    # 🟥 Tiros a puerta sin gol (Attempt Saved)
    if not df_saved.empty:
        ax_goal.scatter(
            df_saved['Goal_mouth_y_co-ordinate'],
            df_saved['Goal_mouth_z_co-ordinate'],
            color='#E53935',
            label='Tiro a puerta sin gol',
            s=df_saved['size'] * 1.1,
            edgecolors='black',
            alpha=0.6
        )

    ax_goal.set_xlim(y_post1, y_post2)
    ax_goal.set_ylim(z_min, z_max)
    ax_goal.set_xticks([])
    ax_goal.set_yticks([])

    ax_goal.set_title(
        'Distribución de tiros a puerta',
        fontsize=14,
        color='white',
        pad=10
    )
    
    # Solo mostrar la leyenda si hay algo que mostrar
    if not df_goal_head.empty or not df_goal_foot.empty or not df_saved.empty:
        ax_goal.legend()

    ax_goal.invert_xaxis()

    plt.tight_layout()

    return fig


def plot_xg_actions_bar(df, team_name="Racing de Santander", filter_col='TeamName'):
    """
    Calcula el xG acumulado para las posesiones que incluyen cada tipo de acción.
    Se basa en la lógica de `plot_goal_actions_bar` pero suma xG en lugar de contar goles.
    """
    try:
        # 1. Usar una función auxiliar para obtener los flags de acción por posesión.
        #    Esta función es una adaptación de `summarize_goal_possessions` para
        #    trabajar sobre todas las posesiones con tiro, no solo las de gol.
        
        # 1a. Filtrar equipo
        df_team = df[df[filter_col] == team_name].copy()

        # 1b. Posesiones que terminan en TIRO (tienen xg)
        shot_possessions = df_team.loc[df_team['xg'].notna(), 'Posesion'].unique()
        if len(shot_possessions) == 0:
            raise ValueError(f"No hay posesiones con tiro para {team_name}")

        # 1c. Quedarnos solo con eventos de esas posesiones
        df_pos_shot = df_team[df_team['Posesion'].isin(shot_possessions)].copy()

        # 1d. Reutilizar la función `flag_actions` de `summarize_goal_possessions`
        #     para no duplicar código.
        def flag_actions(g):
            return pd.Series({
                "Incluye Balón Largo": (g['long_ball'].notna() & g['chipped'].notna() & g['cross'].isna()).any(),
                "Incluye Balón Largo Raso": (g['long_ball'].notna() & g['chipped'].isna() & g['cross'].isna()).any(),
                "Pase a la profundidad": g['through_ball'].notna().any(),
                "Apoyo": g['lay_off'].notna().any(),
                "1 vs 1": (g['1_on_1'] == 1).any(),
                "A un toque": (g['First_Touch'] == -1).any(),
                "No asistido": (g['Individual_Play'] == 1).any(),
                "Cutback": (g['cutback'] == 1).any(),
                "Pase Dividido": (g['dividido'] == 1).any(),
                "Panenka": (g['Panenka'] == -1).any(),
                "Desviado": (g['Deflection'] == -1).any(),
                "Recuperación rápida tras pérdida": (g['counterpress_5s_flag'] == 1).any(),
                "Saque de Banda": (g['throw_in'] == -1).any(),
                "Saque de Falta": ((g['Set_piece'] == 1) | (g['Free_kick'] == 1)).any(),
                "Centro temprano": ((g['cross'].notna()) & (g['x'] < 75)).any(),
                "Centro abierto": ((g['cross'].notna()) & (g['x'] >= 75) & g['out_swing'].notna() & g['chipped'].notna()).any(),
                "Centro cerrado": ((g['cross'].notna()) & (g['x'] >= 75) & g['in_swinger'].notna() & g['chipped'].notna()).any(),
                "Centro raso": ((g['cross'].notna()) & (g['x'] >= 75) & g['chipped'].isna()).any(),
            })

        per_pos_actions = df_pos_shot.groupby('Posesion').apply(flag_actions).astype(bool)

    except ValueError as e:
        st.warning(f"⚠️ {e}")
        return None

    # 2. Obtener el xG total por posesión y unirlo a los flags
    possession_xg = df_pos_shot.groupby('Posesion')['xg'].sum()
    per_pos_actions['possession_xg'] = per_pos_actions.index.map(possession_xg)

    # 3. Calcular el xG acumulado por cada tipo de acción
    xg_by_action = {}
    action_cols = [col for col in per_pos_actions.columns if col != 'possession_xg']

    for action in action_cols:
        # Sumar el 'possession_xg' solo de las posesiones donde la acción es True
        total_xg_for_action = per_pos_actions.loc[per_pos_actions[action], 'possession_xg'].sum()
        if total_xg_for_action > 0:
            xg_by_action[action] = total_xg_for_action
    
    if not xg_by_action:
        st.warning(f"⚠️ No se encontró xG asociado a acciones destacadas para {team_name}.")
        return None

    # 4. Crear el gráfico de barras
    df_xg_counts = pd.DataFrame.from_dict(xg_by_action, orient='index', columns=['total_xg'])
    df_xg_counts = df_xg_counts.rename_axis("Acción").reset_index()
    df_xg_counts = df_xg_counts.sort_values('total_xg', ascending=True)

    fig = px.bar(
        df_xg_counts,
        x="total_xg",
        y="Acción",
        orientation="h",
        text="total_xg",
        template="plotly_white",
    )

    fig.update_traces(
        hovertemplate=(
            "%{y}<br>" +
            "xG Acumulado: %{x:.2f}<extra></extra>"
        ),
        texttemplate='%{x:.2f}',
        textposition="outside"
    )

    fig.update_layout(
        title=f"{team_name} – xG acumulado por tipo de acción en la posesión",
        xaxis_title="xG Acumulado",
        yaxis_title="",
        margin=dict(l=120, r=30, t=80, b=30),
    )

    return fig

def plot_pass_matrix(df, team_name, filter_col='TeamName', x_range=(0, 100), y_range=(0, 100)):
    """
    Crea una matriz de pases (heatmap) para un equipo, con opción de filtrar por zona.
    """
    # 1. Filtrar datos
    mask = (
        (df[filter_col] == team_name) &
        (df['NaEventType'] == 'Pass') &
        (df['Outcome'] == 1) &
        (df['receiving_player'].notna()) &
        (df['receiving_player'] != '') &
        (df['receiving_player'] != 'null') &
        (df['x'].between(x_range[0], x_range[1])) &
        (df['y'].between(y_range[0], y_range[1]))
    )
    df_passes = df[mask].copy()

    if df_passes.empty:
        st.warning(f"⚠️ No hay datos de pases para {team_name} con los filtros aplicados (x_range={x_range}, y_range={y_range}).")
        return None

    # 2. Crear la matriz de pases
    pass_matrix = pd.crosstab(df_passes['NaPlayer'], df_passes['receiving_player'])

    # Asegurarse de que todos los jugadores estén en filas y columnas
    all_players = sorted(list(set(pass_matrix.index) | set(pass_matrix.columns)))
    pass_matrix = pass_matrix.reindex(index=all_players, columns=all_players, fill_value=0)

    # 3. Ordenar la matriz por pases totales dados
    # Se calcula la suma de pases dados por cada jugador
    total_passes_given = pass_matrix.sum(axis=1).sort_values(ascending=False)
    
    # Se obtiene el orden de los jugadores
    sorted_players = total_passes_given.index.tolist()
    
    # Se reordena la matriz (filas y columnas)
    pass_matrix = pass_matrix.loc[sorted_players, sorted_players]

    # 4. Calcular totales (después de ordenar)
    pass_matrix['Total Pases Dados'] = pass_matrix.sum(axis=1)
    pass_matrix.loc['Total Pases Recibidos'] = pass_matrix.sum(axis=0)
    pass_matrix.loc['Total Pases Recibidos', 'Total Pases Dados'] = pass_matrix['Total Pases Dados'].sum()

    # 5. Preparar para el heatmap (corregir escala de color)
    # Se extrae la matriz de jugadores sin los totales para definir la escala de color
    player_pass_matrix = pass_matrix.iloc[:-1, :-1]
    vmax = player_pass_matrix.max().max() # El valor máximo sin contar los totales

    # 6. Crear el heatmap con Seaborn
    fig, ax = plt.subplots(figsize=(16, 12))
    fig.set_facecolor('#101820')
    
    # Dibujar el heatmap SIN anotaciones primero
    sns.heatmap(
        pass_matrix,
        annot=False, # Se quitan las anotaciones automáticas
        fmt=".0f",
        cmap="viridis",
        linewidths=.5,
        ax=ax,
        cbar=False,
        vmax=vmax
    )

    # 7. Añadir anotaciones con color de texto adaptativo
    # Normalizar la matriz para obtener valores de 0 a 1 para el colormap
    # Usamos el vmax de los jugadores para la normalización
    norm = plt.Normalize(vmin=0, vmax=vmax)

    for i in range(pass_matrix.shape[0]):
        for j in range(pass_matrix.shape[1]):
            value = pass_matrix.iloc[i, j]
            
            # Obtener el color de la celda del colormap usando la normalización
            # np.clip asegura que los valores de los totales (que exceden vmax) se mapeen al color más alto
            color = plt.get_cmap("viridis")(norm(np.clip(value, 0, vmax)))
            
            # Decidir el color del texto basado en la luminosidad del fondo
            luminance = (0.299 * color[0] + 0.587 * color[1] + 0.114 * color[2])
            text_color = "white" if luminance < 0.5 else "black"

            ax.text(j + 0.5, i + 0.5, f'{int(value)}',
                    ha='center', va='center', color=text_color, size=10)

    # Estilizar el gráfico
    ax.set_title(f"Matriz de Pases - {team_name}", color='white', fontsize=16)
    ax.set_xlabel("Receptor", color='white', fontsize=12)
    ax.set_ylabel("Pasador", color='white', fontsize=12)
    plt.xticks(rotation=45, ha='right', color='white')
    plt.yticks(rotation=0, color='white')

    # Resaltar los totales
    ax.get_xticklabels()[-1].set_weight('bold')
    ax.get_yticklabels()[-1].set_weight('bold')
    ax.get_xticklabels()[-1].set_color('yellow')
    ax.get_yticklabels()[-1].set_color('yellow')


    plt.tight_layout()
    return fig


def plot_pass_xg_matrix(df, team_name, filter_col='TeamName', x_range=(0, 100), y_range=(0, 100)):
    """
    Crea una matriz de pases ponderada por el xG de la posesión.
    """
    # 1. Preparar datos: Asignar xG de la posesión a todos sus eventos
    df_team = df[df[filter_col] == team_name].copy()
    
    # Obtener el xG por posesión (solo las que terminan en tiro)
    possession_xg = df_team.loc[df_team['xg'].notna()].groupby('Posesion')['xg'].sum()
    
    if possession_xg.empty:
        st.warning(f"⚠️ No hay posesiones con xG para {team_name}.")
        return None

    # Asignar el xG a cada evento de la posesión correspondiente
    df_team['possession_xg'] = df_team['Posesion'].map(possession_xg)

    # 2. Filtrar solo los pases en posesiones con xG
    mask = (
        (df_team['NaEventType'] == 'Pass') &
        (df_team['Outcome'] == 1) &
        (df_team['receiving_player'].notna()) &
        (df_team['receiving_player'] != '') &
        (df_team['receiving_player'] != 'null') &
        (df_team['possession_xg'].notna()) & # Solo pases en posesiones con xG
        (df_team['x'].between(x_range[0], x_range[1])) &
        (df_team['y'].between(y_range[0], y_range[1]))
    )
    df_passes_xg = df_team[mask].copy()

    # Eliminar duplicados para no sumar el xG de la posesión por cada pase
    df_passes_xg = df_passes_xg.drop_duplicates(subset=['Posesion', 'NaPlayer', 'receiving_player'])

    if df_passes_xg.empty:
        st.warning(f"⚠️ No hay datos de pases en posesiones con xG para {team_name} con los filtros aplicados (x_range={x_range}, y_range={y_range}).")
        return None

    # 3. Crear la matriz de pases de xG
    pass_xg_matrix = pd.pivot_table(
        df_passes_xg,
        values='possession_xg',
        index='NaPlayer',
        columns='receiving_player',
        aggfunc='sum',
        fill_value=0
    )

    # 4. Asegurarse de que todos los jugadores estén en filas y columnas y ordenar
    all_players = sorted(list(set(pass_xg_matrix.index) | set(pass_xg_matrix.columns)))
    pass_xg_matrix = pass_xg_matrix.reindex(index=all_players, columns=all_players, fill_value=0)

    total_xg_given = pass_xg_matrix.sum(axis=1).sort_values(ascending=False)
    sorted_players = total_xg_given.index.tolist()
    pass_xg_matrix = pass_xg_matrix.loc[sorted_players, sorted_players]

    # 5. Calcular totales y ajustar etiquetas
    pass_xg_matrix['Total xG Generado'] = pass_xg_matrix.sum(axis=1)
    pass_xg_matrix.loc['Total Recepciones - xG Generado'] = pass_xg_matrix.sum(axis=0)
    pass_xg_matrix.loc['Total Recepciones - xG Generado', 'Total xG Generado'] = np.nan # Eliminar el valor de la esquina

    # 6. Preparar y crear el heatmap
    player_pass_xg_matrix = pass_xg_matrix.iloc[:-1, :-1]
    vmax = player_pass_xg_matrix.max().max()

    fig, ax = plt.subplots(figsize=(16, 12))
    fig.set_facecolor('#101820')
    
    sns.heatmap(
        pass_xg_matrix,
        annot=False,
        fmt=".2f",
        cmap="viridis",
        linewidths=.5,
        ax=ax,
        cbar=False,
        vmax=vmax
    )

    # 7. Añadir anotaciones con formato de 2 decimales
    norm = plt.Normalize(vmin=0, vmax=vmax if vmax > 0 else 1)

    for i in range(pass_xg_matrix.shape[0]):
        for j in range(pass_xg_matrix.shape[1]):
            value = pass_xg_matrix.iloc[i, j]
            if value == 0: continue # No anotar ceros

            color = plt.get_cmap("viridis")(norm(np.clip(value, 0, vmax)))
            luminance = (0.299 * color[0] + 0.587 * color[1] + 0.114 * color[2])
            text_color = "white" if luminance < 0.5 else "black"

            ax.text(j + 0.5, i + 0.5, f'{value:.2f}',
                    ha='center', va='center', color=text_color, size=9)

    # 8. Estilizar el gráfico
    ax.set_title(f"Matriz de Pases de xG - {team_name}", color='white', fontsize=16)
    ax.set_xlabel("Receptor", color='white', fontsize=12)
    ax.set_ylabel("Pasador", color='white', fontsize=12)
    plt.xticks(rotation=45, ha='right', color='white')
    plt.yticks(rotation=0, color='white')

    ax.get_xticklabels()[-1].set_weight('bold')
    ax.get_yticklabels()[-1].set_weight('bold')
    ax.get_xticklabels()[-1].set_color('yellow')
    ax.get_yticklabels()[-1].set_color('yellow')

    plt.tight_layout()
    return fig

def plot_area_entries_team(
    df,
    team_name,
    filter_col='TeamName',
    title="Ingresos área rival",
    box_end_x=83, box_end_y_low=21, box_end_y_high=79,
    box_start_x=83, box_start_y_low=21, box_start_y_high=79,
    x_bands=(25.0, 50.0, 65.5, 83, 100),          # bandas en largo
    pasillo_edges=(0.0, 21.0, 37.0, 63.0, 79.0, 100),  # pasillos en ancho
    rect_color="#4CAF50",
    line_color="white",
    bg_color="#22312b",
    show_counts=True,
    count_threshold=1,
    label_fontsize=14,
    figsize=(8, 6),
):
    """
    Heatmap discreto de desde dónde entra al área rival un equipo (posesiones exitosas).

    df: dataframe con todos los eventos
    team_name: nombre del equipo a analizar
    filter_col: columna para filtrar ('TeamName' o 'RivalName')
    """

    # --- Filtrar equipo ---
    df_team = df[df[filter_col] == team_name].copy()
    if df_team.empty:
        # En lugar de un error, devolvemos una figura vacía con un mensaje
        fig, ax = plt.subplots(figsize=figsize)
        pitch = Pitch(
            pitch_type="opta",
            goal_type="box", goal_alpha=0.5, corner_arcs=True,
            pitch_color=bg_color, line_color=line_color, linewidth=2,
        )
        pitch.draw(ax=ax)
        ax.set_title(f"{team_name} – Sin datos de eventos",
                     fontsize=16, color="white", fontweight="bold")
        return fig, pd.DataFrame(), None


    # --- Filtro de entradas exitosas al área rival ---
    def _filter_entries(d):
        d = d.copy()
        ok = (
            (d["x"] >= 25) &                              # al menos en campo rival
            (d["corner_taken"] != "-1") &                 # excluir corners (ajusta si cambia)
            (d["corner_taken"].isna()) &
            (d["Outcome"].eq(1)) &                        # acción exitosa
            ((d["NaEventType"] == "Pass")| (d["NaEventType"] == "BallDrive")) &
            (d["end_x"] >= box_end_x) &                   # termina dentro del área en x
            (d["end_y"] >= box_end_y_low) &
            (d["end_y"] <= box_end_y_high) &              # termina dentro del área en y
            ~(
                (d["x"] >= box_start_x) &
                (d["y"] >= box_start_y_low) &
                (d["y"] <= box_start_y_high)
            )                                             # no empieza ya dentro del área
        )
        return d.loc[ok]

    df_entries = _filter_entries(df_team)

    # Si no hay entradas, devolvemos figura vacía agradable
    fig, ax = plt.subplots(figsize=figsize)
    fig.set_facecolor(bg_color)
    pitch = Pitch(
        pitch_type="opta",
        goal_type="box", goal_alpha=0.5, corner_arcs=True,
        pitch_color=bg_color, line_color=line_color, linewidth=2,
    )
    pitch.draw(ax=ax)

    if df_entries.empty:
        ax.set_title(f"{team_name} – Sin ingresos al área con los filtros actuales",
                     fontsize=16, color="white", fontweight="bold")
        return fig, df_entries, None

    # --- Preparamos rejilla ---
    x_edges = np.array(x_bands, dtype=float)
    y_edges = np.array(pasillo_edges, dtype=float)

    def _grid_counts(df_xy, x_edges, y_edges):
        counts = np.zeros((len(x_edges) - 1, len(y_edges) - 1), dtype=int)
        if df_xy.empty:
            return counts
        X = df_xy["x"].to_numpy()
        Y = df_xy["y"].to_numpy()
        xi = np.digitize(X, x_edges) - 1
        yi = np.digitize(Y, y_edges) - 1
        valid = (
            (xi >= 0) & (xi < len(x_edges) - 1) &
            (yi >= 0) & (yi < len(y_edges) - 1)
        )
        for i, j in zip(xi[valid], yi[valid]):
            counts[i, j] += 1
        return counts

    counts = _grid_counts(df_entries, x_edges, y_edges)
    total_entries = int(counts.sum())
    max_c = counts.max() if counts.size and counts.max() > 0 else 1

    # --- Pintar rectángulos ---
    for i in range(len(x_edges) - 1):
        x0, x1 = float(x_edges[i]), float(x_edges[i + 1])
        dx = x1 - x0
        for j in range(len(y_edges) - 1):
            y0, y1 = float(y_edges[j]), float(y_edges[j + 1])
            dy = y1 - y0
            c = counts[i, j]
            if c > 0:
                alpha = (c / max_c) * 0.95
                ax.add_patch(
                    plt.Rectangle(
                        (x0, y0),
                        dx,
                        dy,
                        facecolor=rect_color,
                        edgecolor="none",
                        alpha=alpha,
                        zorder=1,
                    )
                )
                if show_counts and c >= count_threshold:
                    ax.text(
                        x0 + dx / 2,
                        y0 + dy / 2,
                        f"{c}",
                        ha="center",
                        va="center",
                        fontsize=label_fontsize,
                        color="white",
                        fontweight="bold",
                        zorder=3,
                        path_effects=[
                            pe.Stroke(linewidth=3.5, foreground="black", alpha=0.95),
                            pe.Normal(),
                        ],
                    )

    ax.set_title(
        f"{team_name} – Ingresos al área rival\n"
        f"(total: {total_entries})",
        fontsize=18,
        color="white",
        fontweight="bold",
    )

    # Opcional: ajustar límites para que se vea todo bien
    ax.set_xlim(-2, 107)
    ax.set_ylim(-3, 103)

    return fig, df_entries, {
        "grid": counts,
        "total_entries": total_entries,
        "x_edges": x_edges,
        "y_edges": y_edges,
    }

def plot_rival_half_entries_team(
    df,
    team_name,
    filter_col='TeamName',
    title="Ingresos a Campo Rival",
    x_bands=(50.0, 65.5, 83, 100),
    pasillo_edges=(0.0, 21.0, 37.0, 63.0, 79.0, 100),
    rect_color="#4CAF50",
    line_color="white",
    bg_color="#22312b",
    show_counts=True,
    count_threshold=1,
    label_fontsize=14,
    figsize=(8, 6),
):
    """
    Heatmap discreto de dónde ingresa a campo rival un equipo.
    """
    df_team = df[df[filter_col] == team_name].copy()
    if df_team.empty:
        fig, ax = plt.subplots(figsize=figsize)
        pitch = Pitch(pitch_type="opta", pitch_color=bg_color, line_color=line_color)
        pitch.draw(ax=ax)
        ax.set_title(f"{team_name} – Sin datos", color="white")
        return fig, pd.DataFrame(), None

    # Filtro: pases desde campo propio a campo rival
    ok = (
        (df_team["x"] <= 50) &
        (df_team["end_x"] > 50) &
        ((df_team["NaEventType"] == "Pass")| (df_team["NaEventType"] == "BallDrive")) &
        (df_team["Outcome"] == 1)
    )
    df_entries = df_team.loc[ok].copy()

    fig, ax = plt.subplots(figsize=figsize)
    fig.set_facecolor(bg_color)
    pitch = Pitch(pitch_type="opta", pitch_color=bg_color, line_color=line_color)
    pitch.draw(ax=ax)

    if df_entries.empty:
        ax.set_title(f"{team_name} – Sin ingresos a campo rival", color="white")
        return fig, df_entries, None

    x_edges = np.array(x_bands, dtype=float)
    y_edges = np.array(pasillo_edges, dtype=float)

    # Contar por end_x y end_y
    counts = np.histogram2d(df_entries['end_x'], df_entries['end_y'], bins=[x_edges, y_edges])[0].T

    total_entries = int(counts.sum())
    max_c = counts.max() if counts.size and counts.max() > 0 else 1

    for i in range(len(y_edges) - 1):
        for j in range(len(x_edges) - 1):
            c = counts[i, j]
            if c > 0:
                x0, x1 = float(x_edges[j]), float(x_edges[j+1])
                y0, y1 = float(y_edges[i]), float(y_edges[i+1])
                dx, dy = x1 - x0, y1 - y0
                alpha = (c / max_c) * 0.95
                ax.add_patch(
                    plt.Rectangle((x0, y0), dx, dy, facecolor=rect_color, edgecolor="none", alpha=alpha, zorder=1)
                )
                if show_counts and c >= count_threshold:
                    ax.text(
                        x0 + dx / 2, y0 + dy / 2, f"{int(c)}",
                        ha="center", va="center", fontsize=label_fontsize, color="white", fontweight="bold", zorder=3,
                        path_effects=[pe.Stroke(linewidth=3.5, foreground="black", alpha=0.95), pe.Normal()],
                    )

    ax.set_title(f"{team_name} – {title}\n(Total: {total_entries})", fontsize=18, color="white", fontweight="bold")
    ax.set_xlim(-2, 107)
    ax.set_ylim(-3, 103)

    return fig, df_entries, {"grid": counts, "total_entries": total_entries, "x_edges": x_edges, "y_edges": y_edges}


def plot_area_entry_passes(
    df,
    team_name,
    filter_col='TeamName',
    title_prefix="Ingresos al área por tipo de pase",
    only_assists=False,
    box_min_x=83.0,
    box_y_low=21.1,
    box_y_high=78.9,
):
    """
    Dibuja los pases que suponen un ingreso al área rival para un equipo dado,
    coloreados por tipo (cutback, through ball, etc.).

    df: DataFrame con eventos (formato Opta, x/y/end_x/end_y en [0,100])
    team_name: nombre del equipo (columna df['TeamName'])
    only_assists: si True, solo incluye pases marcados como 'assist' no nulos.
    """

    dfp = df.copy()
    dfp = dfp[
        (dfp[filter_col] == team_name) &
        (dfp["NaEventType"] == "Pass") &
        (dfp["corner_taken"].isna()) &
        (dfp["Outcome"] == 1)                               # pase correcto
    ].copy()

    if only_assists:
        dfp = dfp[dfp["assist"].notna()].copy()

    # Asegurar numéricos
    for c in ["x", "y", "end_x", "end_y"]:
        if c in dfp.columns:
            dfp[c] = pd.to_numeric(dfp[c], errors="coerce")

    # ---- Filtro geométrico: pases que ENTRAN al área ----
    # Termina dentro del área
    in_box_end = (
        (dfp["end_x"] >= box_min_x) &
        (dfp["end_y"] >= box_y_low) &
        (dfp["end_y"] <= box_y_high)
    )
    # No empieza ya dentro del área
    from_outside_box = ~(
        (dfp["x"] >= box_min_x) &
        (dfp["y"] >= box_y_low) &
        (dfp["y"] <= box_y_high)
    )

    dfp = dfp[in_box_end & from_outside_box].copy()

    if dfp.empty:
        print(f"⚠️ No hay ingresos al área para {team_name} con los filtros actuales.")
        return None, dfp

    # --------- Categoría por prioridad (una sola por pase) ----------
    def notna_col(df_local, col):
        return (
            df_local[col].notna()
            if col in df_local.columns
            else pd.Series(False, index=df_local.index)
        )

    def equals_val(df_local, col, val):
        return (
            (df_local[col] == val)
            if col in df_local.columns
            else pd.Series(False, index=df_local.index)
        )

    # Nuevas categorías con prioridad
    is_throw_in = equals_val(dfp, "throw_in", -1)
    is_free_kick = equals_val(dfp, "Free_kick", 1) | equals_val(dfp, "Set_piece", 1)
    is_centro_raso = equals_val(dfp, "cross", -1) & dfp["chipped"].isna() if "cross" in dfp.columns and "chipped" in dfp.columns else pd.Series(False, index=dfp.index)

    # Categorías existentes
    is_cutback  = (dfp["cutback"] == 1)   if "cutback" in dfp.columns  else pd.Series(False, index=dfp.index)
    is_dividido = (dfp["dividido"] == 1)  if "dividido" in dfp.columns else pd.Series(False, index=dfp.index)
    is_through  = notna_col(dfp, "through_ball")
    is_in       = notna_col(dfp, "in_swinger")
    is_out      = notna_col(dfp, "out_swing")
    is_longball = notna_col(dfp, "long_ball")
    is_layoff   = notna_col(dfp, "lay_off")

    dfp["assist_type"] = np.select(
        [is_throw_in, is_free_kick, is_centro_raso, is_cutback, is_dividido, is_through, is_in, is_out, is_longball, is_layoff],
        ["Saque de banda", "Saque de falta", "Centro Raso", "Cutback", "Dividido", "Pase Profundo", "Centro Cerrado", "Centro Abierto", "Balón Largo", "Apoyo"],
        default="Other",
    )

    # --------- Colores ----------
    COLORS = {
        "Saque de banda": "#F4D03F", # amarillo
        "Saque de falta": "#EE9559", # azul claro
        "Centro Raso":   "#E74C3C", # rojo
        "Cutback":      "#C2185B",  # magenta
        "Dividido":     "#5555AA",  # azul grisáceo
        "Pase Profundo": "#000000",  # negro
        "Centro Cerrado":   "#7AE7A7",  # verde
        "Centro Abierto":    "#0A6611",  # azul más oscuro
        "Balón Largo":    "#8D6E63",  # marrón
        "Apoyo":      "#747372",  # naranja
        "Other":        "#BD73DC",  # violeta
    }

    # --------- Plot ----------
    pitch = Pitch(pitch_type="opta", stripe=False)
    fig, ax = pitch.draw(figsize=(12, 7))
    #fig.set_facecolor("#EFE9E6")

    categories = ["Saque de banda", "Saque de falta", "Centro Raso", "Cutback", "Dividido", "Pase Profundo",
                  "Centro Cerrado", "Centro Abierto", "Balón Largo",
                  "Apoyo", "Other"]

    for key in categories:
        dfk = dfp[dfp["assist_type"] == key]
        if not dfk.empty:
            # trayectorias
            pitch.lines(
                dfk["x"], dfk["y"], dfk["end_x"], dfk["end_y"],
                color=COLORS[key],
                comet=True,
                transparent=True,
                alpha_start=0.10,
                alpha_end=0.30,
                ax=ax,
            )
            # punto de entrada al área
            pitch.scatter(
                dfk["end_x"], dfk["end_y"],
                ax=ax,
                facecolor="white",
                edgecolor=COLORS[key],
                linewidth=1.2,
                s=24,
                zorder=4,
            )

    # Leyenda
    legend_items = [
        Line2D([0], [0], color=COLORS[k], lw=4, label=k)
        for k in categories
    ]
    
    ax.legend(
        handles=legend_items,
        loc="lower left",
        frameon=True,
        facecolor="white",
        edgecolor="none",
        fontsize=11,
    )

    extra = " (solo asistencias)" if only_assists else ""
    ax.set_title(
        f"{title_prefix}{extra} — {team_name}\nIngresos al área: N={len(dfp)}",
        fontsize=14,
    )

    plt.tight_layout()

    return fig

def plot_area_entry_by_corridor(
    df,
    team_name,
    filter_col='TeamName',
    title_prefix="Ingresos al área por pasillo de origen",
    box_min_x=83.0,
    box_y_low=21,
    box_y_high=79,
):
    """
    Dibuja los pases que suponen un ingreso al área rival para un equipo dado,
    coloreados según el PASILLO de origen (en función de y inicial).

    df: DataFrame con eventos (formato Opta, x/y/end_x/end_y en [0,100])
    team_name: nombre del equipo (columna df['TeamName'])
    """

    # --- Definición de pasillos ---
    pasillos_y = {
        "Pasillo Central": (37, 63),
        "Pasillo Interior Izquierdo": (63, 79),
        "Pasillo Interior Derecho": (21, 37),
        "Pasillo Exterior Izquierdo": (79, 102),
        "Pasillo Exterior Derecho": (0, 21),
    }

    # Colores para cada pasillo
    PASILLO_COLORS = {
        "Pasillo Central":            "#FDD835",  # amarillo
        "Pasillo Interior Izquierdo": "#43A047",  # verde
        "Pasillo Interior Derecho":   "#1E88E5",  # azul
        "Pasillo Exterior Izquierdo": "#e53935",  # rojo
        "Pasillo Exterior Derecho":   "#8E24AA",  # violeta
    }

    # --- Filtro base: pases correctos del equipo que terminan entrando al área ---
    dfp = df.copy()
    dfp = dfp[
        (dfp[filter_col] == team_name) &
        (dfp["NaEventType"] == "Pass") &
        (dfp["corner_taken"].isna()) &
        (dfp["corner_taken"] != "-1") &
        (dfp["Outcome"] == 1)        # pase correcto
    ].copy()

    # Asegurar numéricos
    for c in ["x", "y", "end_x", "end_y"]:
        if c in dfp.columns:
            dfp[c] = pd.to_numeric(dfp[c], errors="coerce")

    # Termina dentro del área
    in_box_end = (
        (dfp["end_x"] >= box_min_x) &
        (dfp["end_y"] >= box_y_low) &
        (dfp["end_y"] <= box_y_high)
    )
    # No empieza ya dentro del área
    from_outside_box = ~(
        (dfp["x"] >= box_min_x) &
        (dfp["y"] >= box_y_low) &
        (dfp["y"] <= box_y_high)
    )

    dfp = dfp[in_box_end & from_outside_box].copy()

    if dfp.empty:
        print(f"⚠️ No hay ingresos al área para {team_name} con los filtros actuales.")
        return None, dfp

    # --- Asignar pasillo según y de origen ---
    def assign_corridor(y):
        for name, (y_min, y_max) in pasillos_y.items():
            if (y >= y_min) and (y < y_max):
                return name
        return None

    dfp["corridor"] = dfp["y"].apply(assign_corridor)
    dfp = dfp[dfp["corridor"].notna()].copy()

    if dfp.empty:
        print(f"⚠️ No hay ingresos con pasillo identificable para {team_name}.")
        return None, dfp

    pitch = Pitch(pitch_type="opta", stripe=False)
    fig, ax = pitch.draw(figsize=(12, 7))

    corridor_order = list(pasillos_y.keys())
    counts_corridor = {}

    for corridor_name in corridor_order:
        dfk = dfp[dfp["corridor"] == corridor_name]
        counts_corridor[corridor_name] = len(dfk)
        if dfk.empty:
            continue
        color = PASILLO_COLORS.get(corridor_name, "#000000")
        pitch.lines(
            dfk["x"], dfk["y"], dfk["end_x"], dfk["end_y"],
            color=color, comet=True, transparent=True,
            alpha_start=0.10, alpha_end=0.30, ax=ax, ls='dotted'
        )
        pitch.scatter(
            dfk["end_x"], dfk["end_y"], ax=ax, facecolor="white",
            edgecolor=color, linewidth=1.2, s=24, zorder=4,
        )

    # --- Líneas finas separando pasillos y mitad de campo ---
    for _, (y_min, y_max) in pasillos_y.items():
        ax.axhline(y=y_min, color="grey", linestyle="--", linewidth=0.7, alpha=0.6)
    ax.axhline(y=100, color="grey", linestyle="--", linewidth=0.7, alpha=0.6)
    ax.axvline(x=50, color="grey", linestyle="-", linewidth=1.0, alpha=0.8)

    # --- Contadores por pasillo ---
    for corridor_name in corridor_order:
        y_min, y_max = pasillos_y[corridor_name]
        y_mid = (y_min + y_max) / 2
        count = counts_corridor.get(corridor_name, 0)
        ax.text(
            10,
            y_mid,
            f"{count} Ingresos",
            ha="left",
            va="center",
            fontsize=11,
            color="black",
            bbox=dict(facecolor="white", alpha=0.7, edgecolor="none", boxstyle="round,pad=0.3"),
            zorder=5,
        )

    legend_items = [Line2D([0], [0], color=PASILLO_COLORS[name], lw=2, ls='dotted', label=name) for name in corridor_order]
    ax.legend(handles=legend_items, loc="lower right", frameon=True, facecolor="white", edgecolor="none", fontsize=10)

    total_entries = len(dfp)
    ax.set_title(f"{title_prefix} — {team_name}\nTotal: N={total_entries}", fontsize=14)
    plt.tight_layout()
    return fig, dfp

def plot_distribution_comparison(df, team_name, column, title, xaxis_title, filter_col='TeamName'):
    """
    Crea un gráfico de densidad para comparar la distribución de una columna
    entre el equipo seleccionado y el resto de la liga.
    """
    # Usamos el df global que ya está filtrado por fecha, etc.
    # Necesitamos una fila por posesión para no contar la misma duración/xg varias veces.
    df_poss = df.drop_duplicates(subset=['Posesion']).copy()
    df_poss = df_poss.dropna(subset=[column])

    if df_poss.empty:
        st.warning(f"No hay datos de posesión para la columna '{column}'.")
        return None

    # Crear una columna para diferenciar el equipo seleccionado del resto
    df_poss['Grupo'] = np.where(df_poss[filter_col] == team_name, team_name, 'Resto de la Liga')

    # Definir colores
    color_map = {
        team_name: '#EF553B',  # Naranja/Rojo de Plotly
        'Resto de la Liga': '#636EFA'  # Azul de Plotly
    }

    # Crear el gráfico de densidad con Plotly Express
    fig = px.histogram(
        df_poss,
        x=column,
        color='Grupo',
        color_discrete_map=color_map,
        histnorm='probability density',  # Esto crea un gráfico de densidad
        barmode='overlay',               # Superponer las distribuciones
        marginal='rug',                  # Añade 'rugs' para ver puntos de datos individuales
        opacity=0.6,
        template="plotly_white"
    )

    fig.update_layout(
        title_text=title,
        xaxis_title_text=xaxis_title,
        yaxis_title_text='Densidad',
        legend_title_text='Comparativa'
    )

    return fig

def plot_area_entry_drives(
    df,
    team_name,
    filter_col='TeamName',
    title_prefix="Conducciones en Campo Rival"
):
    """
    Dibuja las conducciones que suponen un ingreso al área rival para un equipo dado, originadas en campo rival.
    La opacidad de la línea varía según el 'possession_xg'.
    """
    dfp = df.copy()
    dfp = dfp[
        (dfp[filter_col] == team_name) &
        (dfp["NaEventType"] == "BallDrive") &
        (dfp["x"] > 50) &
        (dfp["end_x"] > dfp["x"]) &
        (dfp["Outcome"] == 1)
    ].copy()

    for c in ["x", "y", "end_x", "end_y", "possession_xg"]:
        if c in dfp.columns:
            dfp[c] = pd.to_numeric(dfp[c], errors="coerce")

    if dfp.empty:
        print(f"⚠️ No hay conducciones en campo rival para {team_name} con los filtros actuales.")
        return None, dfp

    # Normalizar possession_xg para usarlo como alpha (opacidad)
    # Se suma un pequeño epsilon para evitar división por cero si todos los xg son iguales.
    min_xg = dfp['possession_xg'].min()
    max_xg = dfp['possession_xg'].max()
    if max_xg > min_xg:
        dfp['alpha'] = 0.2 + 0.8 * (dfp['possession_xg'] - min_xg) / (max_xg - min_xg)
    else:
        dfp['alpha'] = 0.5 # Usar un alpha fijo si no hay variación

    dfp['alpha'] = dfp['alpha'].fillna(0.2) # Rellenar NaNs con un alpha bajo

    pitch = Pitch(pitch_type="opta", stripe=False)
    fig, ax = pitch.draw(figsize=(12, 7))

    # Iterar sobre cada conducción para dibujarla con su alpha correspondiente
    for row in dfp.itertuples():
        pitch.lines(
            row.x, row.y, row.end_x, row.end_y,
            color="#BD73DC",
            lw=2, # Ancho de línea fijo
            alpha=row.alpha, # Usar el alpha calculado
            ax=ax,
            zorder=3
        )

    # Dibujar los puntos finales de las conducciones
    pitch.scatter(
        dfp["end_x"], dfp["end_y"],
        ax=ax,
        facecolor="white",
        edgecolor="#BD73DC",
        linewidth=1.2,
        s=24,
        zorder=4,
    )

    legend_items = [Line2D([0], [0], color="#BD73DC", lw=2, label='Conducción (opacidad por xG)')]
    ax.legend(handles=legend_items, loc="lower left", frameon=True, facecolor="white", edgecolor="none", fontsize=11)

    ax.set_title(
        f"{title_prefix} — {team_name}\nTotal: N={len(dfp)}",
        fontsize=14,
    )
    plt.tight_layout()
    return fig, dfp

def plot_area_entry_drives_by_corridor(
    df,
    team_name,
    filter_col='TeamName',
    title_prefix="Conducciones en Campo Rival por Pasillo"
):
    """
    Dibuja las conducciones que suponen un ingreso al área rival, coloreadas por pasillo de origen y originadas en campo rival.
    """
    pasillos_y = {
        "Pasillo Central": (37, 63), "Pasillo Interior Izquierdo": (63, 79),
        "Pasillo Interior Derecho": (21, 37), "Pasillo Exterior Izquierdo": (79, 102),
        "Pasillo Exterior Derecho": (0, 21),
    }
    PASILLO_COLORS = {
        "Pasillo Central": "#FDD835", "Pasillo Interior Izquierdo": "#43A047",
        "Pasillo Interior Derecho": "#1E88E5", "Pasillo Exterior Izquierdo": "#e53935",
        "Pasillo Exterior Derecho": "#8E24AA",
    }

    dfp = df.copy()
    dfp = dfp[
        (dfp[filter_col] == team_name) &
        (dfp["NaEventType"] == "BallDrive") &
        (dfp["x"] > 50) & # <--- AÑADIDO: Filtrar por inicio en campo rival
        (dfp["end_x"] > dfp["x"]) &
        (dfp["Outcome"] == 1)
    ].copy()

    for c in ["x", "y", "end_x", "end_y"]:
        if c in dfp.columns:
            dfp[c] = pd.to_numeric(dfp[c], errors="coerce")

    if dfp.empty:
        print(f"⚠️ No hay ingresos al área por conducción desde campo rival para {team_name} con los filtros actuales.")
        return None, dfp

    def assign_corridor(y):
        for name, (y_min, y_max) in pasillos_y.items():
            if (y >= y_min) and (y < y_max):
                return name
        return None

    dfp["corridor"] = dfp["y"].apply(assign_corridor)
    dfp = dfp[dfp["corridor"].notna()].copy()

    if dfp.empty:
        print(f"⚠️ No hay ingresos por conducción con pasillo identificable para {team_name}.")
        return None, dfp

    pitch = Pitch(pitch_type="opta", stripe=False)
    fig, ax = pitch.draw(figsize=(12, 7))

    corridor_order = list(pasillos_y.keys())
    counts_corridor = {}

    for corridor_name in corridor_order:
        dfk = dfp[dfp["corridor"] == corridor_name]
        counts_corridor[corridor_name] = len(dfk)
        if dfk.empty:
            continue
        color = PASILLO_COLORS.get(corridor_name, "#000000")
        pitch.lines(
            dfk["x"], dfk["y"], dfk["end_x"], dfk["end_y"],
            color=color, comet=True, transparent=True,
            alpha_start=0.10, alpha_end=0.30, ax=ax, ls='dotted'
        )
        pitch.scatter(
            dfk["end_x"], dfk["end_y"], ax=ax, facecolor="white",
            edgecolor=color, linewidth=1.2, s=24, zorder=4,
        )

    # --- Líneas finas separando pasillos y mitad de campo ---
    for _, (y_min, y_max) in pasillos_y.items():
        ax.axhline(y=y_min, color="grey", linestyle="--", linewidth=0.7, alpha=0.6)
    ax.axhline(y=100, color="grey", linestyle="--", linewidth=0.7, alpha=0.6)
    ax.axvline(x=50, color="grey", linestyle="-", linewidth=1.0, alpha=0.8)

    # --- Contadores por pasillo ---
    for corridor_name in corridor_order:
        y_min, y_max = pasillos_y[corridor_name]
        y_mid = (y_min + y_max) / 2
        count = counts_corridor.get(corridor_name, 0)
        ax.text(
            10,
            y_mid,
            f"{count} conducciones",
            ha="left",
            va="center",
            fontsize=11,
            color="black",
            bbox=dict(facecolor="white", alpha=0.7, edgecolor="none", boxstyle="round,pad=0.3"),
            zorder=5,
        )

    legend_items = [Line2D([0], [0], color=PASILLO_COLORS[name], lw=2, ls='dotted', label=name) for name in corridor_order]
    ax.legend(handles=legend_items, loc="lower right", frameon=True, facecolor="white", edgecolor="none", fontsize=10)

    total_entries = len(dfp)
    ax.set_title(f"{title_prefix} — {team_name}\nTotal: N={total_entries}", fontsize=14)
    plt.tight_layout()
    return fig, dfp

# Definición de zonas de disparo basadas en las líneas del código original
zone_areas = {
    'Zona 1': {'x_lower_bound': 0, 'x_upper_bound': 21.1, 'y_lower_bound': 66.6, 'y_upper_bound': 83},
    'Zona 2': {'x_lower_bound': 21.1, 'x_upper_bound': 36.8, 'y_lower_bound': 66.6, 'y_upper_bound': 83},
    'Zona 3': {'x_lower_bound': 36.8, 'x_upper_bound': 63.2, 'y_lower_bound': 66.6, 'y_upper_bound': 83},
    'Zona 4': {'x_lower_bound': 63.2, 'x_upper_bound': 78.9, 'y_lower_bound': 66.6, 'y_upper_bound': 83},
    'Zona 5': {'x_lower_bound': 78.9, 'x_upper_bound': 100, 'y_lower_bound': 66.6, 'y_upper_bound': 83},
    'Zona 6': {'x_lower_bound': 0, 'x_upper_bound': 21.1, 'y_lower_bound': 83, 'y_upper_bound': 94.2},
    'Zona 7': {'x_lower_bound': 21.1, 'x_upper_bound': 36.8, 'y_lower_bound': 83, 'y_upper_bound': 94.2},
    'Zona 8': {'x_lower_bound': 36.8, 'x_upper_bound': 63.2, 'y_lower_bound': 83, 'y_upper_bound': 94.2},
    'Zona 9': {'x_lower_bound': 63.2, 'x_upper_bound': 78.9, 'y_lower_bound': 83, 'y_upper_bound': 94.2},
    'Zona 10': {'x_lower_bound': 78.9, 'x_upper_bound': 100, 'y_lower_bound': 83, 'y_upper_bound': 94.2},
    'Zona 11': {'x_lower_bound': 0, 'x_upper_bound': 21.1, 'y_lower_bound': 94.2, 'y_upper_bound': 100},
    'Zona 12': {'x_lower_bound': 21.1, 'x_upper_bound': 36.8, 'y_lower_bound': 94.2, 'y_upper_bound': 100},
    'Zona 13': {'x_lower_bound': 36.8, 'x_upper_bound': 63.2, 'y_lower_bound': 94.2, 'y_upper_bound': 100},
    'Zona 14': {'x_lower_bound': 63.2, 'x_upper_bound': 78.9, 'y_lower_bound': 94.2, 'y_upper_bound': 100},
    'Zona 15': {'x_lower_bound': 78.9, 'x_upper_bound': 100, 'y_lower_bound': 94.2, 'y_upper_bound': 100},
}

# Constantes para los gráficos de disparos
SHOT_EVENTS = ['Goal', 'Attempt Saved', 'Miss', 'Post']
DEFAULT_XG = 0.1
MIN_PCT_THRESHOLD = 0.001
HIGH_PCT_THRESHOLD = 0.075
XG_SIZE_MULTIPLIER = 750
ZONE_LINE_WIDTH = 1.5

def assign_shot_zone(y, x):
    """
    Asigna una zona de disparo basada en las coordenadas y (ancho) y x (profundidad).
    Nota: En VerticalPitch, y es el ancho y x es la profundidad.
    """
    for zone_name, bounds in zone_areas.items():
        if (bounds['x_lower_bound'] <= y < bounds['x_upper_bound'] and
            bounds['y_lower_bound'] <= x < bounds['y_upper_bound']):
            return zone_name
    return 'Zona Desconocida'

def _filter_and_prepare_shots_data(df, team_name=None, player_name=None, filter_col='TeamName'):
    """
    Filtra y prepara los datos de disparos.
    
    Returns:
    --------
    tuple: (df_filtered, team_name) donde df_filtered es el dataframe preparado
    """
    # Detectar equipo si no se proporciona
    if team_name is None:
        unique_teams = df[filter_col].dropna().unique()
        if len(unique_teams) == 1:
            team_name = unique_teams[0]
            df_filtered = df.copy()
        else:
            df_filtered = df.copy()
    else:
        df_filtered = df[df[filter_col] == team_name].copy()
    
    # Filtrar por jugador
    if player_name and player_name != "Todos":
        df_filtered = df_filtered[df_filtered['NaPlayer'] == player_name].copy()
    
    # Filtrar eventos de tiro
    df_filtered = df_filtered[df_filtered['NaEventType'].isin(SHOT_EVENTS)].copy()
    
    if df_filtered.empty:
        return None, team_name
    
    # Preparar columnas necesarias
    df_filtered = df_filtered.copy()
    df_filtered['outcome'] = (df_filtered['NaEventType'] == 'Goal').astype(int)
    
    # Normalizar xg
    if 'xg' not in df_filtered.columns:
        df_filtered['xg'] = DEFAULT_XG
    df_filtered['xg'] = pd.to_numeric(df_filtered['xg'], errors='coerce').fillna(DEFAULT_XG)
    
    # Asignar zonas de forma más eficiente
    df_filtered['zone_area'] = df_filtered.apply(
        lambda row: assign_shot_zone(row['y'], row['x']), axis=1
    )
    
    return df_filtered, team_name

def _draw_zone_delimiter_lines(ax):
    """Dibuja las líneas delimitadoras de zonas."""
    ax.plot([21.1, 21.1], [66.6, 100], ls=':', color='black', linewidth=ZONE_LINE_WIDTH)
    ax.plot([78.9, 78.9], [66.6, 100], ls=':', color='black', linewidth=ZONE_LINE_WIDTH)
    ax.plot([36.8, 36.8], [66.6, 100], ls=':', color='black', linewidth=ZONE_LINE_WIDTH)
    ax.plot([63.2, 63.2], [66.6, 100], ls=':', color='black', linewidth=ZONE_LINE_WIDTH)
    ax.plot([0, 100], [83, 83], ls=':', color='black', linewidth=ZONE_LINE_WIDTH)
    ax.plot([36.8, 63.2], [94.2, 94.2], ls=':', color='black', linewidth=ZONE_LINE_WIDTH)
    ax.plot([0, 100], [66.6, 66.6], ls=':', color='black', linewidth=ZONE_LINE_WIDTH)

def _draw_zones_heatmap(ax, df, use_adaptive_text_color=True):
    """
    Dibuja el mapa de zonas coloreado según porcentaje de disparos.
    
    Parameters:
    -----------
    ax : matplotlib.axes.Axes
        Eje donde dibujar
    df : DataFrame
        DataFrame con columnas 'zone_area', 'y', 'x'
    use_adaptive_text_color : bool
        Si True, adapta el color del texto según el porcentaje
    """
    # Calcular estadísticas por zona
    zone_stats = df.groupby('zone_area').size().reset_index(name='count')
    zone_stats['pct'] = zone_stats['count'] / len(df)
    
    if zone_stats.empty:
        return
    
    max_pct = zone_stats['pct'].max() if zone_stats['pct'].max() > 0 else 1.0
    
    # Dibujar cancha
    pitch = VerticalPitch(pitch_type='opta', half=True, pitch_color='#22312b', line_color='white')
    pitch.draw(ax=ax)
    ax.set_facecolor('#22312b')
    
    # Colorear zonas
    for _, row in zone_stats.iterrows():
        zone = row['zone_area']
        shot_pct = row['pct']
        
        if zone not in zone_areas:
            continue
        
        bounds = zone_areas[zone]
        x_lim = [bounds['x_lower_bound'], bounds['x_upper_bound']]
        y1, y2 = bounds['y_lower_bound'], bounds['y_upper_bound']
        
        # Rellenar zona
        ax.fill_between(
            x=x_lim, y1=y1, y2=y2,
            color='green',
            alpha=(shot_pct / max_pct) if max_pct > 0 else 0.1,
            zorder=0, ec='None'
        )
        
        # Texto con porcentaje
        if shot_pct >= MIN_PCT_THRESHOLD:
            if use_adaptive_text_color:
                color_text = 'white' if shot_pct > HIGH_PCT_THRESHOLD else 'black'
                fore_color = 'black' if shot_pct > HIGH_PCT_THRESHOLD else 'white'
            else:
                color_text = 'white'
                fore_color = 'black'
            
            x_pos = x_lim[0] + (x_lim[1] - x_lim[0]) / 2
            y_pos = y1 + (y2 - y1) / 2
            
            txt = ax.annotate(
                xy=(x_pos, y_pos),
                text=f'{shot_pct:.0%}',
                ha='center', va='center',
                color=color_text, weight='bold', size=12
            )
            txt.set_path_effects([
                pe.Stroke(linewidth=1.5, foreground=fore_color),
                pe.Normal()
            ])
    
    # Líneas delimitadoras
    _draw_zone_delimiter_lines(ax)

def _draw_shots_scatter(ax, df):
    """Dibuja los disparos (gol / no gol) sobre la mitad de la cancha."""
    pitch = VerticalPitch(pitch_type='opta', half=True, pitch_color='#22312b', line_color='white')
    pitch.draw(ax=ax)
    ax.set_facecolor('#22312b')
    
    # Separar goles y no goles
    no_gol = df[df['outcome'] == 0]
    gol = df[df['outcome'] == 1]
    
    # Dibujar no goles
    if not no_gol.empty:
        ax.scatter(
            no_gol['y'], no_gol['x'],
            color='red',
            s=no_gol['xg'] * XG_SIZE_MULTIPLIER,
            edgecolors='black', alpha=0.4, label='No gol',
            zorder=3
        )
    
    # Dibujar goles
    if not gol.empty:
        ax.scatter(
            gol['y'], gol['x'],
            color='green',
            s=gol['xg'] * XG_SIZE_MULTIPLIER,
            edgecolors='black', alpha=1, label='Gol',
            zorder=3
        )
    
    ax.legend(loc='lower center', ncols=2, fontsize=15, facecolor='white', edgecolor='none')

def _draw_empty_pitch(ax, title_text):
    """Dibuja una cancha vacía con un título."""
    pitch = VerticalPitch(pitch_type='opta', half=True, pitch_color='#22312b', line_color='white')
    pitch.draw(ax=ax)
    ax.set_facecolor('#22312b')
    ax.set_title(title_text, fontsize=16, color='white', fontweight='bold')

def plot_team_shots(df, team_name=None, player_name=None, filter_col='TeamName'):
    """
    Crea un gráfico de dos paneles mostrando:
    1. Zonas de disparo con porcentajes
    2. Scatter plot de tiros (goles vs no goles)
    
    Parameters:
    -----------
    df : DataFrame
        DataFrame con los eventos (puede estar ya filtrado por otros criterios)
    team_name : str, optional
        Nombre del equipo. Si es None, verifica si el df ya tiene un solo equipo o usa todo el dataset
    player_name : str, optional
        Nombre del jugador. Si es None, muestra todos los jugadores
    filter_col : str
        Columna para filtrar por equipo (default: 'TeamName')
    
    Returns:
    --------
    fig : matplotlib.figure.Figure
        Figura con los dos gráficos
    """
    # Filtrar y preparar datos
    tiros_df, team_name = _filter_and_prepare_shots_data(df, team_name, player_name, filter_col)
    
    if tiros_df is None or tiros_df.empty:
        return None
    
    # Crear figura
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 9))
    fig.set_facecolor('#101820')
    
    # Panel 1: Zonas de disparo
    _draw_zones_heatmap(ax1, tiros_df, use_adaptive_text_color=False)
    ax1.set_title(
        f"Ubicaciones en zonas de los tiros. Cantidad: {len(tiros_df)}",
        fontsize=22, fontweight='bold', color='white'
    )
    
    # Panel 2: Scatter plot
    _draw_shots_scatter(ax2, tiros_df)
    ax2.set_title(
        "Distribución de tiros por resultado",
        fontsize=22, fontweight='bold', color='white'
    )
    
    plt.tight_layout()
    return fig

# Funciones auxiliares para set_piece (usando las funciones unificadas)
def _draw_zones_set_piece(ax, df):
    """Dibuja el mapa de zonas coloreado según porcentaje de disparos."""
    _draw_zones_heatmap(ax, df, use_adaptive_text_color=True)

def _draw_scatter_set_piece(ax, df):
    """Dibuja los disparos (gol / no gol) sobre la mitad de la cancha."""
    _draw_shots_scatter(ax, df)

def plot_set_piece_shots(df, team_name=None, player_name=None, filter_col='TeamName'):
    """
    Crea un gráfico 2x2 mostrando disparos en pelota parada:
    - Fila 1: Córners (zonas y scatter)
    - Fila 2: Resto de jugadas de pelota parada (zonas y scatter)
    
    Parameters:
    -----------
    df : DataFrame
        DataFrame con los eventos (puede estar ya filtrado por otros criterios)
    team_name : str, optional
        Nombre del equipo. Si es None, verifica si el df ya tiene un solo equipo o usa todo el dataset
    player_name : str, optional
        Nombre del jugador. Si es None, muestra todos los jugadores
    filter_col : str
        Columna para filtrar por equipo (default: 'TeamName')
    
    Returns:
    --------
    fig : matplotlib.figure.Figure
        Figura con los cuatro gráficos
    """
    # Filtrar y preparar datos
    tiros_df, team_name = _filter_and_prepare_shots_data(df, team_name, player_name, filter_col)
    
    if tiros_df is None or tiros_df.empty:
        return None
    
    # Separar por tipo de jugada
    corner_df = tiros_df[tiros_df['play_type'] == 'From_corner'].copy()
    rest_df = tiros_df[tiros_df['play_type'].isin(['Free_kick', 'Set_piece', 'Throw-in_set_piece'])].copy()
    
    # Calcular estadísticas de forma más eficiente
    def _calc_stats(df_subset):
        if df_subset.empty:
            return {'xg': 0.0, 'shots': 0, 'goals': 0}
        return {
            'xg': round(df_subset['xg'].sum(), 2),
            'shots': len(df_subset),
            'goals': int(df_subset['outcome'].sum())
        }
    
    corner_stats = _calc_stats(corner_df)
    rest_stats = _calc_stats(rest_df)
    
    # Crear figura 2x2
    fig, axes = plt.subplots(2, 2, figsize=(20, 18))
    fig.set_facecolor('#101820')
    (ax1, ax2), (ax3, ax4) = axes
    
    # Título general
    title_parts = [f"Disparos de {team_name if team_name else 'Todos los equipos'}"]
    if player_name and player_name != "Todos":
        title_parts.append(f" - {player_name}")
    title_parts.append(" en pelota parada\n")
    title_parts.append(
        f"Córners – xG: {corner_stats['xg']} | Tiros: {corner_stats['shots']} | Goles: {corner_stats['goals']}\n"
    )
    title_parts.append(
        f"Resto – xG: {rest_stats['xg']} | Tiros: {rest_stats['shots']} | Goles: {rest_stats['goals']}"
    )
    
    fig.suptitle(''.join(title_parts), fontsize=24, fontweight="bold", color='white')
    
    # Primera fila: córners
    if not corner_df.empty:
        _draw_zones_set_piece(ax1, corner_df)
        ax1.set_title("Córners – Zonas", fontsize=16, color='white', fontweight='bold')
        _draw_scatter_set_piece(ax2, corner_df)
        ax2.set_title("Disparos (córners)", fontsize=16, color='white', fontweight='bold')
    else:
        _draw_empty_pitch(ax1, "Córners – Zonas (Sin datos)")
        _draw_empty_pitch(ax2, "Disparos (córners) (Sin datos)")
    
    # Segunda fila: resto de jugadas
    if not rest_df.empty:
        _draw_zones_set_piece(ax3, rest_df)
        ax3.set_title("Resto de jugadas – Zonas", fontsize=16, color='white', fontweight='bold')
        _draw_scatter_set_piece(ax4, rest_df)
        ax4.set_title("Disparos (resto)", fontsize=16, color='white', fontweight='bold')
    else:
        _draw_empty_pitch(ax3, "Resto de jugadas – Zonas (Sin datos)")
        _draw_empty_pitch(ax4, "Disparos (resto) (Sin datos)")
    
    plt.tight_layout()
    return fig

def plot_crosses_analysis(df, team_name=None, filter_col='TeamName'):
    """
    Crea un gráfico 2x2 mostrando análisis de centros:
    - Fila 1: Origen y destino de centros incompletos (Outcome == 0)
    - Fila 2: Origen y destino de centros completos (Outcome == 1)
    
    Parameters:
    -----------
    df : DataFrame
        DataFrame con los eventos (puede estar ya filtrado por otros criterios)
    team_name : str, optional
        Nombre del equipo. Si es None, verifica si el df ya tiene un solo equipo
    filter_col : str
        Columna para filtrar por equipo (default: 'TeamName')
    
    Returns:
    --------
    fig : matplotlib.figure.Figure
        Figura con los cuatro gráficos
    """
    import matplotlib.gridspec as gridspec
    
    # Detectar equipo si no se proporciona
    if team_name is None:
        unique_teams = df[filter_col].dropna().unique()
        if len(unique_teams) == 1:
            team_name = unique_teams[0]
            df_filtered = df.copy()
        else:
            df_filtered = df.copy()
    else:
        df_filtered = df[df[filter_col] == team_name].copy()
    
    # Filtrar centros (cross == '-1' o cross.notna())
    df_centros = df_filtered[
        (df_filtered['cross'] == '-1') | (df_filtered['cross'].notna())
    ].copy()
    
    if df_centros.empty:
        return None
    
    # Obtener eventos únicos
    base_df = df_centros.drop_duplicates('IdEvent').copy()
    
    if base_df.empty:
        return None
    
    # Crear figura con GridSpec 2x2
    fig = plt.figure(figsize=(18, 12))
    gs = gridspec.GridSpec(2, 2, figure=fig)
    axes = [fig.add_subplot(gs[i, j]) for i in range(2) for j in range(2)]
    
    pitch = VerticalPitch(pitch_type='opta', half=True)
    
    # Definir filtros para cada subplot
    incompletos = base_df[base_df['Outcome'] == 0]
    completos = base_df[base_df['Outcome'] == 1]
    
    filtros = {
        f"De donde vinieron los centros (incompletos) | {len(incompletos)} total": {
            "df": incompletos,
            "cols": ("x", "y")
        },
        "Donde terminaron (incompletos)": {
            "df": incompletos,
            "cols": ("end_x", "end_y")
        },
        f"De donde vinieron los centros (completos) | {len(completos)} total": {
            "df": completos,
            "cols": ("x", "y")
        },
        "Donde terminaron (completos)": {
            "df": completos,
            "cols": ("end_x", "end_y")
        }
    }
    
    # Dibujar cada cancha
    for ax, (titulo, info) in zip(axes, filtros.items()):
        df_subset = info["df"]
        x_col, y_col = info["cols"]
        
        if df_subset.empty:
            pitch.draw(ax=ax)
            ax.set_facecolor('#22312b')
            ax.set_title(titulo, fontsize=14)
            continue
        
        # Asignar zonas
        df_subset = df_subset.copy()
        df_subset['zone_area'] = df_subset.apply(
            lambda row: assign_shot_zone(row[y_col], row[x_col]), axis=1
        )
        
        # Calcular estadísticas por zona
        zone_stats = df_subset.groupby('zone_area').size().reset_index(name='count')
        zone_stats['pct'] = zone_stats['count'] / len(df_subset)
        
        max_pct = zone_stats['pct'].max() if zone_stats['pct'].max() > 0 else 1.0
        
        # Dibujar cancha
        pitch.draw(ax=ax)
        ax.set_facecolor('white')
        
        # Dibujar puntos de centros
        pitch.scatter(
            df_subset[x_col],
            df_subset[y_col],
            ax=ax,
            zorder=2,
            color='green',
            edgecolor='black',
            alpha=0.6
        )
        
        # Colorear zonas
        for _, row in zone_stats.iterrows():
            zone = row['zone_area']
            shot_pct = row['pct']
            
            if zone not in zone_areas:
                continue
            
            bounds = zone_areas[zone]
            x_lim = [bounds['x_lower_bound'], bounds['x_upper_bound']]
            y1, y2 = bounds['y_lower_bound'], bounds['y_upper_bound']
            
            ax.fill_between(
                x=x_lim,
                y1=y1,
                y2=y2,
                color='green',
                alpha=(shot_pct / max_pct) if max_pct > 0 else 0.1,
                zorder=0,
                ec='None'
            )
            
            # Texto en el centro de cada zona
            if shot_pct >= MIN_PCT_THRESHOLD:
                if shot_pct > HIGH_PCT_THRESHOLD:
                    color_text = 'white'
                    fore_color = 'black'
                else:
                    color_text = 'black'
                    fore_color = 'white'
                
                x_pos = x_lim[0] + (x_lim[1] - x_lim[0]) / 2
                y_pos = y1 + (y2 - y1) / 2
                
                text_ = ax.annotate(
                    xy=(x_pos, y_pos),
                    text=f'{shot_pct:.0%}',
                    ha='center',
                    va='center',
                    color=color_text,
                    weight='bold',
                    size=12
                )
                text_.set_path_effects([
                    pe.Stroke(linewidth=1.5, foreground=fore_color),
                    pe.Normal()
                ])
        
        # Líneas delimitadoras
        _draw_zone_delimiter_lines(ax)
        
        ax.set_title(titulo, fontsize=14)
    
    plt.tight_layout()
    return fig