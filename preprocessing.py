import pandas as pd
import numpy as np
import json
import ast


# Mapeo de columnas del nuevo CSV (preprocessed_SSD_25-26) al formato interno
_COLUMN_RENAME_MAP = {
    'event_name':         'NaEventType',
    'jugador':            'NaPlayer',
    'fecha':              'DtGame',
    'endX':               'end_x',
    'endY':               'end_y',
    'xG':                 'xg',
    'xGoT':               'xgot',
    'TeamRival':          'RivalName',
    'outcome_value':      'Outcome',
    'id':                 'IdFrame',
    'goalMouthY':         'Goal_mouth_y_co-ordinate',
    'goalMouthZ':         'Goal_mouth_z_co-ordinate',
    'receiver_playerName':'receiving_player',
}

# Columnas derivadas de qualifiers que no están en el nuevo CSV;
# se agregan como NaN para que el código no rompa.
_STUB_COLUMNS = [
    'NaHomeTeam', 'NaAwayTeam', 'IdHomeTeam', 'IdAwayTeam', 'IdTeam',
    'Regular_play', 'counterpress_5s_flag', 'long_ball', 'chipped',
    'corner_taken', 'in_swinger', 'out_swing', 'cross',
    'Set_piece', 'blocked', 'through_ball', 'lay_off',
    'Free_kick', 'head_info', '1_on_1', 'First_Touch', 'Individual_Play',
    'Panenka', 'Deflection', 'throw_in',
]

# Diccionarios para derivar columnas de tiro desde qualifiers.
# Las claves son los displayName reales del formato Opta (CamelCase).
# Los valores mantienen el formato del CSV original para que todo el código
# downstream (filtros de página, plot_set_piece_shots, plot_goals_sunburst) siga funcionando.
_PLAY_TYPE_MAP = {
    "RegularPlay":     "Regular_play",
    "SetPiece":        "Set_piece",
    "Penalty":         "Penalty",
    "FastBreak":       "Fast_break",
    "FromCorner":      "From_corner",
    "ThrowinSetPiece": "Throw-in_set_piece",
}

# Orden importa: SmallBox y OutOfBox deben ir antes de Box
# para que el substring match no sea ambiguo.
_SHOT_LOCATION_MAP = {
    "SmallBox":  "Small_box",
    "SixYard":   "Small_box",
    "OutOfBox":  "Out_of_box",
    "Box":       "Box",
}

_SHOT_PART_MAP = {
    "RightFoot":     "Right_footed",
    "LeftFoot":      "Left_footed",
    "Head":          "Head",
    "OtherBodyPart": "Other Body Part",
}


def _map_from_qualifiers(qualifiers_text, mapping):
    """
    Dado el texto de la columna qualifiers y un diccionario de mapeo,
    retorna el primer valor cuya clave aparece como substring en el texto.
    Si no hay match, retorna None.
    """
    if pd.isna(qualifiers_text):
        return None
    text = str(qualifiers_text)
    for key, value in mapping.items():
        if key in text:
            return value
    return None


