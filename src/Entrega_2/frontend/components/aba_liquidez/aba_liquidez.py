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

def render_aba_liquidez(df_filtrado: pd.DataFrame, lojas=None, categorias=None, export: bool = False):
    """
    Aba Liquidez. Se export=True, retorna {titulo: fig}.
    """
    dff = _aplica_filtros(df_filtrado, lojas, categorias)
    dff = prepare_liquidez_cols(dff)
    figs = {}

    # ===== Modo normal: widgets na sidebar =====
    if not export:
        with st.sidebar:
            st.markdown("### Exibição (Liquidez)")
            modo_exib = st.radio(
                "Tipo de exibição dos gráficos:",
                ["Valores (R$)", "Porcentagem (%)", "Ambos"],
                index=0, key="liq_modo"
            )
            top_n = st.slider(
                "Qtde de lojas no ranking",
                min_value=5, max_value=30, value=15, step=1,
                key="liq_top_n",
                help="Ajuste quantas lojas aparecem no ranking"
            )
    else:
        # Em export, respeita o estado atual (ou usa padrão)
        modo_exib = st.session_state.get("liq_modo", "Valores (R$)")
        top_n = st.session_state.get("liq_top_n", 15)

    def _mode_str():
        return {"Valores (R$)": "valores", "Porcentagem (%)": "percent", "Ambos": "ambos"}[modo_exib]

    # ===== KPIs (não são figuras) =====
    k = kpis_liquidez(dff)
    if not export:
        titulo = "KPIs de Liquidez"
        if k.get("fallback"):
            titulo += " (estimado)"
        st.subheader(titulo)
        c1, c2 = st.columns(2)
        c1.metric("Receita Líquida (R$)", fmt_br_money(k["receita_liquida"]) if pd.notna(k["receita_liquida"]) else "—")
        c2.metric("Margem Líquida (%)", f"{k['margem_liquida']*100:.2f}%" if pd.notna(k["margem_liquida"]) else "—")

    # ===== Série diária =====
    fig = fig_receita_liquida_diaria(dff)
    if fig:
        if not export:
            st.markdown("### Evolução Diária")
            st.plotly_chart(fig, use_container_width=True)
        figs["Receita Líquida por Dia (R$)"] = fig

    # ===== Top lojas =====
    mode = _mode_str()
    if mode == "ambos":
        fig1 = fig_top_lojas_receita_liquida(dff, top=top_n, mode="valores")
        fig2 = fig_top_lojas_receita_liquida(dff, top=top_n, mode="percent")
        if fig1:
            if not export:
                st.markdown("### Maiores Lojas por Receita Líquida — Valores (R$)")
                st.plotly_chart(fig1, use_container_width=True)
            figs[f"Top {top_n} Lojas por Receita Líquida (R$)"] = fig1
        if fig2:
            if not export:
                st.markdown("### Maiores Lojas por Receita Líquida — Porcentagem (%)")
                st.plotly_chart(fig2, use_container_width=True)
            figs[f"Top {top_n} Lojas por Receita Líquida (%)"] = fig2
    else:
        fig3 = fig_top_lojas_receita_liquida(dff, top=top_n, mode=mode)
        if fig3:
            if not export:
                st.markdown("### Maiores Lojas por Receita Líquida")
                st.plotly_chart(fig3, use_container_width=True)
            rot = "R$" if mode == "valores" else "%"
            figs[f"Top {top_n} Lojas por Receita Líquida ({rot})"] = fig3

    # ===== Custo por Tipo de Cupom =====
    fig = fig_custo_por_tipo_cupom(dff, mode=("valores" if mode != "percent" else "percent"))
    if fig:
        if not export:
            st.markdown("### Alocação de Custo por Tipo de Cupom")
            st.plotly_chart(fig, use_container_width=True)
        rot = "R$" if mode != "percent" else "%"
        figs[f"Custo por Tipo de Cupom ({rot})"] = fig

    # ===== Receita Líquida por Canal =====
    fig = fig_receita_liquida_por_canal(dff, mode=("valores" if mode != "percent" else "percent"))
    if fig:
        if not export:
            st.markdown("### Receita Líquida por Canal de Captação")
            st.plotly_chart(fig, use_container_width=True)
        rot = "R$" if mode != "percent" else "%"
        figs[f"Receita Líquida por Canal ({rot})"] = fig

    # ===== Margem por Tipo de Cupom (sempre %) =====
    fig = fig_margem_liquida_por_tipo(dff, min_receita=1000)
    if fig:
        if not export:
            st.markdown("### Margem Líquida por Tipo de Cupom (%)")
            st.plotly_chart(fig, use_container_width=True)
        figs["Margem Líquida por Tipo de Cupom (%)"] = fig

    return None if not export else figs
