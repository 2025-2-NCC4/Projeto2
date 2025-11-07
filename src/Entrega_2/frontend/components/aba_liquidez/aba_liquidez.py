import streamlit as st
import pandas as pd

from charts.KPIs_Liquidez.KPIs_Liquidez import (
    prepare_liquidez_cols,
    kpis_liquidez,
    fmt_br_money,
    fig_receita_liquida_diaria,
    fig_top_lojas_receita_liquida,
    fig_margem_liquida_por_tipo,
    fig_custo_por_tipo_cupom,
    fig_receita_liquida_por_canal,
)

def _aplica_filtros(df, lojas=None, categorias=None):
    d = df.copy()
    if lojas and "nome_estabelecimento" in d.columns:
        d = d[d["nome_estabelecimento"].isin(lojas)]
    if categorias and "categoria_estabelecimento" in d.columns:
        d = d[d["categoria_estabelecimento"].isin(categorias)]
    return d

def render_aba_liquidez(df_filtrado: pd.DataFrame, lojas=None, categorias=None):
    dff = _aplica_filtros(df_filtrado, lojas, categorias)
    dff = prepare_liquidez_cols(dff)

    # ===== Sidebar: modo de exibição =====
    with st.sidebar:
        st.markdown("### Exibição (Liquidez)")
        modo_exib = st.radio(
            "Tipo de exibição dos gráficos:",
            ["Valores (R$)", "Porcentagem (%)", "Ambos"],
            index=0, key="liq_modo"
        )

    def _mode_str():
        return {"Valores (R$)": "valores", "Porcentagem (%)": "percent", "Ambos": "ambos"}[modo_exib]

    # ===== KPIs =====
    k = kpis_liquidez(dff)
    titulo = "KPIs de Liquidez"
    if k.get("fallback"):
        titulo += " (estimado)"
    st.subheader(titulo)

    c1, c2 = st.columns(2)
    c1.metric("Receita Líquida (R$)", fmt_br_money(k["receita_liquida"]) if pd.notna(k["receita_liquida"]) else "—")
    c2.metric("Margem Líquida (%)", f"{k['margem_liquida']*100:.2f}%" if pd.notna(k["margem_liquida"]) else "—")

    # ===== Série diária =====
    st.markdown("### Evolução Diária")
    fig = fig_receita_liquida_diaria(dff)
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Sem dados suficientes para a série diária de Receita Líquida.")

    # ===== Ranking de Lojas (header + slider acima do gráfico) =====
    hdr_left, hdr_right = st.columns([3, 2])
    with hdr_left:
        st.markdown("### Maiores Lojas por Receita Líquida")
    with hdr_right:
        top_n = st.slider(
            "Qtde de lojas no ranking",
            min_value=5, max_value=30, value=15, step=1,
            key="liq_top_n",
            help="Ajuste quantas lojas aparecem no ranking"
        )

    if _mode_str() == "ambos":
        t1, t2 = st.tabs(["Valores (R$)", "Porcentagem (%)"])
        with t1:
            fig = fig_top_lojas_receita_liquida(dff, top=top_n, mode="valores")
            if fig: st.plotly_chart(fig, use_container_width=True)
        with t2:
            fig = fig_top_lojas_receita_liquida(dff, top=top_n, mode="percent")
            if fig: st.plotly_chart(fig, use_container_width=True)
    else:
        fig = fig_top_lojas_receita_liquida(dff, top=top_n, mode=_mode_str())
        if fig: st.plotly_chart(fig, use_container_width=True)

    # ===== Custo por Tipo de Cupom =====
    st.markdown("### Alocação de Custo por Tipo de Cupom")
    if _mode_str() == "ambos":
        t1, t2 = st.tabs(["Valores (R$)", "Porcentagem (%)"])
        with t1:
            fig = fig_custo_por_tipo_cupom(dff, mode="valores")
            if fig: st.plotly_chart(fig, use_container_width=True)
        with t2:
            fig = fig_custo_por_tipo_cupom(dff, mode="percent")
            if fig: st.plotly_chart(fig, use_container_width=True)
    else:
        fig = fig_custo_por_tipo_cupom(dff, mode=_mode_str())
        if fig: st.plotly_chart(fig, use_container_width=True)

    # ===== Receita Líquida por Canal =====
    st.markdown("### Receita Líquida por Canal de Captação")
    if _mode_str() == "ambos":
        t1, t2 = st.tabs(["Valores (R$)", "Porcentagem (%)"])
        with t1:
            fig = fig_receita_liquida_por_canal(dff, mode="valores")
            if fig: st.plotly_chart(fig, use_container_width=True)
        with t2:
            fig = fig_receita_liquida_por_canal(dff, mode="percent")
            if fig: st.plotly_chart(fig, use_container_width=True)
    else:
        fig = fig_receita_liquida_por_canal(dff, mode=_mode_str())
        if fig: st.plotly_chart(fig, use_container_width=True)

    # ===== Margem por Tipo de Cupom (sempre %) =====
    st.markdown("### Margem Líquida por Tipo de Cupom (%)")
    fig = fig_margem_liquida_por_tipo(dff, min_receita=1000)
    if fig: st.plotly_chart(fig, use_container_width=True)
