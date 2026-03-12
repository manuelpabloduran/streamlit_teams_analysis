import streamlit as st
import pandas as pd
from utils.plots import plot_xg_scatter, plot_xgot_scatter
from preprocessing import normalize_columns

st.set_page_config(layout="wide")

st.title('Análisis de Posesiones y Tiros')

# Cargar datos (con caché para mejorar rendimiento)
@st.cache_data
def load_data(url):
    df = pd.read_parquet(url)
    df = normalize_columns(df)
    return df

df = load_data('preprocessed_SSD_25-26.parquet')

st.header('Análisis de Expected Goals (xG) y Expected Goals on Target (xGOT)')

# --- Análisis de xG (Expected Goals) ---
st.subheader('xG a Favor vs. xG en Contra')
fig_xg = plot_xg_scatter(df)
st.plotly_chart(fig_xg, use_container_width=True)


# --- Análisis de xGOT (Expected Goals on Target) ---
st.subheader('xGOT a Favor vs. xGOT en Contra')
fig_xgot = plot_xgot_scatter(df)
st.plotly_chart(fig_xgot, use_container_width=True)
