import streamlit as st
import pandas as pd
from utils.plots import (
    plot_shot_map,
    plot_shot_quality,
    plot_possession_duration,
)

st.title('Análisis Ofensivo')

df = st.session_state['df']
selected_team = st.session_state['selected_team']

team_df = df[df['team_name'] == selected_team]

st.header(f'Análisis para {selected_team}')

st.subheader('Mapa de Tiros')
fig_shot_map = plot_shot_map(team_df)
st.plotly_chart(fig_shot_map, use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    st.subheader('Calidad de Tiro (xG)')
    fig_shot_quality = plot_shot_quality(team_df)
    st.plotly_chart(fig_shot_quality, use_container_width=True)

with col2:
    st.subheader('Duración de Posesiones con Tiro')
    fig_possession_duration = plot_possession_duration(team_df)
    st.plotly_chart(fig_possession_duration, use_container_width=True)
