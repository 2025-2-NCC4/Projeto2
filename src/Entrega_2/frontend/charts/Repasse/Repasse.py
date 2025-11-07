import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

# ---------------------------
# Utils
# ---------------------------
def fmt_br_money(x):
    try:
        return f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "—"

def _to_num(df, cols):
    df = df.copy()
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df

# ---------------------------
# Pré-processamento de repasse
# ---------------------------
def prepare_repasse_cols(df):
    df = df.copy()

    # datas
    if "data" in df.columns:
        df["data"] = pd.to_datetime(df["data"], errors="coerce")

    # numéricos
    df = _to_num(df, ["valor_cupom", "repasse_picmoney"])

    # colunas derivadas
    if "valor_cupom" in df.columns and "repasse_picmoney" in df.columns:
        df["repasse_lojista"] = df["valor_cupom"] - df["repasse_picmoney"]
        df["take_rate"] = np.where(
            df["valor_cupom"] > 0,
            df["repasse_picmoney"] / df["valor_cupom"],
            np.nan,
        )
    return df

# ---------------------------
# KPIs
# ---------------------------
def kpis_repasse(df):
    valor_bruto = df["valor_cupom"].sum() if "valor_cupom" in df.columns else np.nan
    rep_pic = df["repasse_picmoney"].sum() if "repasse_picmoney" in df.columns else np.nan
    rep_loja = (
        df["repasse_lojista"].sum()
        if "repasse_lojista" in df.columns
        else (valor_bruto - rep_pic if np.isfinite(valor_bruto) and np.isfinite(rep_pic) else np.nan)
    )
    take_rate = (rep_pic / valor_bruto) if (np.isfinite(rep_pic) and np.isfinite(valor_bruto) and valor_bruto > 0) else np.nan

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Valor Bruto (R$)", fmt_br_money(valor_bruto) if np.isfinite(valor_bruto) else "—")
    c2.metric("Repasse PicMoney (R$)", fmt_br_money(rep_pic) if np.isfinite(rep_pic) else "—")
    c3.metric("Repasse Lojista (R$)", fmt_br_money(rep_loja) if np.isfinite(rep_loja) else "—")
    c4.metric("Take Rate (%)", f"{take_rate*100:.2f}%" if np.isfinite(take_rate) else "—")

# ---------------------------
# Gráficos básicos
# ---------------------------
def fig_repasse_timeseries(df, col="repasse_lojista", title="Repasse Lojista por dia"):
    if "data" not in df.columns or col not in df.columns:
        return None
    d = df.groupby(df["data"].dt.date)[col].sum().reset_index()
    d.columns = ["Data", "Valor"]
    return px.line(d, x="Data", y="Valor", markers=True, title=title, labels={"Valor": "R$"})

def fig_repasse_ranking(df, col_valor="repasse_lojista", eixo="nome_estabelecimento",
                        titulo="Top Estabelecimentos por Repasse Lojista (R$)"):
    if eixo not in df.columns or col_valor not in df.columns:
        return None
    d = (df.groupby(eixo)[col_valor].sum()
           .reset_index()
           .sort_values(col_valor, ascending=False)
           .head(15))
    d["Label"] = d[col_valor].map(fmt_br_money)
    fig = px.bar(d, x=col_valor, y=eixo, orientation="h", text="Label", title=titulo,
                 labels={col_valor: "R$", eixo: "Estabelecimento"})
    fig.update_traces(textposition="outside")
    return fig

def tabela_repasse(df, eixo="nome_estabelecimento"):
    req = {"valor_cupom", "repasse_picmoney", eixo}
    if not req.issubset(df.columns):
        return None

    d = (df.groupby(eixo)
            .agg(transacoes=("celular", "count"),
                 valor_bruto=("valor_cupom", "sum"),
                 rep_pic=("repasse_picmoney", "sum"))
            .reset_index())
    d["rep_loja"] = d["valor_bruto"] - d["rep_pic"]
    d["ticket_repasse"] = np.where(d["transacoes"] > 0, d["rep_loja"] / d["transacoes"], np.nan)
    d["take_rate"] = np.where(d["valor_bruto"] > 0, d["rep_pic"] / d["valor_bruto"], np.nan)

    for c in ["valor_bruto", "rep_pic", "rep_loja", "ticket_repasse"]:
        d[c] = d[c].map(fmt_br_money)
    d["take_rate"] = (d["take_rate"] * 100).round(2).astype(str) + "%"

    return d


