import pandas as pd
import numpy as np
import plotly.express as px

# Dicionário único de meses (use este em todo o módulo)
MESES_PT = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho",
    7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}

def _mes_numero(mes):
    """Retorna (mes_num, MESES_PT). Aceita número ou string PT-BR ('Julho')."""
    if isinstance(mes, str):
        mes_num = {v.lower(): k for k, v in MESES_PT.items()}.get(mes.lower())
    else:
        mes_num = int(mes)
    return mes_num, MESES_PT


# =========================
# Lojas por número de capturas (mês/ano)
# =========================
def usuarios_loja(df, mes, ano, modo="valores"):
    df = df.copy()
    req = {"data", "celular", "nome_estabelecimento"}
    if not req.issubset(df.columns):
        faltando = ", ".join(sorted(req - set(df.columns)))
        return px.bar(title=f"Colunas obrigatórias ausentes: {faltando}")

    df["data"] = pd.to_datetime(df["data"], errors="coerce")
    df = df.dropna(subset=["data"])

    m, meses_pt = _mes_numero(mes)
    if m not in range(1, 13):
        return px.bar(title=f"Mês inválido: {mes}")

    df = df[(df["data"].dt.year == int(ano)) & (df["data"].dt.month == m)]
    if df.empty:
        return px.bar(title=f"Lojas por Número de Capturas – {meses_pt[m]} {ano} (sem dados)")

    s = (df.groupby("nome_estabelecimento")["celular"]
           .nunique().sort_values(ascending=False)
           .reset_index(name="valor"))

    total = s["valor"].sum()
    s["pct"] = (s["valor"] / total).fillna(0.0) if total > 0 else 0.0
    titulo = f"Lojas por Número de Capturas – {meses_pt[m]} {ano}"

    if modo.lower() == "percentual":
        fig = px.bar(
            s, y="nome_estabelecimento", x="pct", orientation="h",
            text=s["pct"].map(lambda x: f"{x:.1%}"),
            color="pct", color_continuous_scale="Blues",
            title=titulo + " (Percentual)",
            labels={"nome_estabelecimento": "Lojas", "pct": "% do total"}
        )
        fig.update_layout(height=500, xaxis_tickformat=".0%")
        return fig

    text_series = (
        s["valor"].astype(int).astype(str)
        if modo.lower() == "valores"
        else s.apply(lambda r: f'{int(r["valor"])}  ({r["pct"]:.1%})', axis=1)
    )

    fig = px.bar(
        s, y="nome_estabelecimento", x="valor", orientation="h",
        text=text_series, color="valor", color_continuous_scale="Blues",
        title=titulo, labels={"nome_estabelecimento": "Lojas", "valor": "Capturas"}
    )
    fig.update_layout(height=500)
    return fig


# =========================
# Categorias por número de capturas (mês/ano)
# =========================
def capturas_categoria(df, mes, ano, modo="valores"):
    df = df.copy()
    req = {"data", "celular", "categoria_estabelecimento"}
    if not req.issubset(df.columns):
        faltando = ", ".join(sorted(req - set(df.columns)))
        return px.bar(title=f"Colunas obrigatórias ausentes: {faltando}")

    df["data"] = pd.to_datetime(df["data"], errors="coerce")  # <- corrigido (era 'dataa')
    df = df.dropna(subset=["data"])

    m, meses_pt = _mes_numero(mes)
    if m not in range(1, 13):
        return px.bar(title=f"Mês inválido: {mes}")

    df = df[(df["data"].dt.year == int(ano)) & (df["data"].dt.month == m)]
    if df.empty:
        return px.bar(title=f"Categorias por Número de Capturas – {meses_pt[m]} {ano} (sem dados)")

    s = (df.groupby("categoria_estabelecimento")["celular"]
           .nunique().sort_values(ascending=False)
           .reset_index(name="valor"))

    total = s["valor"].sum()
    s["pct"] = (s["valor"] / total).fillna(0.0) if total > 0 else 0.0
    titulo = f"Categorias por Número de Capturas – {meses_pt[m]} {ano}"

    if modo.lower() == "percentual":
        fig = px.bar(
            s, y="categoria_estabelecimento", x="pct", orientation="h",
            text=s["pct"].map(lambda x: f"{x:.1%}"),
            color="pct", color_continuous_scale="Blues",
            title=titulo + " (Percentual)",
            labels={"categoria_estabelecimento": "Categorias", "pct": "% do total"}
        )
        fig.update_layout(height=500, xaxis_tickformat=".0%")
        return fig

    text_series = (
        s["valor"].astype(int).astype(str)
        if modo.lower() == "valores"
        else s.apply(lambda r: f'{int(r["valor"])}  ({r["pct"]:.1%})', axis=1)
    )
    fig = px.bar(
        s, y="categoria_estabelecimento", x="valor", orientation="h",
        text=text_series, color="valor", color_continuous_scale="Blues",
        title=titulo, labels={"categoria_estabelecimento": "Categorias", "valor": "Capturas"}
    )
    fig.update_layout(height=500)
    return fig