def normalize_columns(df):
    """
    Normaliza las columnas del nuevo CSV (preprocessed_SSD_25-26) al formato
    que espera el resto de la app. Renombra columnas y agrega stubs para las
    que no existen en el nuevo archivo.
    """
    df = df.copy()

    # 1. Renombrar columnas presentes
    rename = {k: v for k, v in _COLUMN_RENAME_MAP.items() if k in df.columns}
    df = df.rename(columns=rename)

    # 2. Convertir isOwnGoal (bool) al formato antiguo: True → -1, False/NaN → NaN
    if 'isOwnGoal' in df.columns:
        df['own_goal'] = df['isOwnGoal'].apply(lambda x: -1 if x is True or x == True else np.nan)
    elif 'own_goal' not in df.columns:
        df['own_goal'] = np.nan

    # 3. Agregar columnas faltantes como NaN
    for col in _STUB_COLUMNS:
        if col not in df.columns:
            df[col] = np.nan

    # 4. Derivar play_type, shot_location y shot_part desde qualifiers
    #    solo para filas donde xg no es nulo (eventos de tiro)
    shot_mask = df['xg'].notna()
    for col, mapping in [
        ('play_type',     _PLAY_TYPE_MAP),
        ('shot_location', _SHOT_LOCATION_MAP),
        ('shot_part',     _SHOT_PART_MAP),
    ]:
        df[col] = None
        if shot_mask.any() and 'qualifiers' in df.columns:
            df.loc[shot_mask, col] = df.loc[shot_mask, 'qualifiers'].apply(
                lambda q: _map_from_qualifiers(q, mapping)
            )

    df['cross'] = np.where(df['qualifiers'].str.contains('Cross'), -1, np.nan)

    # Clave única de posesión por partido (Posesion se repite entre partidos)
    df['Posesion_key'] = df['matchId'].astype(str) + '_' + df['Posesion'].astype(str)

    return df

def refine_set_pieces(df):
    """
    Refina el 'possession_type' para jugadas a balón parado basándose en reglas específicas.
    """
    # Obtener las posesiones que no fueron categorizadas por la lógica de juego regular.
    df = df.copy()
    uncategorized_mask = df['possession_type'].isna()
    uncategorized_possessions = df[uncategorized_mask]['Posesion_key'].unique()
    print(len(uncategorized_possessions))

    # Creamos un diccionario para mapear Posesion_key -> nuevo_tipo
    new_types_map = {}

    # Agrupamos el dataframe original por 'Posesion_key' una sola vez para eficiencia
    grouped_df = df.sort_values(by=['Posesion_key', 'time_seconds', 'IdFrame']).groupby('Posesion_key')

    for poss_id in uncategorized_possessions:
        possession_group = grouped_df.get_group(poss_id)
        play_type_series = possession_group.loc[
            possession_group['play_type'].notna(), 'play_type'
        ]
        if play_type_series.empty:
            # Si no hay ningún play_type definido, saltamos esta posesión
            # (o podrías poner new_type = "Otro" si prefieres algo por defecto)
            continue
        
        play_type = play_type_series.iloc[0]
        
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

    # Solo sobrescribimos donde antes estaba NaN
    df['possession_type'] = df['possession_type'].astype(object)
    df.loc[uncategorized_mask, 'possession_type'] = (
        df.loc[uncategorized_mask, 'Posesion_key'].map(new_types_map)
    )
    
    return df