def fig_pizza_tipo_cupom(df):
    """Composição por tipo de cupom (soma do valor_cupom)."""
    if "tipo_cupom" not in df.columns or "valor_cupom" not in df.columns:
        return None
    d = (df.groupby("tipo_cupom")["valor_cupom"].sum()
           .reset_index()
           .sort_values("valor_cupom", ascending=False))
    d["label"] = d["valor_cupom"].map(fmt_br_money)
    fig = px.pie(d, names="tipo_cupom", values="valor_cupom",
                 title="Composição por Tipo de Cupom (R$)", hole=0.4)
    fig.update_traces(text=d["label"], textposition="inside")
    return fig

def fig_top_lojas_valor_cupom(df, top=15):
    if "nome_estabelecimento" not in df.columns or "valor_cupom" not in df.columns:
        return None
    d = (df.groupby("nome_estabelecimento")["valor_cupom"].sum()
           .reset_index()
           .sort_values("valor_cupom", ascending=False)
           .head(top))
    d["Label"] = d["valor_cupom"].map(fmt_br_money)
    fig = px.bar(d, x="valor_cupom", y="nome_estabelecimento", orientation="h",
                 text="Label", title="Top Lojas por Valor de Cupons (R$)",
                 labels={"valor_cupom": "R$", "nome_estabelecimento": "Estabelecimento"})
    fig.update_traces(textposition="outside")
    return fig

def fig_top_lojas_repasse_valor(df, top=15):
    if "nome_estabelecimento" not in df.columns or "repasse_lojista" not in df.columns:
        return None
    d = (df.groupby("nome_estabelecimento")["repasse_lojista"].sum()
           .reset_index()
           .sort_values("repasse_lojista", ascending=False)
           .head(top))
    d["Label"] = d["repasse_lojista"].map(fmt_br_money)
    fig = px.bar(d, x="repasse_lojista", y="nome_estabelecimento", orientation="h",
                 text="Label", title="Top Lojas por Repasse ao Lojista (R$)",
                 labels={"repasse_lojista": "R$", "nome_estabelecimento": "Estabelecimento"})
    fig.update_traces(textposition="outside")
    return fig

def fig_top_lojas_repasse_pct(df, top=15, min_valor=1000):
    """
    % de repasse ao lojista = repasse_lojista / valor_cupom.
    Filtra lojas com valor_cupom mínimo para evitar outliers.
    """
    req = {"nome_estabelecimento", "repasse_lojista", "valor_cupom"}
    if not req.issubset(df.columns):
        return None

    g = (df.groupby("nome_estabelecimento")
            .agg(rep_loja=("repasse_lojista", "sum"),
                 valor=("valor_cupom", "sum"))
            .reset_index())

    g = g[g["valor"] >= min_valor].copy()

    g["repasse_pct_lojista"] = np.where(g["valor"] > 0, g["rep_loja"] / g["valor"], np.nan)
    g = g.dropna(subset=["repasse_pct_lojista"])\
         .sort_values("repasse_pct_lojista", ascending=False)\
         .head(top)

    g["pct_label"] = (g["repasse_pct_lojista"] * 100).round(2).astype(str) + "%"

    fig = px.bar(g, x="repasse_pct_lojista", y="nome_estabelecimento", orientation="h",
                 text="pct_label", title="Top Lojas por % de Repasse ao Lojista",
                 labels={"repasse_pct_lojista": "%", "nome_estabelecimento": "Estabelecimento"})
    fig.update_traces(textposition="outside")
    fig.update_layout(xaxis_tickformat=".0%")
    return fig
