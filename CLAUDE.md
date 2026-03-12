# Project: Streamlit Teams Analysis

Multipage Streamlit app for football (Spanish Segunda División 25-26) event data analysis.

## Key Files
- `preprocessed_SSD_25-26.parquet` — main data source (Opta event data, ~300k+ rows). Tracked via Git LFS. All pages load it with `pd.read_parquet(...)`.
- `preprocessing.py` — normalization layer (`normalize_columns`, `preprocess_data`, `add_pressures`)
- `utils/plots.py` — all plot functions
- `app.py` — home page (xG/xGOT scatter); uses `normalize_columns` only
- `pages/1_analisis_ofensivo.py` — offensive analysis; uses `preprocess_data`
- `pages/2_analisis_defensivo.py` — defensive analysis; uses `preprocess_data`
- `pages/3_presiones.py` — pressure maps (realized + received) and filters
- `pages/4_saques_de_arco.py` — goal kicks analysis + possession viewer; uses `preprocess_data`

## Data / Columns
- Event columns: `NaEventType`, `NaPlayer`, `TeamName`, `RivalName`, `Posesion`, `matchId`, `time_seconds`, `x`, `y`, `end_x`, `end_y`, `xg`, `xgot`, `Outcome`, `DtGame`
- `Posesion` IDs **repeat across matches** — use `Posesion_key` (created in `normalize_columns` as `matchId_Posesion`) for all groupby/isin operations
- `play_type`, `shot_location`, `shot_part` — derived from `qualifiers` column in `normalize_columns` using substring matching; values are Opta keys (`Regular_play`, `From_corner`, `Right_footed`, etc.), NOT Spanish
- `possession_duration` — NaN for non-shot possessions (intentional)
- `possession_xg` — sum of `xg` per possession; 0 for non-shot possessions
- `previous_event`, `next_event_posesion` — event context columns available in the raw parquet
- `estado_partido` — game state column, already present in parquet

## Normalization Pattern (preprocessing.py)
`normalize_columns(df)` handles all column renames and stub columns so no downstream code needs changing:
- `_COLUMN_RENAME_MAP`: parquet column → internal name (e.g. `endX`→`end_x`, `jugador`→`NaPlayer`, `fecha`→`DtGame`, `xG`→`xg`, `outcome_value`→`Outcome`, `TeamRival`→`RivalName`)
- `_STUB_COLUMNS`: NaN placeholders for missing columns
- `_PLAY_TYPE_MAP / _SHOT_LOCATION_MAP / _SHOT_PART_MAP`: Opta `displayName` → Opta key
- Also creates `Posesion_key = matchId + '_' + Posesion`

## Shot Event Names
`'SavedShot'`, `'MissedShots'`, `'Goal'` (NOT `'Attempt Saved'`, `'Miss'`, `'Post'`)

## Offensive vs Defensive Filter Pattern
- Offensive: filter by `TeamName`
- Defensive: filter by `RivalName` (pass `filter_col='RivalName'` to plot functions)

## Presiones (page 3)
- Data loaded via `add_pressures(df)` — returns exploded pressure rows with `positionX`, `positionY`, `intensity`, `equipo_vs_name`, `homeTeamName`
- Two KDE maps side by side: **Presiones recibidas** (`equipo_vs_name`) and **Presiones realizadas** (`TeamName`)
- Each map uses its own filtered df (`filtered_recibidas` / `filtered_realizadas`) — the team filter is applied separately per map to avoid conflicts
- Player filter uses `jugador` column; BallRecovery checkboxes filter on `previous_event` and `next_event_posesion`
- `plot_pressure_kde` accepts `title_label` param for custom title

## Saques de Arco (page 4)
- Loads full parquet via `preprocess_data`, then filters `qualifiers.str.contains('GoalKick')`
- Uses normalized column names: `end_x`, `Outcome`, `DtGame`, `RivalName`, `xg`
- `plot_goal_kicks` and `plot_goal_kicks_effectiveness` auto-detect normalized vs raw column names
- Possession viewer: selects possessions with GoalKick + xG > 0; draws full possession path with `plot_possession_path`
- `estado_partido` filter is applied to both `filtered` and `df_no_team` (for scatter stats)

## Known Pitfalls
- `Posesion` is NOT globally unique — `Posesion_key` must be used in ALL groupby/isin calls
- `df_page_filtered` must NOT be mutated after initial filters; use separate vars for section-specific filters
- `plot_pass_xg_matrix` internally recomputes `possession_xg` from `xg` column — doesn't use the preprocessed one
- Pages 1, 2, 4 use `preprocess_data` (heavy, cached). `app.py` uses only `normalize_columns`. Page 3 uses `add_pressures`.
- `plot_possession_path` expects `NaEventType` / `end_x` / `end_y` / `xg` (normalized names) but falls back to raw names