def preprocess_data(df):
    """
    Aplica un pipeline de pre-procesamiento para calcular el tipo de posesión.
    """
    # --- Inicio del Pipeline ---

    # Normalizar columnas del nuevo CSV al formato interno
    df = normalize_columns(df)

    # Corrección de goles en propia puerta (solo si hay datos de equipos local/visitante)
    own_goal_condition = (df['NaEventType'] == 'Goal') & (df['own_goal'].notna())
    if df['NaHomeTeam'].notna().any():
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
    possession_duration = df.groupby('Posesion_key')['time_seconds'].transform(lambda x: x.max() - x.min())
    possession_counts = df.groupby('Posesion_key')['time_seconds'].transform('count')
    df['possession_duration'] = possession_duration.where(possession_counts > 1, np.nan)
    df['possession_duration'] = df['possession_duration'].clip(upper=100)
    print(df['possession_duration'])
    print(df['possession_duration'].describe())


    # Limitar possession_duration a posesiones con tiro (comportamiento original:
    # el CSV anterior solo contenía posesiones con tiro, por lo que la distribución
    # solo reflejaba esas posesiones).
    shot_events_set = {'Goal', 'MissedShots', 'SavedShot'}
    shot_possession_keys = set(
        df.loc[df['NaEventType'].isin(shot_events_set), 'Posesion_key'].unique()
    )
    df.loc[~df['Posesion_key'].isin(shot_possession_keys), 'possession_duration'] = np.nan

    df['possession_xg'] = df.groupby('Posesion_key')['xg'].transform('sum')
    df['possession_xg'] = df['possession_xg'].clip(upper=1)
    print(df['possession_xg'])
    print(df['possession_xg'].describe())

    df['iniciacion_area'] = np.where(((df["x"] >= 84) & (df["y"] <= 81) & (df["y"] >= 19)), 1, 0)
    df['finalizacion_area'] = np.where(((df["end_x"] >= 84) & (df["end_y"] <= 81) & (df["end_y"] >= 19)), 1, 0)
    df['pase_peligroso_al_area'] = np.where(((df["iniciacion_area"] == 0) & (df["end_x"] >= 84) & (df["end_y"] <= 81) & (df["end_y"] >= 19)), 1, 0)

    df['cutback'] = np.where(((df["NaEventType"]=="Pass") & (df["finalizacion_area"]==1) & (df["x"]>80) & (df["y"]<=37) & (df["Angle"]>1.57) & (df["Angle"]<3.14)) | ((df["NaEventType"]=="Pass") & (df["finalizacion_area"]==1) & (df["chipped"].isna()) & (df["Outcome"]==1) & (df["x"]>80) & (df["y"]>=63) & (df["Angle"]>3.14) & (df["Angle"]<4.71)), 1, 0)
    df['dividido'] = np.where(((df["NaEventType"]=="Pass") & (df["finalizacion_area"]==1) & (df["x"]>80) & (df["y"]<=37) & (df["Angle"]>0) & (df["Angle"]<1.57)) | ((df["NaEventType"]=="Pass") & (df["finalizacion_area"]==1) & (df["chipped"].isna()) & (df["Outcome"]==1) & (df["x"]>80) & (df["y"]>=63) & (df["Angle"]>4.71) & (df["Angle"]<6.28)), 1, 0)

    df['DtGame'] = pd.to_datetime(
        df['DtGame'].astype(str).str.replace('Z$', '', regex=True),
        errors='coerce'
    ).dt.date

    # 1. Filtrar para quedarse con todas las filas de los grupos que tienen un evento de remate
    shot_events = ['Goal', 'MissedShots', 'SavedShot']
    df_shots_filtered = df.groupby(['TeamName', 'Posesion_key']).filter(lambda g: g['NaEventType'].isin(shot_events).any()).copy()

    # 2. Filtrar por posesiones con al menos un evento de juego regular
    posesiones_regulares = df_shots_filtered[df_shots_filtered['Regular_play'] == 1]['Posesion_key'].unique()
    df_filtered = df_shots_filtered[df_shots_filtered['Posesion_key'].isin(posesiones_regulares)].copy()

    df_filtered = df_filtered.sort_values(by=['time_seconds', 'IdFrame'])
    is_pass = (df_filtered['NaEventType'] == 'Pass') & (df_filtered['long_ball'] != -1) & (df_filtered['chipped'] != -1)

    # 3. Calcular métricas para juego regular
    possession_metrics = df_filtered.groupby(['Posesion_key']).agg(
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
    df_final = pd.merge(df, possession_metrics[['Posesion_key', 'possession_type']], on='Posesion_key', how='left')

    # 6. Refinar las categorías para jugadas a balón parado
    df_final = refine_set_pieces(df_final)

    # Rellenar cualquier valor restante con 'Otro'
    df_final['possession_type'] = df_final['possession_type']

    return df_final

def add_pressures(df):
    """
    Extrae y normaliza las filas con información de presión del DataFrame original.
    Devuelve un DataFrame con las presiones ya parseadas y columnas útiles
    (`pressure_parsed`, `pressureReceived`, `positionX`, `positionY`, `equipo_vs_name`, `fecha`).
    """
    team_ids = pd.read_json('team_ids.json')

    def parse_pressure(x):
        if pd.isna(x):
            return {}
        if isinstance(x, dict):
            return x
        if isinstance(x, str):
            try:
                return json.loads(x)
            except json.JSONDecodeError:
                try:
                    return ast.literal_eval(x)
                except Exception:
                    return {}
        return {}

    df = df.copy()

    # Si no existe la columna `pressure`, devolvemos un dataframe vacío
    if 'pressure' not in df.columns:
        return pd.DataFrame()

    # Filtrar solo filas con presión
    presiones = df[df['pressure'].notna()].copy()

    # 1. Parsear todo a dict
    presiones["pressure_parsed"] = presiones["pressure"].apply(parse_pressure)

    # 2. Explotar a columnas
    qual_presiones = pd.json_normalize(presiones["pressure_parsed"]) if not presiones["pressure_parsed"].empty else pd.DataFrame()

    # 3. Unir al dataframe original
    presiones = presiones.drop(columns=["pressure"]).join(qual_presiones)

    presiones["pressureReceived"] = presiones["pressure_parsed"].apply(
        lambda x: x.get("pressureReceived", {}).get("value") if isinstance(x, dict) else np.nan
    )

    presiones["player"] = presiones["pressure_parsed"].apply(
        lambda x: x.get("player", []) if isinstance(x, dict) else []
    )

    # Explode players y normalizar sus columnas si existen
    presiones = presiones.explode("player").reset_index(drop=True)
    if 'player' in presiones.columns:
        player_cols = pd.json_normalize(presiones["player"]) if not presiones["player"].isna().all() else pd.DataFrame()
        presiones = presiones.drop(columns=["player"])
        if not player_cols.empty:
            presiones = pd.concat([presiones.reset_index(drop=True), player_cols.reset_index(drop=True)], axis=1)

    presiones["positionX"] = pd.to_numeric(presiones.get("positionX", pd.Series(dtype=float)), errors="coerce")
    presiones["positionY"] = pd.to_numeric(presiones.get("positionY", pd.Series(dtype=float)), errors="coerce")

    # Asegurar columna de fecha (parse robusto: soporta sufijo 'Z' y entradas inconsistentes)
    if 'DtGame' in presiones.columns:
        presiones['fecha'] = pd.to_datetime(presiones['DtGame'], errors='coerce').dt.date
    elif 'fecha' in presiones.columns:
        s = presiones['fecha'].astype(str).str.replace('Z$', '', regex=True)
        tmp = pd.to_datetime(s, errors='coerce')
        presiones['fecha'] = tmp.dt.date

    # Añadir nombres de equipo
    # Si el nuevo CSV ya trae TeamName y TeamRival, usamos esas directamente
    if 'TeamName' in presiones.columns and 'homeTeamName' not in presiones.columns:
        presiones['homeTeamName'] = presiones['TeamName']
    else:
        presiones = presiones.merge(team_ids, left_on="teamId", right_on="homeTeamId", how="left").drop(columns=["homeTeamId"])

    if 'TeamRival' in presiones.columns and 'equipo_vs_name' not in presiones.columns:
        presiones['equipo_vs_name'] = presiones['TeamRival']
    elif 'equipo vs' in presiones.columns:
        presiones = presiones.merge(team_ids, left_on='equipo vs', right_on='homeTeamId', suffixes=['', '_vs']).rename(columns={'homeTeamName_vs': 'equipo_vs_name'}).drop(columns=["homeTeamId"])
    else:
        presiones['equipo_vs_name'] = presiones.get('homeTeamName', None)

    # Calcular estado del partido si no viene ya calculado
    if 'estado_partido' not in presiones.columns:
        estado_col = 'estado partdo' if 'estado partdo' in presiones.columns else None
        if estado_col:
            presiones['estado_partido'] = np.where(
                presiones[estado_col] == 'Gana Visita',
                'Gana_' + presiones['equipo_vs_name'],
                np.where(
                    presiones[estado_col] == 'Gana Local',
                    'Gana_' + presiones['homeTeamName'],
                    'Empate'
                )
            )
        else:
            presiones['estado_partido'] = 'Empate'

    return presiones