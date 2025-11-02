import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from charts.KPIs_Base_Players import (df_principais_categorias, fig_faixa_etaria, fig_idade_x_sexo, fig_sexo, grafico_bairros, grafico_cidades, metricas_etarias,)

from api_client import get_json_df, get_all_json_df

# carregar bases no cache
@st.cache_data(show_spinner=False)
def load_players():
    return get_all_json_df("/players")

df_players = pd.read_csv(r"base_de_dados\base_players.csv", sep=",")
df_lojas = pd.read_csv(r"base_de_dados\base_lojas.csv", sep=",")


st.set_page_config(page_title="Dashboard CEO", layout="wide")
st.title("Dashboard – CEO")

aba1, aba2 = st.tabs(["Perfil dos Players", "Perfil das Lojas"])
with aba1:
    aba1, aba2, aba3, aba4 = st.tabs(["Perfil Etarico", "Perfil de Gênero","Perfil Comportamento", "Perfil Demográfico"])
    with aba1:

        st.markdown("### Métricas Etária")

        moda, media, mediana = metricas_etarias(df_players)

        col1, col2, col3 = st.columns(3)
        col1.metric("Média de idade", f"{media} anos")
        col2.metric("Mediana de idade", f"{mediana} anos")
        col3.metric("Moda de idade", f"{moda} anos")

        st.plotly_chart(fig_faixa_etaria(df_players), use_container_width=True)

    with aba2:
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(fig_sexo(df_players), use_container_width=True)

        with col2:
            st.plotly_chart(fig_idade_x_sexo(df_players), use_container_width=True)

    with aba3:
        st.plotly_chart(df_principais_categorias(df_players), use_container_width=True, hide_index=True)

    with aba4:
        tipo_options = ["Moradia", "Trabalho", "Escola"]
        tipo_to_col  = {
            "Moradia":  "cidade_residencial",
            "Trabalho": "cidade_trabalho",
            "Escola":   "cidade_escola",
        }


        tipo_cidade_bairro = st.selectbox("Selecione um tipo de cidade", tipo_options)

        col1, col2 = st.columns(2)
        with col1:
            col_cidade = tipo_to_col[tipo_cidade_bairro]
            lista_cidades = (
                df_players[col_cidade]
                        .dropna()
                .astype(str)
                .unique()
            )

            st.plotly_chart(grafico_cidades(df_players, tipo_cidade_bairro), use_container_width=True)
        with col2:
            cidade_selecionada = st.selectbox("Selecione a cidade", sorted(lista_cidades))
            st.plotly_chart(
                grafico_bairros(df_players, tipo_cidade_bairro, cidade_selecionada),
                use_container_width=True
            )


with aba2:
    st.markdown("## Perfil dos players")



