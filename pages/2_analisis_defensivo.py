import streamlit as st
import pandas as pd
from utils.plots import plot_defensive_actions

st.title('Análisis Defensivo')

df = st.session_state['df']
selected_team = st.session_state['selected_team']

# For defensive analysis, we look at shots against the selected team
opponent_df = df[df['opponent_name'] == selected_team]

st.header(f'Análisis Defensivo para {selected_team}')

st.subheader('Acciones Defensivas que Terminan en Tiro del Rival')
fig_defensive_actions = plot_defensive_actions(opponent_df)
st.plotly_chart(fig_defensive_actions, use_container_width=True)
