# components/aba_players.py
import streamlit as st
from charts.KPIs_Base_Players.KPIs_Base_Players import (
    df_principais_categorias,
    fig_faixa_etaria,
    fig_idade_x_sexo,
    fig_sexo,
    grafico_bairros,
    grafico_cidades,
    metricas_etarias,
)

def render_aba_players(df_players):
    """Renderiza a aba 'Perfil dos Players'."""
    st.subheader("Perfil dos Players")
    try:
        c1, c2, c3 = st.columns(3)
        with c1:
            st.plotly_chart(fig_sexo(df_players), use_container_width=True)
        with c2:
            st.plotly_chart(fig_faixa_etaria(df_players), use_container_width=True)
        with c3:
            st.plotly_chart(fig_idade_x_sexo(df_players), use_container_width=True)

        st.plotly_chart(grafico_cidades(df_players), use_container_width=True)
        st.plotly_chart(grafico_bairros(df_players), use_container_width=True)

        st.dataframe(metricas_etarias(df_players), use_container_width=True)
    except Exception as e:
        st.warning(f"Alguma função de Players não pôde ser renderizada: {e}")
