import numpy as np
import pandas as pd
import plotly.express as px

def fmt_br_money(x):
    try:
        return f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "—"

def _to_num(df, cols):
    d = df.copy()
    for c in cols:
        if c in d.columns:
            d[c] = pd.to_numeric(d[c], errors="coerce")
    return d

def _first_present(d: pd.DataFrame, candidates):
    for c in candidates:
        if c in d.columns:
            return c
    low = {c.lower(): c for c in d.columns}
    for c in candidates:
        if c.lower() in low:
            return low[c.lower()]
    return None

def prepare_liquidez_cols(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    if "data" in d.columns:
        d["data"] = pd.to_datetime(d["data"], errors="coerce")
        d = d.dropna(subset=["data"])

    col_compra = _first_present(d, ["valor_compra","valor_bruto_compra","vl_compra","valor_total","compra","vl_total"])
    col_cupom  = _first_present(d, ["valor_cupom","vl_cupom","cupom","desconto"])
    col_rep    = _first_present(d, ["repasse_picmoney","repasse","comissao","taxa"])

    if col_compra and col_compra != "valor_compra":
        d = d.rename(columns={col_compra: "valor_compra"})
    if col_cupom and col_cupom != "valor_cupom":
        d = d.rename(columns={col_cupom: "valor_cupom"})
    if col_rep and col_rep != "repasse_picmoney":
        d = d.rename(columns={col_rep: "repasse_picmoney"})

    d = _to_num(d, ["valor_compra","valor_cupom","repasse_picmoney"])
    d["_liquidez_fallback"] = False

    if d.get("valor_compra") is not None and d["valor_compra"].notna().any() and "valor_cupom" in d.columns:
        # Liquidez REAL
        d["receita_liquida"] = d["valor_compra"] - d["valor_cupom"]
        d["margem_liquida"]  = np.where(d["valor_compra"]>0, d["receita_liquida"]/d["valor_compra"], np.nan)
    elif "valor_cupom" in d.columns and "repasse_picmoney" in d.columns:
        # FALLBACK (usa cupom e repasse)
        d["_liquidez_fallback"] = True
        d["receita_liquida"] = d["valor_cupom"] - d["repasse_picmoney"]          # ~ lucro_bruto
        d["margem_liquida"]  = np.where(d["valor_cupom"]>0, d["receita_liquida"]/d["valor_cupom"], np.nan)
        if "valor_compra" not in d.columns:
            d["valor_compra"] = np.nan
    else:
        for c in ["valor_compra","valor_cupom","repasse_picmoney","receita_liquida","margem_liquida"]:
            if c not in d.columns:
                d[c] = np.nan

    return d

def kpis_liquidez(df: pd.DataFrame) -> dict:
    d = prepare_liquidez_cols(df)

    receita_liq = d["receita_liquida"].sum(min_count=1)

    # Base da margem: compra (real) ou cupom (fallback)
    fallback = bool(d["_liquidez_fallback"].any())
    if fallback:
        base_margem = d["valor_cupom"].sum(min_count=1)
    else:
        base_margem = d["valor_compra"].sum(min_count=1)

    margem_liq = (receita_liq / base_margem) if (pd.notna(receita_liq) and pd.notna(base_margem) and base_margem > 0) else np.nan

    return {
        "receita_liquida": receita_liq,
        "margem_liquida":  margem_liq,
        "fallback": fallback
    }

# === Helpers de gráfico / modos ===
def _apply_mode_bar(fig, mode: str, y_percent: bool):
    if mode == "percent" or y_percent:
        fig.update_layout(yaxis_tickformat=".0%")
    fig.update_traces(textposition="outside")
    return fig

# === Gráficos com modos e top-N ===
def fig_top_lojas_receita_liquida(df: pd.DataFrame, top=15, mode: str = "valores"):
    d = prepare_liquidez_cols(df)
    if "nome_estabelecimento" not in d.columns or d["receita_liquida"].isna().all():
        return None

    g = (d.groupby("nome_estabelecimento")["receita_liquida"]
           .sum().reset_index().sort_values("receita_liquida", ascending=False).head(top))
    total = g["receita_liquida"].sum()

    if mode == "percent":
        g["share"] = np.where(total > 0, g["receita_liquida"] / total, np.nan)
        g["Label"] = (g["share"]*100).round(2).astype(str) + "%"
        fig = px.bar(
            g, x="nome_estabelecimento", y="share", text="Label",
            title=f"Maiores Lojas por Receita Líquida (% de {fmt_br_money(total)})",
            labels={"nome_estabelecimento":"Estabelecimento", "share":"%"}
        )
        return _apply_mode_bar(fig, "percent", True)

    g["Label"] = g["receita_liquida"].map(fmt_br_money)
    fig = px.bar(
        g, x="nome_estabelecimento", y="receita_liquida", text="Label",
        title="Maiores Lojas por Receita Líquida (R$)",
        labels={"nome_estabelecimento":"Estabelecimento","receita_liquida":"R$"}
    )
    return _apply_mode_bar(fig, "valores", False)

# --- Série diária de Receita Líquida ---
def fig_receita_liquida_diaria(df: pd.DataFrame):
    d = prepare_liquidez_cols(df)
    if "data" not in d.columns or d["receita_liquida"].isna().all():
        return None
    d["dia"] = d["data"].dt.to_period("D").dt.to_timestamp()
    g = d.groupby("dia")["receita_liquida"].sum().reset_index()

    import plotly.express as px
    fig = px.line(
        g, x="dia", y="receita_liquida", markers=True,
        title="Receita Líquida por Dia",
        labels={"dia": "Dia", "receita_liquida": "R$"}
    )
    return fig


def fig_custo_por_tipo_cupom(df: pd.DataFrame, mode: str = "percent"):
    d = prepare_liquidez_cols(df)
    if "tipo_cupom" not in d.columns or "valor_cupom" not in d.columns:
        return None
    g = d.groupby("tipo_cupom")["valor_cupom"].sum().reset_index()
    total = g["valor_cupom"].sum()

    if mode == "percent":
        g["participacao"] = np.where(total > 0, g["valor_cupom"]/total, np.nan)
        g["Label"] = (g["participacao"]*100).round(2).astype(str)+"%"
        fig = px.bar(
            g, x="tipo_cupom", y="participacao", text="Label",
            title="Alocação de Custo por Tipo de Cupom (%)",
            labels={"tipo_cupom":"Tipo de Cupom","participacao":"%"}
        )
        return _apply_mode_bar(fig, "percent", True)

    g["Label"] = g["valor_cupom"].map(fmt_br_money)
    fig = px.bar(
        g, x="tipo_cupom", y="valor_cupom", text="Label",
        title="Alocação de Custo por Tipo de Cupom (R$)",
        labels={"tipo_cupom":"Tipo de Cupom","valor_cupom":"R$"}
    )
    return _apply_mode_bar(fig, "valores", False)

def fig_receita_liquida_por_canal(df: pd.DataFrame, mode: str = "valores"):
    d = prepare_liquidez_cols(df)
    if "local_captura" not in d.columns or d["receita_liquida"].isna().all():
        return None
    g = d.groupby("local_captura")["receita_liquida"].sum().reset_index().sort_values("receita_liquida", ascending=False)
    total = g["receita_liquida"].sum()

    if mode == "percent":
        g["share"] = np.where(total > 0, g["receita_liquida"]/total, np.nan)
        g["Label"] = (g["share"]*100).round(2).astype(str)+"%"
        fig = px.bar(
            g, x="local_captura", y="share", text="Label",
            title=f"Receita Líquida por Canal (% de {fmt_br_money(total)})",
            labels={"local_captura":"Canal","share":"%"}
        )
        return _apply_mode_bar(fig, "percent", True)

    g["Label"] = g["receita_liquida"].map(fmt_br_money)
    fig = px.bar(
        g, x="local_captura", y="receita_liquida", text="Label",
        title="Receita Líquida por Canal de Captação (R$)",
        labels={"local_captura":"Canal","receita_liquida":"R$"}
    )
    return _apply_mode_bar(fig, "valores", False)

def fig_margem_liquida_por_tipo(df: pd.DataFrame, min_receita=1000):
    """
    Gera gráfico de colunas com a Margem Líquida (%) por Tipo de Cupom.
    Exibe apenas tipos com receita mínima para evitar distorção.
    """
    d = prepare_liquidez_cols(df)

    # validações básicas
    if "tipo_cupom" not in d.columns or d["receita_liquida"].isna().all():
        return None

    base = "valor_compra" if "valor_compra" in d.columns and d["valor_compra"].notna().any() else "valor_cupom"
    g = (
        d.groupby("tipo_cupom")
         .agg(receita=(base, "sum"), receita_liq=("receita_liquida", "sum"))
         .reset_index()
    )

    g = g[g["receita"].fillna(0) >= min_receita].copy()
    if g.empty:
        return None

    g["margem_liq"] = np.where(g["receita"] > 0, g["receita_liq"] / g["receita"], np.nan)
    g["pct_label"] = (g["margem_liq"] * 100).round(2).astype(str) + "%"

    fig = px.bar(
        g,
        x="tipo_cupom",
        y="margem_liq",
        text="pct_label",
        title="Margem Líquida por Tipo de Cupom (%)",
        labels={"tipo_cupom": "Tipo de Cupom", "margem_liq": "%"},
    )

    fig.update_traces(textposition="outside")
    fig.update_layout(yaxis_tickformat=".0%")

    return fig
