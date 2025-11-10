import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from charts.Repasse.Repasse import prepare_repasse_cols

def _aplica_filtros(df, lojas=None, categorias=None):
    dff = df.copy()
    if lojas and "nome_estabelecimento" in dff.columns:
        dff = dff[dff["nome_estabelecimento"].isin(lojas)]
    if categorias and "categoria_estabelecimento" in dff.columns:
        dff = dff[dff["categoria_estabelecimento"].isin(categorias)]
    return dff

def _fmt_br(x):
    try:
        return f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "—"

def _kpis_repasse_cfo(df_rep: pd.DataFrame):
    bruto = df_rep["valor_cupom"].sum() if "valor_cupom" in df_rep.columns else np.nan
    pic   = df_rep["repasse_picmoney"].sum() if "repasse_picmoney" in df_rep.columns else np.nan
    loja  = df_rep["repasse_lojista"].sum() if "repasse_lojista" in df_rep.columns else (
        bruto - pic if pd.notna(bruto) and pd.notna(pic) else np.nan
    )
    pct_pic  = (pic/bruto) * 100 if pd.notna(bruto) and bruto > 0 and pd.notna(pic) else np.nan
    pct_loja = (loja/bruto) * 100 if pd.notna(bruto) and bruto > 0 and pd.notna(loja) else np.nan

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Comissão PicMoney (R$)", _fmt_br(pic)  if pd.notna(pic)  else "—")
    c2.metric("Comissão PicMoney (%)", f"{pct_pic:.2f}%" if pd.notna(pct_pic) else "—")
    c3.metric("Repasse ao Lojista (R$)", _fmt_br(loja) if pd.notna(loja) else "—")
    c4.metric("Participação do Lojista (%)", f"{pct_loja:.2f}%" if pd.notna(pct_loja) else "—")

def _col_lojas_por_valor(df_rep, top=15):
    if {"nome_estabelecimento","valor_cupom"} - set(df_rep.columns): return None
    d = (df_rep.groupby("nome_estabelecimento")["valor_cupom"].sum()
            .reset_index().sort_values("valor_cupom", ascending=False).head(top))
    d["Label"] = d["valor_cupom"].map(_fmt_br)
    fig = px.bar(
        d, x="nome_estabelecimento", y="valor_cupom", text="Label",
        title="Maiores Lojas por Valor de Cupons (R$)",
        labels={"nome_estabelecimento":"Estabelecimento","valor_cupom":"R$"}
    )
    fig.update_traces(textposition="outside")
    return fig

def _col_lojas_por_repasse_valor(df_rep, top=15):
    if {"nome_estabelecimento","repasse_lojista"} - set(df_rep.columns): return None
    d = (df_rep.groupby("nome_estabelecimento")["repasse_lojista"].sum()
            .reset_index().sort_values("repasse_lojista", ascending=False).head(top))
    d["Label"] = d["repasse_lojista"].map(_fmt_br)
    fig = px.bar(
        d, x="nome_estabelecimento", y="repasse_lojista", text="Label",
        title="Maiores Lojas por Repasse ao Lojista (R$)",
        labels={"nome_estabelecimento":"Estabelecimento","repasse_lojista":"R$"}
    )
    fig.update_traces(textposition="outside")
    return fig

