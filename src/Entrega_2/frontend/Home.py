import streamlit as st
import pandas as pd
from api_client import get_json_df

st.set_page_config(page_title="PicMoney – Dashboards", layout="wide")
st.title("PicMoney – Dashboards")
st.write("Use o menu à esquerda para acessar: CEO ou CFO.")

df_players = get_json_df("/players", {"sexo": "Feminino"})
df_lojas = get_json_df("/lojas")
df_simulacao = get_json_df("/simulacao")
df_transacoes = get_json_df("/transacoes")

st.dataframe(df_players, use_container_width=True)
st.dataframe(df_lojas, use_container_width=True)
st.dataframe(df_simulacao, use_container_width=True)
st.dataframe(df_transacoes, use_container_width=True)
