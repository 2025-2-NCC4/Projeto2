# components/aba_players.py
import streamlit as st
from charts.KPIs_Base_Players.KPIs_Base_Players import (
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

    # --- Métricas etárias (cards a partir do DataFrame retornado) ---
    try:
        met = metricas_etarias(df_players)  # DataFrame com colunas: "Métrica" e "Valor"

        st.write("### Métricas Etárias")
        if met is not None and not met.empty:
            cols = st.columns(len(met))  # um card por linha do DF
            for col, (_, row) in zip(cols, met.iterrows()):
                nome = str(row.get("Métrica", "Métrica"))
                valor = row.get("Valor", "—")
                col.metric(nome, f"{valor}")
        else:
            st.info("Sem dados para calcular as métricas etárias no período selecionado.")
    except Exception as e:
        st.warning(f"Erro ao calcular ou exibir 'metricas_etarias': {e}")
        
    # --- Gráficos principais ---
    try:
        c1, c2, c3 = st.columns(3)
        with c1:
            try:
                st.plotly_chart(fig_sexo(df_players), use_container_width=True)
            except Exception as e:
                st.warning(f"Erro ao renderizar gráfico 'fig_sexo': {e}")

        with c2:
            try:
                st.plotly_chart(fig_faixa_etaria(df_players), use_container_width=True)
            except Exception as e:
                st.warning(f"Erro ao renderizar gráfico 'fig_faixa_etaria': {e}")

        with c3:
            try:
                st.plotly_chart(fig_idade_x_sexo(df_players), use_container_width=True)
            except Exception as e:
                st.warning(f"Erro ao renderizar gráfico 'fig_idade_x_sexo': {e}")

    except Exception as e:
        st.warning(f"Erro na renderização dos gráficos principais: {e}")

    # --- Gráficos de localização ---
    try:
        st.plotly_chart(grafico_cidades(df_players), use_container_width=True)
    except Exception as e:
        st.warning(f"Erro ao renderizar gráfico 'grafico_cidades': {e}")

    try:
        st.plotly_chart(grafico_bairros(df_players), use_container_width=True)
    except Exception as e:
        st.warning(f"Erro ao renderizar gráfico 'grafico_bairros': {e}")

