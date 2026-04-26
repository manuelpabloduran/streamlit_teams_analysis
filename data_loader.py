import os
import streamlit as st
import pandas as pd
from preprocessing import preprocess_data, add_pressures, normalize_columns

_PARQUET = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'preprocessed_SSD_25-26.parquet')


@st.cache_data
def load_preprocessed_data():
    """Carga y preprocesa el parquet principal. Usado por páginas 1, 2 y 4."""
    df = pd.read_parquet(_PARQUET)
    return preprocess_data(df)


@st.cache_data
def load_pressure_data():
    """Carga y procesa presiones. Usado por página 3."""
    df = pd.read_parquet(_PARQUET)
    df = add_pressures(df)
    if 'fecha' not in df.columns and 'DtGame' in df.columns:
        df['fecha'] = pd.to_datetime(df['DtGame']).dt.date
    return df


@st.cache_data
def load_normalized_data():
    """Carga y normaliza columnas sin preprocesamiento pesado. Usado por app.py."""
    df = pd.read_parquet(_PARQUET)
    return normalize_columns(df)
