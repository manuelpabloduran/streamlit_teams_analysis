import pandas as pd
import numpy as np

def preprocess_data(df):
    """
    Aplica un pipeline de pre-procesamiento para calcular el tipo de posesión.
    """
    # --- Inicio del Pipeline ---

    # Copia para evitar SettingWithCopyWarning
    df = df.copy()

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

    # --- Cálculo de variables adicionales (a nivel de evento) ---
    df['dx'] = df['end_x'] - df['x']
    df['dy'] = df['end_y'] - df['y']
    df['Angle'] = np.arctan2(df['dy'], df['dx']).mod(2 * np.pi)

    # --- Cálculo de variables adicionales (a nivel de posesión) ---
    # Duración de la posesión
    possession_duration = df.groupby('Posesion')['time_seconds'].transform(lambda x: x.max() - x.min())
    possession_counts = df.groupby('Posesion')['time_seconds'].transform('count')
    df['possession_duration'] = possession_duration.where(possession_counts > 1, np.nan)
    df['possession_duration'] = df['possession_duration'].clip(upper=100)

    # xG de la posesión
    df['possession_xg'] = df.groupby('Posesion')['xg'].transform('sum')
    df['possession_xg'] = df['possession_xg'].clip(upper=1)

    df['iniciacion_area'] = np.where(((df["x"] >= 84) &
                                                 (df["y"] <= 81) &
                                                 (df["y"] >= 19)), 1, 0)

    df['finalizacion_area'] = np.where(((df["end_x"] >= 84) &
                                                 (df["end_y"] <= 81) &
                                                 (df["end_y"] >= 19)), 1, 0)

    df['pase_peligroso_al_area'] = np.where(((df["iniciacion_area"] == 0) &
                                                       (df["end_x"] >= 84) &
                                                       (df["end_y"] <= 81) &
                                                       (df["end_y"] >= 19)), 1, 0)

    # AGREGAMOS CUTBACKS AL ANÁLISIS
    df['cutback'] = np.where(((df["NaEventType"]=="Pass") &
                                (df["finalizacion_area"]==1) &
                                (df["x"]>80) &
                                (df["y"]<=37) &
                                (df["Angle"]>1.57) &
                                (df["Angle"]<3.14)) |
                                ((df["NaEventType"]=="Pass") &
                                 (df["finalizacion_area"]==1) &
                                 (df["chipped"].isna()) &
                                 (df["Outcome"]==1) &
                                 (df["x"]>80) &
                                 (df["y"]>=63) &
                                 (df["Angle"]>3.14) &
                                 (df["Angle"]<4.71)), 1, 0)

    df['dividido'] = np.where(((df["NaEventType"]=="Pass") &
                                             (df["finalizacion_area"]==1) &
                                             (df["x"]>80) &
                                             (df["y"]<=37) &
                                             (df["Angle"]>0) &
                                             (df["Angle"]<1.57)) |
                                ((df["NaEventType"]=="Pass") &
                                 (df["finalizacion_area"]==1) &
                                 (df["chipped"].isna()) &
                                 (df["Outcome"]==1) &
                                 (df["x"]>80) &
                                 (df["y"]>=63) &
                                 (df["Angle"]>4.71) &
                                 (df["Angle"]<6.28)), 1, 0)

    # --- Conversión y filtro de fecha ---
    df['DtGame'] = pd.to_datetime(df['DtGame']).dt.date

    # 1. Filtrar para quedarse con todas las filas de los grupos (TeamName, Posesion) que tienen un evento de remate
    shot_events = ['Goal', 'Attempt Saved', 'Miss', 'Post']
    df_shots_filtered = df.groupby(['TeamName', 'Posesion']).filter(lambda g: g['NaEventType'].isin(shot_events).any()).copy()

    # 2. Filtrar por posesiones con al menos un evento de juego regular
    posesiones_regulares = df_shots_filtered[df_shots_filtered['Regular_play'] == 1]['Posesion'].unique()
    df_filtered = df_shots_filtered[df_shots_filtered['Posesion'].isin(posesiones_regulares)].copy()

    # Ordenar los datos
    df_filtered = df_filtered.sort_values(by=['time_seconds', 'IdFrame'])

    # Definir qué es un pase (no longball y no chipped)
    is_pass = (df_filtered['NaEventType'] == 'Pass') & (df_filtered['long_ball'] != -1) & (df_filtered['chipped'] != -1)

    # 3. Calcular métricas por posesión
    possession_metrics = df_filtered.groupby(['Posesion']).agg(
        total_time=('time_seconds', lambda x: x.max() - x.min()),
        total_actions=('x', 'count'),
        actions_x_le_20=('x', lambda x: (x <= 20).sum()),
        passes_x_20_40=('x', lambda s: (is_pass[s.index] & (s > 20) & (s <= 40)).sum()),
        passes_x_gt_40=('x', lambda s: (is_pass[s.index] & (s > 40)).sum()),
        total_passes=('NaEventType', lambda s: (s == 'Pass').sum()),
        min_x=('x', 'min'),
        includes_counterpress=('counterpress_5s_flag', lambda s: 1 if (s == 1).any() else 0),
        includes_long_ball_from_defense=('x', lambda s: 1 if (
            (df_filtered.loc[s.index, 'long_ball'] == 1) & 
            (df_filtered.loc[s.index, 'chipped'].isna()) & 
            (s <= 30)
        ).any() else 0),
        high_recovery_start=('x', lambda s: 1 if (
            (df_filtered.loc[s.index, 'NaEventType'].isin(['Ball recovery', 'Ball touch', 'Tackle', 'Interception', 'Blocked Pass'])) &
            (df_filtered.loc[s.index, 'Outcome'] == 1) &
            (s >= 60)
        ).any() else 0)
    ).reset_index()

    # 4. Función para categorizar la posesión
    def categorize_possession(row):
        if row['total_time'] == 0 and row['total_actions'] == 1:
            return 'Una acción tras ruido'

        le_20 = row['actions_x_le_20']
        x_20_40 = row['passes_x_20_40']
        gt_40 = row['passes_x_gt_40']

        category = 'Otro'
        if le_20 >= 1 and le_20 >= x_20_40 and le_20 > gt_40:
            category = 'Superar Presiones'
        elif x_20_40 >= 1 and x_20_40 > le_20 and x_20_40 >= gt_40:
            category = 'Ataque a bloque medio'
        elif gt_40 >= 1 and gt_40 > le_20 and gt_40 > x_20_40:
            category = 'Atacando bloque bajo'

        if row['includes_counterpress'] == 1 or row['high_recovery_start'] == 1:
            category = 'Recuperación Alta'
            
        if category == 'Otro':
            return 'Otra Posesión'
        
        return category

    possession_metrics['possession_type'] = possession_metrics.apply(categorize_possession, axis=1)

    # 5. Asignar las categorías al DataFrame original
    df_final = pd.merge(df, possession_metrics[['Posesion', 'possession_type']], on='Posesion', how='left')

    # Para las posesiones no categorizadas (sin Regular_play), usar el valor de 'play_type'
    df_final['possession_type'] = df_final['possession_type'].fillna(df_final['play_type'])

    return df_final
