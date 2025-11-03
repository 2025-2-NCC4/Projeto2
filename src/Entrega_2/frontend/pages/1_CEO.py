import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from charts.KPIs_Base_Players import (df_principais_categorias, fig_faixa_etaria, fig_idade_x_sexo, fig_sexo, grafico_bairros, grafico_cidades, metricas_etarias,)
from charts.KPIs_Base_Lojas import (frequencia_ano, frequencia_diaria, frequencia_mensal, frequencia_semanal, medias_frequencia, usuarios_loja)

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
    aba1_1, aba1_2, aba1_3, aba1_4 = st.tabs(["Perfil Etárico", "Perfil de Gênero","Perfil Comportamento", "Perfil Demográfico"])
    with aba1_1:

        st.markdown("### Métricas Etária")

        moda, media, mediana = metricas_etarias(df_players)

        col1, col2, col3 = st.columns(3)
        col1.metric("Média de idade", f"{media} anos")
        col2.metric("Mediana de idade", f"{mediana} anos")
        col3.metric("Moda de idade", f"{moda} anos")

        st.plotly_chart(fig_faixa_etaria(df_players), use_container_width=True)

    with aba1_2:
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(fig_sexo(df_players), use_container_width=True)

        with col2:
            st.plotly_chart(fig_idade_x_sexo(df_players), use_container_width=True)

    with aba1_3:
        st.plotly_chart(df_principais_categorias(df_players), use_container_width=True, hide_index=True)

    with aba1_4:
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

    aba2_1, aba2_2 = st.tabs(["Frequência", "Lojas"])
    with aba2_1:
        
        df_lojas["data_captura"] = pd.to_datetime(df_lojas["data_captura"], errors="coerce")
        df_lojas = df_lojas.dropna(subset=["data_captura"])

        anos_disponiveis = sorted(df_lojas["data_captura"].dt.year.dropna().unique(), reverse=True)
        ano_escolhido = st.selectbox("Selecione o ano:", anos_disponiveis)

        meses_disponiveis = (
            df_lojas[df_lojas["data_captura"].dt.year == ano_escolhido]["data_captura"]
            .dt.month.unique()
        )
        meses_disponiveis = sorted(meses_disponiveis)

        meses_pt = {
            1:"Janeiro",2:"Fevereiro",3:"Março",4:"Abril",5:"Maio",6:"Junho",
            7:"Julho",8:"Agosto",9:"Setembro",10:"Outubro",11:"Novembro",12:"Dezembro"
        }

        opcoes_meses = [meses_pt[m] for m in meses_disponiveis]
        mes_escolhido = st.selectbox("Selecione o mês:", opcoes_meses)

        valores = medias_frequencia(df_lojas, mes_escolhido, ano_escolhido)

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Média Diária", round(valores["media_diaria_mes_ano"], 2))

        with col2:
            st.metric("Média Semanal", round(valores["media_semanal_ano"], 2))

        with col3:
            st.metric("Média Mensal", round(valores["media_mensal_ano"], 2))

        with col4:
            st.metric("Média Anual", round(valores["media_anual"], 2))

        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(frequencia_diaria(df_lojas, mes=mes_escolhido, ano=ano_escolhido), use_container_width=True)
        with col2:
            st.plotly_chart(frequencia_semanal(df_lojas, ano_escolhido), use_container_width=True)
        col3, col4 = st.columns(2)
        with col3:
            st.plotly_chart(frequencia_mensal(df_lojas, ano_escolhido), use_container_width=True)
        with col4:
            st.plotly_chart(frequencia_ano(df_lojas), use_container_width=True)

    with aba2_2:
        st.plotly_chart(usuarios_loja(df_lojas), use_container_width=True)

    
    



