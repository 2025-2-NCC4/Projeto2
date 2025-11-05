import streamlit as st
from calendar import monthrange
from charts.KPIs_Base_Transacoes.Taxa_Retencao import (
    taxa_retencao_mensal,
    taxa_retencao_anual,
    taxa_retencao_semanal,
    taxa_retencao_diaria,
    retencao_por_defasagem_dias,
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
):
    st.subheader("Taxas de Retenção de Usuários")

    # --- Cálculo das taxas ---
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
        st.error(f"Erro ao calcular taxas de retenção: {e}")
        return

    # --- Exibição dos resultados ---
    st.markdown("### Médias de Retenção por Período")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Anual", f"{r_anual['taxa']*100:.1f} %", help="Média entre anos consecutivos.")
    c2.metric("Mensal", f"{r_mensal['taxa']*100:.1f} %", help="Média entre meses consecutivos.")
    c3.metric("Semanal", f"{r_semanal['taxa']*100:.1f} %", help="Média entre semanas consecutivas.")
    c4.metric("Diária", f"{r_diaria['taxa']*100:.1f} %", help="Média entre dias consecutivos.")

    st.subheader("Retenção por Defasagem de Dias")

    dias_no_mes = monthrange(int(ano_escolhido), int(mes_escolhido))[1]
    max_k = st.slider(
    "Máx. defasagem (dias)",
    min_value=1,
    max_value=max(dias_no_mes - 1, 1),
    value=min(14, max(dias_no_mes - 1, 1)),
    step=1,
    help=f"Seleciona o intervalo máximo (1 a {dias_no_mes - 1}) para a análise de defasagem."
)

    # Gráfico (linha)
    try:
        st.plotly_chart(
            grafico_retencao_por_defasagem(
                df_filtrado,
                ano=ano_escolhido,
                mes=mes_escolhido,
                max_defasagem_dias=max_k,   # ← aqui
                nomes_lojas=filtro_nome or None,
                categorias=filtro_tipo or None,
                coluna_data="data",
                modo="percentual"),
                use_container_width=True
            )
    except Exception as e:
        st.warning(f"Falha ao gerar gráfico: {e}")