# =========================
# Resumo de parceiros (retorna tupla simples)
# =========================
def resumo_parceiros(df, mes, ano):
    dff = df.copy()
    req_cols = {"data", "nome_estabelecimento", "categoria_estabelecimento"}
    if not req_cols.issubset(dff.columns):
        return 0, 0

    dff["data"] = pd.to_datetime(dff["data"], errors="coerce")
    dff = dff.dropna(subset=["data"])

    m, _ = _mes_numero(mes)
    if m not in range(1, 13):
        return 0, 0

    dff = dff[(dff["data"].dt.year == int(ano)) & (dff["data"].dt.month == m)]
    total_lojas = int(dff["nome_estabelecimento"].nunique()) if not dff.empty else 0
    total_categorias = int(dff["categoria_estabelecimento"].nunique()) if not dff.empty else 0
    return total_lojas, total_categorias


# =========================
# Tipo de cupom (pie)
# =========================
def tipo_cupom(df, ano, mes=None, nome_estabelecimento=None, categoria_estabelecimento=None, modo="valores"):
    df = df.copy()
    req = {"data", "celular", "tipo_cupom"}
    if not req.issubset(df.columns):
        faltando = ", ".join(sorted(req - set(df.columns)))
        return px.bar(title=f"Colunas obrigatórias ausentes: {faltando}")

    df["data"] = pd.to_datetime(df["data"], errors="coerce")
    df = df.dropna(subset=["data"])

    # filtro por ano/mês
    df = df[df["data"].dt.year == int(ano)]

    mes_num = None
    sufixo_mes = ""
    if mes is not None:
        mes_num, _ = _mes_numero(mes)
        if mes_num in range(1, 13):
            df = df[df["data"].dt.month == mes_num]
            sufixo_mes = f" – {MESES_PT[mes_num]}"

    # filtros nome/categoria
    def _norm_one(x): return str(x).strip().casefold()
    sufixo_loja = ""

    if nome_estabelecimento:
        if not isinstance(nome_estabelecimento, (list, tuple, set)):
            nome_estabelecimento = [nome_estabelecimento]
        nomes_norm = {_norm_one(x) for x in nome_estabelecimento if str(x).strip() not in {"", "todas", "all"}}
        if nomes_norm and "nome_estabelecimento" in df.columns:
            df = df[df["nome_estabelecimento"].astype(str).str.strip().str.casefold().isin(nomes_norm)]
            sufixo_loja = f" – {', '.join(sorted({str(x) for x in nome_estabelecimento}))}"

    if (not nome_estabelecimento) and categoria_estabelecimento:
        if not isinstance(categoria_estabelecimento, (list, tuple, set)):
            categoria_estabelecimento = [categoria_estabelecimento]
        tipos_norm = {_norm_one(x) for x in categoria_estabelecimento if str(x).strip() not in {"", "todas", "all"}}
        if tipos_norm and "categoria_estabelecimento" in df.columns:
            df = df[df["categoria_estabelecimento"].astype(str).str.strip().str.casefold().isin(tipos_norm)]
            sufixo_loja = f" – {', '.join(sorted({str(x) for x in categoria_estabelecimento}))}"

    if df.empty:
        return px.bar(title=f"Sem dados para {ano}{sufixo_mes}{sufixo_loja}")

    s = (df.groupby("tipo_cupom")["celular"]
           .nunique()
           .reset_index(name="valor")
           .sort_values("valor", ascending=False))

    total = s["valor"].sum()
    s["pct"] = (s["valor"] / total).fillna(0.0) if total > 0 else 0.0
    titulo = f"Distribuição por Tipo de Cupom – {ano}{sufixo_mes}{sufixo_loja}"

    if modo.lower() == "percentual":
        fig = px.pie(
            s, names="tipo_cupom", values="pct",
            title=titulo + " (Percentual)", hole=0.35
        )
        fig.update_traces(
            textposition="inside",
            texttemplate="%{label}<br>%{percent:.1%}",
            hovertemplate="<b>%{label}</b><br>Participação: %{percent:.1%}<extra></extra>"
        )
        fig.update_layout(height=500, legend_title_text="Tipo de Cupom")
        return fig

    s["texto"] = (
        s["valor"].astype(int).astype(str)
        if modo.lower() == "valores"
        else s.apply(lambda r: f'{int(r["valor"])} ({r["pct"]:.1%})', axis=1)
    )

    fig = px.pie(
        s, names="tipo_cupom", values="valor",
        title=titulo, hole=0.35
    )
    fig.update_traces(
        textposition="inside",
        texttemplate="%{label}<br>%{customdata}",
        customdata=s["texto"],
        hovertemplate="<b>%{label}</b><br>Capturas: %{value:d}<br>Participação: %{percent:.1%}<extra></extra>"
    )
    fig.update_layout(height=500, legend_title_text="Tipo de Cupom")
    return fig


