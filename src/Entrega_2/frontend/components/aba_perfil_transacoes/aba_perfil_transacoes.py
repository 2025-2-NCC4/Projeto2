import streamlit as st
from calendar import monthrange
from charts.KPIs_Base_Transacoes.Taxa_Retencao import (
    taxa_retencao_mensal,
    taxa_retencao_anual,
    taxa_retencao_semanal,
    taxa_retencao_diaria,
    grafico_retencao_por_defasagem,
)

def render_aba_perfil_transacoes(
    df_filtrado,
    ano_escolhido: int,
    mes_escolhido: int,
    modo: str,
    filtro_nome=None,
    filtro_tipo=None,
    filtro_categ=None,
    export: bool = False,
):
    """
    Aba de Retenção. Se export=True, retorna {titulo: fig}.
    """
    figs = {}

    # --- Cálculo das taxas (métricas, não são figuras) ---
    try:
        r_anual = taxa_retencao_anual(
            df_filtrado,
            ano=ano_escolhido,
            nomes_lojas=filtro_nome or None,
            categorias=filtro_tipo or None,
            coluna_data="data",
        )
        r_mensal = taxa_retencao_mensal(
            df_filtrado,
            ano=ano_escolhido,
            mes=mes_escolhido,
            nomes_lojas=filtro_nome or None,
            categorias=filtro_tipo or None,
            coluna_data="data",
        )
        r_semanal = taxa_retencao_semanal(
            df_filtrado,
            ano_iso=ano_escolhido,
            semana=1,
            nomes_lojas=filtro_nome or None,
            categorias=filtro_tipo or None,
            coluna_data="data",
        )
        r_diaria = taxa_retencao_diaria(
            df_filtrado,
            data_base=None,
            nomes_lojas=filtro_nome or None,
            categorias=filtro_tipo or None,
            coluna_data="data",
        )
    except Exception as e:
        if not export:
            st.error(f"Erro ao calcular taxas de retenção: {e}")
        return None if not export else {}

    # --- UI das métricas (somente modo normal) ---
    if not export:
        st.subheader("Taxas de Retenção de Usuários")
        st.markdown("### Médias de Retenção por Período")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Anual", f"{r_anual['taxa']*100:.1f} %", help="Média entre anos consecutivos.")
        c2.metric("Mensal", f"{r_mensal['taxa']*100:.1f} %", help="Média entre meses consecutivos.")
        c3.metric("Semanal", f"{r_semanal['taxa']*100:.1f} %", help="Média entre semanas consecutivas.")
        c4.metric("Diária", f"{r_diaria['taxa']*100:.1f} %", help="Média entre dias consecutivos.")
        st.subheader("Retenção por Defasagem de Dias")

    # --- Slider / estado para 'max defasagem' ---
    dias_no_mes = monthrange(int(ano_escolhido), int(mes_escolhido))[1]
    default_k = min(14, max(dias_no_mes - 1, 1))
    if not export:
        max_k = st.slider(
            "Máx. defasagem (dias)",
            min_value=1,
            max_value=max(dias_no_mes - 1, 1),
            value=default_k,
            step=1,
            key="ret_max_k",
            help=f"Seleciona o intervalo máximo (1 a {dias_no_mes - 1}) para a análise de defasagem.",
        )
    else:
        max_k = st.session_state.get("ret_max_k", default_k)

    # --- Gráfico principal ---
    try:
        fig = grafico_retencao_por_defasagem(
            df_filtrado,
            ano=ano_escolhido,
            mes=mes_escolhido,
            max_defasagem_dias=max_k,
            nomes_lojas=filtro_nome or None,
            categorias=filtro_tipo or None,
            coluna_data="data",
            modo="percentual",
        )
        if fig is not None:
            if not export:
                st.plotly_chart(fig, use_container_width=True)
            figs[f"Retenção por Defasagem (até {max_k} dias)"] = fig
    except Exception as e:
        if not export:
            st.warning(f"Falha ao gerar gráfico: {e}")

    return None if not export else figs
