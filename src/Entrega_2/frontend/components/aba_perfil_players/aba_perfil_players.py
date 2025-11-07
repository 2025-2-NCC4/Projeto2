import streamlit as st
from charts.KPIs_Base_Players.Perfil_Social_Players import (
    fig_faixa_etaria,
    fig_idade_x_sexo,
    fig_sexo,
    metricas_etarias
)

from charts.KPIs_Base_Players.Perfil_Espacial_Players import (
    grafico_bairros,
    grafico_cidades
)

def render_aba_players(df_players):
    """Renderiza a aba 'Perfil dos Players'."""
    st.subheader("Perfil dos Players")
    aba1, aba2 = st.tabs(["Perfil Social", "Perfil Geográfico"])
    with aba1:
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
            c1, c2 = st.columns(2)
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

            try:
                st.plotly_chart(fig_idade_x_sexo(df_players), use_container_width=True)
            except Exception as e:
                st.warning(f"Erro ao renderizar gráfico 'fig_idade_x_sexo': {e}")

        except Exception as e:
            st.warning(f"Erro na renderização dos gráficos principais: {e}")
    with aba2:
        # -------------------------------
        # Filtros de Localização (Players)
        # -------------------------------
        with st.expander("Filtros de localização (Players)", expanded=True):
            # 1) Contexto (define quais colunas usar)
            tipo_opt = st.selectbox(
                "Contexto",
                ["Moradia", "Trabalho", "Escola"],
                index=0,
                key="players_tipo_cidade"
            )
            sufixo = "residencial" if tipo_opt == "Moradia" else ("escola" if tipo_opt == "Escola" else "trabalho")
            col_city = f"cidade_{sufixo}"
            col_bairro = f"bairro_{sufixo}"

            # 2) Cidade (opcional)
            cidades_disp = sorted(df_players[col_city].dropna().astype(str).unique()) if col_city in df_players.columns else []
            cidade_sel = st.selectbox(
                "Cidade",
                ["(Todas)"] + cidades_disp,
                index=0,
                key="players_cidade"
            )

            # 3) Bairro (opcional, depende da cidade escolhida)
            if cidade_sel != "(Todas)" and col_bairro in df_players.columns:
                bairros_disp = sorted(
                    df_players.loc[df_players[col_city] == cidade_sel, col_bairro]
                            .dropna().astype(str).unique()
                )
            else:
                bairros_disp = sorted(
                    df_players[col_bairro].dropna().astype(str).unique()
                ) if col_bairro in df_players.columns else []

            bairro_sel = st.selectbox(
                "Bairro",
                ["(Todos)"] + bairros_disp,
                index=0,
                key="players_bairro"
            )

        # --- prepara DataFrames filtrados para os gráficos de localização ---
        df_players_loc_cidades = df_players  # grafico_cidades já agrega todas as cidades do contexto
        df_players_loc_bairros = df_players.copy()

        # filtra por cidade (para o gráfico de bairros)
        if cidade_sel != "(Todas)" and col_city in df_players_loc_bairros.columns:
            df_players_loc_bairros = df_players_loc_bairros[df_players_loc_bairros[col_city] == cidade_sel]

        # filtra por bairro se selecionado (continua exibindo o ranking se "(Todos)")
        if bairro_sel != "(Todos)" and col_bairro in df_players_loc_bairros.columns:
            df_players_loc_bairros = df_players_loc_bairros[df_players_loc_bairros[col_bairro] == bairro_sel]

            # --- Gráficos de localização ---
        try:
            st.plotly_chart(
                grafico_cidades(df_players_loc_cidades, tipo_cidade=tipo_opt),
                use_container_width=True
            )
        except Exception as e:
            st.warning(f"Erro ao renderizar gráfico 'grafico_cidades' ({tipo_opt}): {e}")

        try:
            st.plotly_chart(
                grafico_bairros(
                    df_players_loc_bairros,
                    tipo_cidade=tipo_opt,
                    cidade=None if cidade_sel == "(Todas)" else cidade_sel
                ),
                use_container_width=True
            )
        except Exception as e:
            alvo = f"{tipo_opt}" + ("" if cidade_sel == "(Todas)" else f" / {cidade_sel}")
            st.warning(f"Erro ao renderizar gráfico 'grafico_bairros' ({alvo}): {e}")



