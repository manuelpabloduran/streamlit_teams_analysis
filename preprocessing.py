import pandas as pd
import numpy as np

def refine_set_pieces(df):
    """
    Refina el 'possession_type' para jugadas a balón parado basándose en reglas específicas.
    """
    # Obtener las posesiones que no fueron categorizadas por la lógica de juego regular.
    uncategorized_mask = df['possession_type'].isna()
    uncategorized_possessions = df[uncategorized_mask]['Posesion'].unique()

    # Creamos un diccionario para mapear Posesion -> nuevo_tipo
    new_types_map = {}

    # Agrupamos el dataframe original por 'Posesion' una sola vez para eficiencia
    grouped_df = df.sort_values(by=['Posesion', 'time_seconds', 'IdFrame']).groupby('Posesion')

    for poss_id in uncategorized_possessions:
        possession_group = grouped_df.get_group(poss_id)
        play_type = possession_group['play_type'].iloc[0]
        
        # Valor por defecto es el play_type original
        new_type = play_type

        # Lógica para Córners
        if play_type in ['Corner', 'From_corner']:
            corner_event = possession_group[possession_group['corner_taken'] == -1]
            if corner_event.empty:
                new_type = "Segunda Jugada"
            else:
                event_row = corner_event.iloc[0]
                if event_row['in_swinger'] == -1:
                    new_type = "Centro Cerrado"
                elif event_row['out_swing'] == -1:
                    new_type = "Centro Abierto"
                elif pd.isna(event_row['cross']) or event_row['cross'] != -1:
                    new_type = "Saque en corto"
        
        # Lógica para Tiros Libres
        elif play_type == 'Free_kick':
            new_type = "Tiro Directo"

        # Lógica para Otras Jugadas a Balón Parado
        elif play_type == 'Set_piece':
            set_piece_event = possession_group[possession_group['Set_piece'] == -1]
            if 'Pass' not in possession_group['NaEventType'].values:
                new_type = "Segunda Jugada"
            elif not set_piece_event.empty:
                event_row = set_piece_event.iloc[0]
                if event_row['in_swinger'] == -1:
                    new_type = "Centro Cerrado"
                elif event_row['out_swing'] == -1:
                    new_type = "Centro Abierto"
                elif pd.isna(event_row['cross']) or event_row['cross'] != -1:
                    new_type = "Saque en corto"
            else:
                new_type = "Segunda Jugada" # Fallback si no se encuentra el evento principal

        # Lógica para Saques de Banda
        elif play_type == 'Throw-in_set_piece':
            if 'Pass' in possession_group['NaEventType'].values:
                new_type = "Indirecto"
            else:
                new_type = "Directo"
        
        new_types_map[poss_id] = new_type

    # Mapeamos los nuevos tipos a la columna 'possession_type'
    # Usamos el 'possession_type' existente si no está en el mapa de nuevos tipos
    df['possession_type'] = df['Posesion'].map(new_types_map) #.fillna(df['possession_type'])
    
    return df


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
    possession_duration = df.groupby('Posesion')['time_seconds'].transform(lambda x: x.max() - x.min())
    possession_counts = df.groupby('Posesion')['time_seconds'].transform('count')
    df['possession_duration'] = possession_duration.where(possession_counts > 1, np.nan)
    df['possession_duration'] = df['possession_duration'].clip(upper=100)

    df['possession_xg'] = df.groupby('Posesion')['xg'].transform('sum')
    df['possession_xg'] = df['possession_xg'].clip(upper=1)

    df['iniciacion_area'] = np.where(((df["x"] >= 84) & (df["y"] <= 81) & (df["y"] >= 19)), 1, 0)
    df['finalizacion_area'] = np.where(((df["end_x"] >= 84) & (df["end_y"] <= 81) & (df["end_y"] >= 19)), 1, 0)
    df['pase_peligroso_al_area'] = np.where(((df["iniciacion_area"] == 0) & (df["end_x"] >= 84) & (df["end_y"] <= 81) & (df["end_y"] >= 19)), 1, 0)

    df['cutback'] = np.where(((df["NaEventType"]=="Pass") & (df["finalizacion_area"]==1) & (df["x"]>80) & (df["y"]<=37) & (df["Angle"]>1.57) & (df["Angle"]<3.14)) | ((df["NaEventType"]=="Pass") & (df["finalizacion_area"]==1) & (df["chipped"].isna()) & (df["Outcome"]==1) & (df["x"]>80) & (df["y"]>=63) & (df["Angle"]>3.14) & (df["Angle"]<4.71)), 1, 0)
    df['dividido'] = np.where(((df["NaEventType"]=="Pass") & (df["finalizacion_area"]==1) & (df["x"]>80) & (df["y"]<=37) & (df["Angle"]>0) & (df["Angle"]<1.57)) | ((df["NaEventType"]=="Pass") & (df["finalizacion_area"]==1) & (df["chipped"].isna()) & (df["Outcome"]==1) & (df["x"]>80) & (df["y"]>=63) & (df["Angle"]>4.71) & (df["Angle"]<6.28)), 1, 0)

    df['DtGame'] = pd.to_datetime(df['DtGame']).dt.date

    # 1. Filtrar para quedarse con todas las filas de los grupos que tienen un evento de remate
    shot_events = ['Goal', 'Attempt Saved', 'Miss', 'Post']
    df_shots_filtered = df.groupby(['TeamName', 'Posesion']).filter(lambda g: g['NaEventType'].isin(shot_events).any()).copy()

    # 2. Filtrar por posesiones con al menos un evento de juego regular
    posesiones_regulares = df_shots_filtered[df_shots_filtered['Regular_play'] == 1]['Posesion'].unique()
    df_filtered = df_shots_filtered[df_shots_filtered['Posesion'].isin(posesiones_regulares)].copy()

    df_filtered = df_filtered.sort_values(by=['time_seconds', 'IdFrame'])
    is_pass = (df_filtered['NaEventType'] == 'Pass') & (df_filtered['long_ball'] != -1) & (df_filtered['chipped'] != -1)

    # 3. Calcular métricas para juego regular
    possession_metrics = df_filtered.groupby(['Posesion']).agg(
        total_time=('time_seconds', lambda x: x.max() - x.min()),
        total_actions=('x', 'count'),
        actions_x_le_20=('x', lambda x: (x <= 20).sum()),
        passes_x_20_40=('x', lambda s: (is_pass[s.index] & (s > 20) & (s <= 40)).sum()),
        passes_x_gt_40=('x', lambda s: (is_pass[s.index] & (s > 40)).sum()),
        total_passes=('NaEventType', lambda s: (s == 'Pass').sum()),
        min_x=('x', 'min'),
        includes_counterpress=('counterpress_5s_flag', lambda s: 1 if (s == 1).any() else 0),
        includes_long_ball_from_defense=('x', lambda s: 1 if ((df_filtered.loc[s.index, 'long_ball'] == 1) & (df_filtered.loc[s.index, 'chipped'].isna()) & (s <= 30)).any() else 0),
        high_recovery_start=('x', lambda s: 1 if ((df_filtered.loc[s.index, 'NaEventType'].isin(['Ball recovery', 'Ball touch', 'Tackle', 'Interception', 'Blocked Pass'])) & (df_filtered.loc[s.index, 'Outcome'] == 1) & (s >= 60)).any() else 0)
    ).reset_index()

    # 4. Función para categorizar la posesión de juego regular
    def categorize_possession(row):
        if row['total_time'] == 0 and row['total_actions'] == 1: return 'Una acción tras ruido'
        le_20, x_20_40, gt_40 = row['actions_x_le_20'], row['passes_x_20_40'], row['passes_x_gt_40']
        
        category = 'Otro'
        if le_20 >= 1 and le_20 >= x_20_40 and le_20 > gt_40: category = 'Superar Presiones'
        elif x_20_40 >= 1 and x_20_40 > le_20 and x_20_40 >= gt_40: category = 'Ataque a bloque medio'
        elif gt_40 >= 1 and gt_40 > le_20 and gt_40 > x_20_40: category = 'Atacando bloque bajo'

        if row['includes_counterpress'] == 1 or row['high_recovery_start'] == 1: category = 'Recuperación Alta'
        if category == 'Otro': return 'Otra Posesión'
        return category

    possession_metrics['possession_type'] = possession_metrics.apply(categorize_possession, axis=1)

    # 5. Asignar las categorías de juego regular al DataFrame final
    df_final = pd.merge(df, possession_metrics[['Posesion', 'possession_type']], on='Posesion', how='left')

    # 6. Refinar las categorías para jugadas a balón parado
    #df_final = refine_set_pieces(df_final)

    # Rellenar cualquier valor restante con 'Otro'
    df_final['possession_type'] = df_final['possession_type'].fillna('Otro')

    return df_final



