import pandas as pd
import numpy as np
import plotly.express as px

# -------------------------
# util: mês para número
# -------------------------
def _mes_numero(mes):
    meses_pt = {
        1:"Janeiro",2:"Fevereiro",3:"Março",4:"Abril",5:"Maio",6:"Junho",
        7:"Julho",8:"Agosto",9:"Setembro",10:"Outubro",11:"Novembro",12:"Dezembro"
    }
    if isinstance(mes, str):
        return {v.lower(): k for k, v in meses_pt.items()}.get(mes.lower()), meses_pt
    return int(mes), meses_pt

# =========================
# Lojas por número de capturas (mês/ano)
# =========================
def usuarios_loja(df, mes, ano, modo="valores"):
    df = df.copy()
    if "data" not in df.columns or "celular" not in df.columns or "nome_estabelecimento" not in df.columns:
        return px.bar(title="Colunas obrigatórias ausentes: data, celular, nome_estabelecimento")

    df["data"] = pd.to_datetime(df["data"], errors="coerce")
    df = df.dropna(subset=["data"])

    mes_num, meses_pt = _mes_numero(mes)
    if mes_num not in range(1, 13):
        return px.bar(title=f"Mês inválido: {mes}")

    df = df[(df["data"].dt.year == int(ano)) & (df["data"].dt.month == mes_num)]
    if df.empty:
        return px.bar(title=f"Lojas por Número de Capturas – {meses_pt[mes_num]} {ano} (sem dados)")

    s = (
        df.groupby("nome_estabelecimento")["celular"]
          .nunique()
          .sort_values(ascending=False)
          .reset_index(name="valor")
    )

    total = s["valor"].sum()
    s["pct"] = (s["valor"] / total).fillna(0.0) if total > 0 else 0.0
    titulo = f"Lojas por Número de Capturas – {meses_pt[mes_num]} {ano}"

    if modo.lower() == "percentual":
        fig = px.bar(
            s, y="nome_estabelecimento", x="pct", orientation="h",
            text=s["pct"].map(lambda x: f"{x:.1%}"),
            color="pct", color_continuous_scale="Blues",
            title=titulo + " (Percentual)",
            labels={"nome_estabelecimento":"Lojas","pct":"% do total"}
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
        title=titulo, labels={"nome_estabelecimento":"Lojas","valor":"Capturas"}
    )
    fig.update_layout(height=500)
    return fig

# =========================
# Categorias por número de capturas (mês/ano)
# =========================
def capturas_categoria(df, mes, ano, modo="valores"):
    df = df.copy()
    if "data" not in df.columns or "celular" not in df.columns or "categoria_estabelecimento" not in df.columns:
        return px.bar(title="Colunas obrigatórias ausentes: data, celular, categoria_estabelecimento")

    df["dataa"] = pd.to_datetime(df["data"], errors="coerce")
    df = df.dropna(subset=["data"])

    mes_num, meses_pt = _mes_numero(mes)
    if mes_num not in range(1, 13):
        return px.bar(title=f"Mês inválido: {mes}")

    df = df[(df["data"].dt.year == int(ano)) & (df["data"].dt.month == mes_num)]
    if df.empty:
        return px.bar(title=f"Categorias por Número de Capturas – {meses_pt[mes_num]} {ano} (sem dados)")

    s = (
        df.groupby("categoria_estabelecimento")["celular"]
          .nunique().sort_values(ascending=False)
          .reset_index(name="valor")
    )

    total = s["valor"].sum()
    s["pct"] = (s["valor"] / total).fillna(0.0) if total > 0 else 0.0
    titulo = f"Categorias por Número de Capturas – {meses_pt[mes_num]} {ano}"

    if modo.lower() == "percentual":
        fig = px.bar(
            s, y="categoria_estabelecimento", x="pct", orientation="h",
            text=s["pct"].map(lambda x: f"{x:.1%}"),
            color="pct", color_continuous_scale="Blues",
            title=titulo + " (Percentual)",
            labels={"categoria_estabelecimento":"Categorias","pct":"% do total"}
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
        title=titulo, labels={"categoria_estabelecimento":"Categorias","valor":"Capturas"}
    )
    fig.update_layout(height=500)
    return fig