def cupons_por_loja(df, mes, ano, modo="valores"):
    """
    x = nome_estabelecimento | y = quantidade (valores | percentual | ambos) | cor = tipo_cupom
    """
    req = {"data", "nome_estabelecimento", "tipo_cupom", "celular"}
    if not req.issubset(df.columns):
        faltando = ", ".join(sorted(req - set(df.columns)))
        return px.bar(title=f"Colunas obrigatórias ausentes: {faltando}")

    dff = df.copy()
    dff["data"] = pd.to_datetime(dff["data"], errors="coerce")
    dff = dff.dropna(subset=["data"])

    m, meses_pt = _mes_numero(mes)
    if m not in range(1, 13):
        return px.bar(title=f"Mês inválido: {mes}")

    dff = dff[(dff["data"].dt.year == int(ano)) & (dff["data"].dt.month == m)]
    if dff.empty:
        return px.bar(title=f"Tipo de Cupom por Loja — {meses_pt[m]} {ano} (sem dados)")

    g = (dff.groupby(["nome_estabelecimento", "tipo_cupom"])["celular"]
            .nunique()
            .reset_index(name="valor"))

    tot_loja = g.groupby("nome_estabelecimento")["valor"].transform("sum")
    g["pct"] = (g["valor"] / tot_loja).fillna(0.0)

    titulo = f"Tipo de Cupom por Loja — {meses_pt[m]} {ano}"

    if modo.lower() == "percentual":
        fig = px.bar(
            g, x="nome_estabelecimento", y="pct", color="tipo_cupom",
            barmode="group", text=g["pct"].map(lambda x: f"{x:.1%}"),
            labels={"nome_estabelecimento": "Loja", "pct": "% na loja", "tipo_cupom": "Tipo de Cupom"},
            title=titulo + " (Percentual)"
        )
        fig.update_layout(xaxis_tickangle=-30, height=520, yaxis_tickformat=".0%")
        return fig

    g["texto"] = g.apply(
        lambda r: f"{int(r['valor'])} ({r['pct']:.1%})" if modo.lower() == "ambos" else f"{int(r['valor'])}",
        axis=1
    )
    fig = px.bar(
        g, x="nome_estabelecimento", y="valor", color="tipo_cupom",
        barmode="group", text="texto",
        labels={"nome_estabelecimento": "Loja", "valor": "Capturas (players únicos)", "tipo_cupom": "Tipo de Cupom"},
        title=titulo
    )
    fig.update_layout(xaxis_tickangle=-30, height=520)
    return fig