def _col_lojas_por_repasse_pct(df_rep, top=15, min_valor=1000):
    req = {"nome_estabelecimento","valor_cupom","repasse_lojista"}
    if not req.issubset(df_rep.columns): return None
    g = (df_rep.groupby("nome_estabelecimento")
            .agg(valor=("valor_cupom","sum"), rep_loja=("repasse_lojista","sum"))
            .reset_index())
    g = g[g["valor"] >= min_valor].copy()
    g["pct_loja"] = np.where(g["valor"]>0, g["rep_loja"]/g["valor"], np.nan)
    g = g.dropna(subset=["pct_loja"]).sort_values("pct_loja", ascending=False).head(top)
    g["Label"] = (g["pct_loja"]*100).round(2).astype(str)+"%"
    fig = px.bar(
        g, x="nome_estabelecimento", y="pct_loja", text="Label",
        title="Participação do Lojista (%) – Maiores Lojas",
        labels={"nome_estabelecimento":"Estabelecimento","pct_loja":"%"}
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(yaxis_tickformat=".0%")
    return fig

def _pizza_tipo_cupom(df_rep):
    if {"tipo_cupom","valor_cupom"} - set(df_rep.columns): return None
    d = (df_rep.groupby("tipo_cupom")["valor_cupom"].sum()
            .reset_index().sort_values("valor_cupom", ascending=False))
    fig = px.pie(
        d, names="tipo_cupom", values="valor_cupom", hole=0.4,
        title="Composição por Tipo de Cupom (R$)"
    )
    return fig

def render_aba_repasse(df_filtrado: pd.DataFrame, lojas=None, categorias=None, export: bool = False):
    """
    Aba de Repasse. Se export=True, retorna {titulo: fig}.
    """
    figs = {}
    dff = _aplica_filtros(df_filtrado, lojas, categorias)
    df_rep = prepare_repasse_cols(dff)

    if not export:
        st.subheader("KPIs de Repasse")
        _kpis_repasse_cfo(df_rep)

        st.markdown("### Séries Temporais de Repasse")
        col1, col2 = st.columns(2)
        with col1:
            if {"data","repasse_lojista"}.issubset(df_rep.columns):
                s = df_rep.copy()
                s["dia"] = pd.to_datetime(s["data"], errors="coerce").dt.to_period("D").dt.to_timestamp()
                g = (s.groupby("dia", as_index=False)["repasse_lojista"].sum().sort_values("dia"))
                fig = px.line(g, x="dia", y="repasse_lojista", markers=True,
                              title="Repasse ao Lojista por Dia (R$)", labels={"dia":"Dia","repasse_lojista":"R$"})
                st.plotly_chart(fig, use_container_width=True)
        with col2:
            if {"data","repasse_picmoney"}.issubset(df_rep.columns):
                s = df_rep.copy()
                s["dia"] = pd.to_datetime(s["data"], errors="coerce").dt.to_period("D").dt.to_timestamp()
                g = (s.groupby("dia", as_index=False)["repasse_picmoney"].sum().sort_values("dia"))
                fig = px.line(g, x="dia", y="repasse_picmoney", markers=True,
                              title="Comissão PicMoney por Dia (R$)", labels={"dia":"Dia","repasse_picmoney":"R$"})
                st.plotly_chart(fig, use_container_width=True)

        st.markdown("### Maiores Lojas")
        c3, c4 = st.columns(2)
        with c3:
            fig = _col_lojas_por_valor(df_rep, top=15)
            if fig: st.plotly_chart(fig, use_container_width=True)
        with c4:
            fig = _col_lojas_por_repasse_valor(df_rep, top=15)
            if fig: st.plotly_chart(fig, use_container_width=True)

        c5, c6 = st.columns(2)
        with c5:
            fig = _col_lojas_por_repasse_pct(df_rep, top=15, min_valor=1000)
            if fig: st.plotly_chart(fig, use_container_width=True)
        with c6:
            fig = _pizza_tipo_cupom(df_rep)
            if fig: st.plotly_chart(fig, use_container_width=True)
        return None

    # ----- Modo export: apenas coletar figuras -----
    if {"data","repasse_lojista"}.issubset(df_rep.columns):
        s = df_rep.copy()
        s["dia"] = pd.to_datetime(s["data"], errors="coerce").dt.to_period("D").dt.to_timestamp()
        g = (s.groupby("dia", as_index=False)["repasse_lojista"].sum().sort_values("dia"))
        figs["Repasse ao Lojista por Dia (R$)"] = px.line(
            g, x="dia", y="repasse_lojista", markers=True,
            title="Repasse ao Lojista por Dia (R$)", labels={"dia":"Dia","repasse_lojista":"R$"}
        )
    if {"data","repasse_picmoney"}.issubset(df_rep.columns):
        s = df_rep.copy()
        s["dia"] = pd.to_datetime(s["data"], errors="coerce").dt.to_period("D").dt.to_timestamp()
        g = (s.groupby("dia", as_index=False)["repasse_picmoney"].sum().sort_values("dia"))
        figs["Comissão PicMoney por Dia (R$)"] = px.line(
            g, x="dia", y="repasse_picmoney", markers=True,
            title="Comissão PicMoney por Dia (R$)", labels={"dia":"Dia","repasse_picmoney":"R$"}
        )

    f = _col_lojas_por_valor(df_rep, top=15)
    if f: figs["Maiores Lojas por Valor de Cupons (R$)"] = f
    f = _col_lojas_por_repasse_valor(df_rep, top=15)
    if f: figs["Maiores Lojas por Repasse ao Lojista (R$)"] = f
    f = _col_lojas_por_repasse_pct(df_rep, top=15, min_valor=1000)
    if f: figs["Participação do Lojista (%) – Maiores Lojas"] = f
    f = _pizza_tipo_cupom(df_rep)
    if f: figs["Composição por Tipo de Cupom (R$)"] = f

    return figs