# =========================
# Resumo de parceiros (retorna DataFrame p/ st.dataframe)
# =========================
def resumo_parceiros(df, mes, ano):
    df = df.copy()
    req_cols = {"data", "nome_estabelecimento", "categoria_estabelecimento"}
    if not req_cols.issubset(df.columns):
        return pd.DataFrame([{"total_lojas": 0, "total_categorias": 0}])

    df["data"] = pd.to_datetime(df["data"], errors="coerce")
    df = df.dropna(subset=["data"])

    mes_num, _ = _mes_numero(mes)
    if mes_num not in range(1, 13):
        return pd.DataFrame([{"total_lojas": 0, "total_categorias": 0}])

    dff = df[(df["data"].dt.year == int(ano)) & (df["data"].dt.month == mes_num)]
    out = {
        "total_lojas": int(dff["nome_estabelecimento"].nunique()),
        "total_categorias": int(dff["categoria_estabelecimento"].nunique()),
    }
    return pd.DataFrame([out])

# =========================
# Tipo de cupom (pie) — aceita listas em nome_estabelecimento/categoria_estabelecimento
# =========================
def tipo_cupom(df, ano, mes=None, nome_estabelecimento=None, categoria_estabelecimento=None, modo="valores"):
    df = df.copy()
    if "data" not in df.columns or "celular" not in df.columns or "tipo_cupom" not in df.columns:
        return px.bar(title="Colunas obrigatórias ausentes: data, celular, tipo_cupom")

    df["data"] = pd.to_datetime(df["data"], errors="coerce")
    df = df.dropna(subset=["data"])

    # --- filtro por ano/mês ---
    df = df[df["data"].dt.year == int(ano)]

    meses_pt = {
        1:"Janeiro",2:"Fevereiro",3:"Março",4:"Abril",5:"Maio",6:"Junho",
        7:"Julho",8:"Agosto",9:"Setembro",10:"Outubro",11:"Novembro",12:"Dezembro"
    }
    mes_num = None
    sufixo_mes = ""
    if mes is not None:
        mes_num, _meses = _mes_numero(mes)
        if mes_num in range(1, 13):
            df = df[df["data"].dt.month == mes_num]
            sufixo_mes = f" – {meses_pt[mes_num]}"

    # --- filtros opcionais por loja/categoria (aceita string ou lista) ---
    def _norm_one(x): 
        return str(x).strip().casefold()

    # nome_estabelecimento
    if nome_estabelecimento:
        if not isinstance(nome_estabelecimento, (list, tuple, set)):
            nome_estabelecimento = [nome_estabelecimento]
        nomes_norm = {_norm_one(x) for x in nome_estabelecimento if str(x).strip() not in {"", "todas", "all"}}
        if nomes_norm and "nome_estabelecimento" in df.columns:
            df = df[df["nome_estabelecimento"].astype(str).str.strip().str.casefold().isin(nomes_norm)]
            sufixo_loja = f" – {', '.join(sorted({str(x) for x in nome_estabelecimento}))}"
        else:
            sufixo_loja = ""
    else:
        sufixo_loja = ""

    # categoria_estabelecimento
    if (not nome_estabelecimento) and categoria_estabelecimento:
        if not isinstance(categoria_estabelecimento, (list, tuple, set)):
            categoria_estabelecimento = [categoria_estabelecimento]
        tipos_norm = {_norm_one(x) for x in categoria_estabelecimento if str(x).strip() not in {"", "todas", "all"}}
        if tipos_norm and "categoria_estabelecimento" in df.columns:
            df = df[df["categoria_estabelecimento"].astype(str).str.strip().str.casefold().isin(tipos_norm)]
            sufixo_loja = f" – {', '.join(sorted({str(x) for x in categoria_estabelecimento}))}"

    if df.empty:
        return px.bar(title=f"Sem dados para {ano}{sufixo_mes}{sufixo_loja}")

    # --- agregação ---
    s = (
        df.groupby("tipo_cupom")["celular"]
          .nunique()
          .reset_index(name="valor")
          .sort_values("valor", ascending=False)
    )

    total = s["valor"].sum()
    s["pct"] = (s["valor"] / total).fillna(0.0) if total > 0 else 0.0
    titulo = f"Distribuição por Tipo de Cupom – {ano}{sufixo_mes}{sufixo_loja}"

    # PERCENTUAL
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

    # VALORES / AMBOS
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