def cupons_por_categoria(df, mes, ano, modo="valores"):
    """
    x = categoria_estabelecimento | y = quantidade (valores | percentual | ambos) | cor = tipo_cupom
    """
    req = {"data", "categoria_estabelecimento", "tipo_cupom", "celular"}
    if not req.issubset(df.columns):
        faltando = ", ".join(sorted(req - set(df.columns)))
        return px.bar(title=f"Colunas obrigatórias ausentes: {faltando}")

    dff = df.copy()
    dff["data"] = pd.to_datetime(dff["data"], errors="coerce")
    dff = dff.dropna(subset=["data"])

    m, meses_pt = _mes_numero(mes)
    if m not in range(1, 13):
        return px.bar(title=f"Mês inválido: {mes}")

    dff = dff[(dff["data"].dt.year == int(ano)) & (dff["data"].dt.month == m)]
    if dff.empty:
        return px.bar(title=f"Tipo de Cupom por Categoria — {meses_pt[m]} {ano} (sem dados)")

    g = (dff.groupby(["categoria_estabelecimento", "tipo_cupom"])["celular"]
            .nunique()
            .reset_index(name="valor"))

    tot_cat = g.groupby("categoria_estabelecimento")["valor"].transform("sum")
    g["pct"] = (g["valor"] / tot_cat).fillna(0.0)

    titulo = f"Tipo de Cupom por Categoria — {meses_pt[m]} {ano}"

    if modo.lower() == "percentual":
        fig = px.bar(
            g, x="categoria_estabelecimento", y="pct", color="tipo_cupom",
            barmode="group", text=g["pct"].map(lambda x: f"{x:.1%}"),
            labels={"categoria_estabelecimento": "Categoria", "pct": "% na categoria", "tipo_cupom": "Tipo de Cupom"},
            title=titulo + " (Percentual)"
        )
        fig.update_layout(xaxis_tickangle=-30, height=520, yaxis_tickformat=".0%")
        return fig

    g["texto"] = g.apply(
        lambda r: f"{int(r['valor'])} ({r['pct']:.1%})" if modo.lower() == "ambos" else f"{int(r['valor'])}",
        axis=1
    )
    fig = px.bar(
        g, x="categoria_estabelecimento", y="valor", color="tipo_cupom",
        barmode="group", text="texto",
        labels={"categoria_estabelecimento": "Categoria", "valor": "Capturas (players únicos)", "tipo_cupom": "Tipo de Cupom"},
        title=titulo
    )
    fig.update_layout(xaxis_tickangle=-30, height=520)
    return fig


def heatmap_capturas_mapa(
    df, mes, ano,
    usar_unicos_por_player=True,
    filtros=None,          # {"categoria_estabelecimento":[...], "nome_estabelecimento":[...], "tipo_cupom":[...]}
    radius=25, opacity=0.7,
    zoom=None, center=None
):
    req = {"data", "latitude", "longitude"}
    if not req.issubset(df.columns):
        faltando = ", ".join(sorted(req - set(df.columns)))
        return px.scatter(title=f"Colunas ausentes: {faltando}")

    dff = df.copy()
    dff["data"] = pd.to_datetime(dff["data"], errors="coerce")
    dff = dff.dropna(subset=["data", "latitude", "longitude"])

    # período
    m, _ = _mes_numero(mes)
    dff = dff[(dff["data"].dt.year == int(ano)) & (dff["data"].dt.month == m)]

    # filtros opcionais
    def _apply_filter(col, values):
        nonlocal dff
        if col in dff.columns and values:
            if not isinstance(values, (list, tuple, set)):
                values = [values]
            vals = {str(v).strip().casefold() for v in values if str(v).strip()}
            dff = dff[dff[col].astype(str).str.strip().str.casefold().isin(vals)]

    if isinstance(filtros, dict):
        _apply_filter("categoria_estabelecimento", filtros.get("categoria_estabelecimento"))
        _apply_filter("nome_estabelecimento", filtros.get("nome_estabelecimento"))
        _apply_filter("tipo_cupom", filtros.get("tipo_cupom"))

    if dff.empty:
        return px.scatter(title=f"Heatmap de Capturas — {MESES_PT[m]} {ano} (sem dados)")

    # peso
    if usar_unicos_por_player and "celular" in dff.columns:
        g = (dff.groupby(["latitude", "longitude"])["celular"]
               .nunique()
               .reset_index(name="peso"))
    else:
        g = dff.assign(peso=1)[["latitude", "longitude", "peso"]]

    # centro e zoom
    if center is None:
        center = {"lat": float(g["latitude"].mean()), "lon": float(g["longitude"].mean())}
    if zoom is None:
        lat_span = float(g["latitude"].max() - g["latitude"].min() + 1e-6)
        lon_span = float(g["longitude"].max() - g["longitude"].min() + 1e-6)
        span = max(lat_span, lon_span)
        zoom = 12 if span < 0.02 else 10 if span < 0.1 else 8 if span < 0.5 else 6

    fig = px.density_mapbox(
        g, lat="latitude", lon="longitude", z="peso",
        radius=radius, opacity=opacity,
        center=center, zoom=zoom,
        mapbox_style="open-street-map",
        title=f"Heatmap de Capturas — {MESES_PT[m]} {ano}",
        labels={"peso": "Intensidade"}
    )
    return fig
