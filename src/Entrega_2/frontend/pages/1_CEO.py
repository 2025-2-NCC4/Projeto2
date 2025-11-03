import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from charts.KPIs_Base_Players.KPIs_Base_Players import (df_principais_categorias, fig_faixa_etaria, fig_idade_x_sexo, fig_sexo, grafico_bairros, grafico_cidades, metricas_etarias,)
from charts.KPIs_Base_Lojas.Frequencia_por_Loja_Capturas import (frequencia_ano_filtrada, frequencia_dia_semana_ano_filtrada, frequencia_dia_semana_mes_filtrada, frequencia_diaria_filtrada, frequencia_mensal_filtrada, frequencia_semanal_filtrada, medias_frequencia_filtrada)
from charts.KPIs_Base_Lojas.Comparativos_Lojas import (capturas_categoria, resumo_parceiros, tipo_cupom, usuarios_loja)

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
    # --- Base e seletores globais (ano/mês/modo) ---
    df_base = df_lojas.copy()
    df_base["data_captura"] = pd.to_datetime(df_base["data_captura"], errors="coerce")
    df_base = df_base.dropna(subset=["data_captura"])

    anos_disponiveis = sorted(df_base["data_captura"].dt.year.unique(), reverse=True)
    ano_escolhido = st.selectbox("Selecione o ano:", anos_disponiveis)

    meses_pt = {
        1:"Janeiro",2:"Fevereiro",3:"Março",4:"Abril",5:"Maio",6:"Junho",
        7:"Julho",8:"Agosto",9:"Setembro",10:"Outubro",11:"Novembro",12:"Dezembro"
    }
    meses_disp = sorted(df_base.loc[df_base["data_captura"].dt.year == ano_escolhido, "data_captura"].dt.month.unique())
    opcoes_meses = [meses_pt[m] for m in meses_disp]
    mes_escolhido = st.selectbox("Selecione o mês:", opcoes_meses)
    modo = st.selectbox("Exibir como:", ["Valores", "Percentual", "Ambos"], index=0).lower()

    # --- Sub-abas: KPIs de captura e Lojas/Categorias ---
    aba2_1, aba2_2 = st.tabs(["Frequência de Captura de cupons", "Perfil geral de lojas"])

    # ===========================
    # 1) FREQUÊNCIA DE CAPTURA
    # ===========================
    with aba2_1:
        

        # Coluna 2: critério (Geral/Categoria/Nome) + select correspondente
        criterio = st.radio("Analisar por:", ["Geral", "Categoria", "Nome"], horizontal=True)
        # Opções (inclui "Todas")
        opcoes_tipo = ["Todas"] + sorted(df_base["tipo_loja"].dropna().astype(str).unique())
        opcoes_nome = ["Todas"] + sorted(df_base["nome_loja"].dropna().astype(str).unique())
        filtro_tipo, filtro_nome = None, None
        if criterio == "Categoria":
            sel = st.selectbox("Categoria:", opcoes_tipo, index=0)
            filtro_tipo = None if sel == "Todas" else sel
        elif criterio == "Nome":
            sel = st.selectbox("Nome:", opcoes_nome, index=0)
            filtro_nome = None if sel == "Todas" else sel
        # Se "Geral": ambos permanecem None

        # Sub-abas internas
        aba2_1_1, aba2_1_2 = st.tabs(["Geral", "Comparativa"])

        with aba2_1_1:
            # KPIs médios (usa mês/ano + filtros)
            valores = medias_frequencia_filtrada(
                df_base, mes_escolhido, ano_escolhido,
                nome_loja=filtro_nome, tipo_loja=filtro_tipo
            )
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Média Diária", round(valores["media_diaria_mes_ano"], 2))
            k2.metric("Média Semanal", round(valores["media_semanal_ano"], 2))
            k3.metric("Média Mensal", round(valores["media_mensal_ano"], 2))
            k4.metric("Média Anual", round(valores["media_anual"], 2))

            # Gráficos (todos aceitam nome_loja/tipo_loja + modo)
            st.plotly_chart(
                frequencia_diaria_filtrada(df_base, mes_escolhido, ano_escolhido,
                                  nome_loja=filtro_nome, tipo_loja=filtro_tipo, modo=modo),
                use_container_width=True
            )
            st.plotly_chart(
                frequencia_semanal_filtrada(df_base, ano_escolhido,
                                   nome_loja=filtro_nome, tipo_loja=filtro_tipo, modo=modo),
                use_container_width=True
            )
            st.plotly_chart(
                frequencia_mensal_filtrada(df_base, ano_escolhido,
                                  nome_loja=filtro_nome, tipo_loja=filtro_tipo, modo=modo),
                use_container_width=True
            )
            st.plotly_chart(
                frequencia_dia_semana_mes_filtrada(df_base, ano_escolhido, mes=mes_escolhido,
                                                   nome_loja=filtro_nome, tipo_loja=filtro_tipo, modo=modo),
                use_container_width=True
            )
            st.plotly_chart(
                frequencia_ano_filtrada(df_base, nome_loja=filtro_nome, tipo_loja=filtro_tipo, modo=modo),
                use_container_width=True
            )
            st.plotly_chart(
                frequencia_dia_semana_ano_filtrada(df_base, ano_escolhido,
                                                   nome_loja=filtro_nome, tipo_loja=filtro_tipo, modo=modo),
                use_container_width=True
            )

    # ===========================
    # 2) LOJAS / CATEGORIAS
    # ===========================
    with aba2_2:
        # Cards (resumo do mês/ano)
        resumo = resumo_parceiros(df_base, mes_escolhido, ano_escolhido)
        c1, c2 = st.columns(2)
        c1.metric("Lojas Parceiras", resumo["total_lojas"])
        c2.metric("Categorias de Lojas", resumo["total_categorias"])

        # Gráficos de ranking (mês/ano + modo)
        c3, c4 = st.columns(2)
        with c3:
            st.plotly_chart(
                usuarios_loja(df_base, mes_escolhido, ano_escolhido, modo=modo),
                use_container_width=True
            )
        with c4:
            st.plotly_chart(
                capturas_categoria(df_base, mes_escolhido, ano_escolhido, modo=modo),
                use_container_width=True
            )
        c5, c6 = st.columns(2)
        with c5:
            st.plotly_chart(
                tipo_cupom(
                    df_lojas,
                    ano_escolhido,
                    mes=mes_escolhido,            
                    nome_loja=filtro_nome,        
                    tipo_loja=filtro_tipo,
                    modo=modo         
                    ),
                use_container_width=True
            )
