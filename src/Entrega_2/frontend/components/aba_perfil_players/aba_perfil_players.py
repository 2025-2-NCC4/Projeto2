# components/aba_perfil_players/aba_perfil_players.py
import streamlit as st
from charts.KPIs_Base_Players.Perfil_Social_Players import (
    fig_faixa_etaria, fig_idade_x_sexo, fig_sexo, metricas_etarias
)
from charts.KPIs_Base_Players.Perfil_Espacial_Players import (
    grafico_bairros, grafico_cidades
)

def render_aba_players(df_players, export: bool = False):
    """
    Renderiza a aba 'Perfil dos Players'.
    Se export=True, retorna um dicionário {titulo: figure} usando os filtros atuais.
    """
    figs = {}  # coletor para exportação

    if not export:
        st.subheader("Perfil dos Players")

    # ------------------ PERFIL SOCIAL ------------------
    # (métricas + gráficos: sexo, faixa etária, idade x sexo)
    try:
        if not export:
            met = metricas_etarias(df_players)
            st.write("### Métricas Etárias")
            if met is not None and not met.empty:
                cols = st.columns(len(met))
                for col, (_, row) in zip(cols, met.iterrows()):
                    col.metric(str(row.get("Métrica","Métrica")), f"{row.get('Valor','—')}")
            else:
                st.info("Sem dados para calcular as métricas etárias no período selecionado.")
    except Exception as e:
        if not export:
            st.warning(f"Erro ao calcular 'metricas_etarias': {e}")

    try:
        f_sexo = fig_sexo(df_players)
        f_faixa = fig_faixa_etaria(df_players)
        f_idade_sexo = fig_idade_x_sexo(df_players)

        if export:
            figs["Distribuição por Sexo"] = f_sexo
            figs["Faixa Etária"] = f_faixa
            figs["Idade x Sexo"] = f_idade_sexo
        else:
            c1, c2 = st.columns(2)
            with c1: st.plotly_chart(f_sexo, use_container_width=True)
            with c2: st.plotly_chart(f_faixa, use_container_width=True)
            st.plotly_chart(f_idade_sexo, use_container_width=True)
    except Exception as e:
        if not export:
            st.warning(f"Erro nos gráficos sociais: {e}")

    # ------------------ PERFIL GEOGRÁFICO ------------------
    # Reutiliza os mesmos controles que você já tem
    if not export:
        with st.expander("Filtros de localização (Players)", expanded=True):
            tipo_opt = st.selectbox("Contexto", ["Moradia","Trabalho","Escola"], index=0, key="players_tipo_cidade")
            sufixo = "residencial" if tipo_opt == "Moradia" else ("escola" if tipo_opt == "Escola" else "trabalho")
            col_city = f"cidade_{sufixo}"
            col_bairro = f"bairro_{sufixo}"

            cidades_disp = sorted(df_players[col_city].dropna().astype(str).unique()) if col_city in df_players.columns else []
            cidade_sel = st.selectbox("Cidade", ["(Todas)"]+cidades_disp, index=0, key="players_cidade")

            if cidade_sel != "(Todas)" and col_bairro in df_players.columns:
                bairros_disp = sorted(df_players.loc[df_players[col_city]==cidade_sel, col_bairro].dropna().astype(str).unique())
            else:
                bairros_disp = sorted(df_players[col_bairro].dropna().astype(str).unique()) if col_bairro in df_players.columns else []
            bairro_sel = st.selectbox("Bairro", ["(Todos)"]+bairros_disp, index=0, key="players_bairro")
    else:
        # Para export, usamos o estado atual dos widgets (se houver) — caem em defaults se não existirem
        tipo_opt = st.session_state.get("players_tipo_cidade", "Moradia")
        sufixo = "residencial" if tipo_opt == "Moradia" else ("escola" if tipo_opt == "Escola" else "trabalho")
        col_city = f"cidade_{sufixo}"
        col_bairro = f"bairro_{sufixo}"
        cidade_sel = st.session_state.get("players_cidade", "(Todas)")
        bairro_sel = st.session_state.get("players_bairro", "(Todos)")

    # monta DFs filtrados p/ geográfico
    df_cidades = df_players
    df_bairros = df_players.copy()
    if cidade_sel != "(Todas)" and col_city in df_bairros.columns:
        df_bairros = df_bairros[df_bairros[col_city] == cidade_sel]
    if bairro_sel != "(Todos)" and col_bairro in df_bairros.columns:
        df_bairros = df_bairros[df_bairros[col_bairro] == bairro_sel]

    try:
        f_cidades = grafico_cidades(df_cidades, tipo_cidade=tipo_opt)
        f_bairros = grafico_bairros(df_bairros, tipo_cidade=tipo_opt, cidade=None if cidade_sel=="(Todas)" else cidade_sel)
        if export:
            figs[f"Cidades – {tipo_opt}"] = f_cidades
            alvo = f"{tipo_opt}" + ("" if cidade_sel == "(Todas)" else f" / {cidade_sel}")
            figs[f"Bairros – {alvo}"] = f_bairros
        else:
            st.plotly_chart(f_cidades, use_container_width=True)
            st.plotly_chart(f_bairros, use_container_width=True)
    except Exception as e:
        if not export:
            st.warning(f"Erro nos gráficos geográficos: {e}")

    return figs if export else None
