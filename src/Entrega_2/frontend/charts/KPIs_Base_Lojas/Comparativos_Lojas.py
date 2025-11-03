import pandas as pd
import numpy as np
import plotly.express as px

def _mes_numero(mes):
    meses_pt = {1:"Janeiro",2:"Fevereiro",3:"Março",4:"Abril",5:"Maio",6:"Junho",
                7:"Julho",8:"Agosto",9:"Setembro",10:"Outubro",11:"Novembro",12:"Dezembro"}
    if isinstance(mes, str):
        return {v.lower(): k for k, v in meses_pt.items()}.get(mes.lower()), meses_pt
    return int(mes), meses_pt

def usuarios_loja(df, mes, ano, modo="valores"):
    df = df.copy()
    df["data_captura"] = pd.to_datetime(df["data_captura"], errors="coerce")
    df = df.dropna(subset=["data_captura"])

    mes_num, meses_pt = _mes_numero(mes)
    if mes_num not in range(1,13): 
        return px.bar(title=f"Mês inválido: {mes}")
    df = df[(df["data_captura"].dt.year == ano) & (df["data_captura"].dt.month == mes_num)]

    if df.empty:
        return px.bar(title=f"Lojas por Número de Capturas – {meses_pt[mes_num]} {ano} (sem dados)")

    s = (df.groupby("nome_loja")["numero_celular"]
           .nunique().sort_values(ascending=False)
           .reset_index(name="valor"))

    total = s["valor"].sum()
    s["pct"] = (s["valor"] / total).fillna(0.0) if total > 0 else 0.0

    titulo = f"Lojas por Número de Capturas – {meses_pt[mes_num]} {ano}"

    if modo.lower() == "percentual":
        fig = px.bar(
            s, y="nome_loja", x="pct", orientation="h",
            text=s["pct"].map(lambda x: f"{x:.1%}"),
            color="pct", color_continuous_scale="Blues",
            title=titulo + " (Percentual)",
            labels={"nome_loja":"Lojas","pct":"% do total"}
        )
        fig.update_layout(height=500, xaxis_tickformat=".0%")
        return fig

    text_series = s["valor"].astype(int).astype(str) if modo.lower() == "valores" \
                  else s.apply(lambda r: f'{int(r["valor"])}  ({r["pct"]:.1%})', axis=1)

    fig = px.bar(
        s, y="nome_loja", x="valor", orientation="h",
        text=text_series, color="valor", color_continuous_scale="Blues",
        title=titulo, labels={"nome_loja":"Lojas","valor":"Capturas"}
    )
    fig.update_layout(height=500)
    return fig

def capturas_categoria(df, mes, ano, modo="valores"):
    df = df.copy()
    df["data_captura"] = pd.to_datetime(df["data_captura"], errors="coerce")
    df = df.dropna(subset=["data_captura"])

    mes_num, meses_pt = _mes_numero(mes)
    if mes_num not in range(1,13): 
        return px.bar(title=f"Mês inválido: {mes}")
    df = df[(df["data_captura"].dt.year == ano) & (df["data_captura"].dt.month == mes_num)]

    if df.empty:
        return px.bar(title=f"Categorias por Número de Capturas – {meses_pt[mes_num]} {ano} (sem dados)")

    s = (df.groupby("tipo_loja")["numero_celular"]
           .nunique().sort_values(ascending=False)
           .reset_index(name="valor"))

    total = s["valor"].sum()
    s["pct"] = (s["valor"] / total).fillna(0.0) if total > 0 else 0.0

    titulo = f"Categorias por Número de Capturas – {meses_pt[mes_num]} {ano}"

    if modo.lower() == "percentual":
        fig = px.bar(
            s, y="tipo_loja", x="pct", orientation="h",
            text=s["pct"].map(lambda x: f"{x:.1%}"),
            color="pct", color_continuous_scale="Blues",
            title=titulo + " (Percentual)",
            labels={"tipo_loja":"Categorias","pct":"% do total"}
        )
        fig.update_layout(height=500, xaxis_tickformat=".0%")
        return fig

    text_series = s["valor"].astype(int).astype(str) if modo.lower() == "valores" \
                  else s.apply(lambda r: f'{int(r["valor"])}  ({r["pct"]:.1%})', axis=1)

    fig = px.bar(
        s, y="tipo_loja", x="valor", orientation="h",
        text=text_series, color="valor", color_continuous_scale="Blues",
        title=titulo, labels={"tipo_loja":"Categorias","valor":"Capturas"}
    )
    fig.update_layout(height=500)
    return fig

def resumo_parceiros(df, mes, ano):
    df = df.copy()
    df["data_captura"] = pd.to_datetime(df["data_captura"], errors="coerce")
    df = df.dropna(subset=["data_captura"])

    mes_num, _ = _mes_numero(mes)
    if mes_num not in range(1,13): 
        return {"total_lojas": 0, "total_categorias": 0}

    df = df[(df["data_captura"].dt.year == ano) & (df["data_captura"].dt.month == mes_num)]

    return {
        "total_lojas": df["nome_loja"].nunique(),
        "total_categorias": df["tipo_loja"].nunique()
    }

def tipo_cupom(df, ano, mes=None, nome_loja=None, tipo_loja=None, modo="valores"):
    df = df.copy()
    df["data_captura"] = pd.to_datetime(df["data_captura"], errors="coerce")
    df = df.dropna(subset=["data_captura"])

    # --- filtro por ano/mês ---
    df = df[df["data_captura"].dt.year == int(ano)]

    mes_num, meses_pt = _mes_numero(mes) if mes else (None, {
        1:"Janeiro",2:"Fevereiro",3:"Março",4:"Abril",5:"Maio",6:"Junho",
        7:"Julho",8:"Agosto",9:"Setembro",10:"Outubro",11:"Novembro",12:"Dezembro"
    })
    sufixo_mes = ""
    if mes_num:
        df = df[df["data_captura"].dt.month == mes_num]
        sufixo_mes = f" – {meses_pt[mes_num]}"

    # --- filtros opcionais por loja/categoria ---
    def _norm(x): return str(x).strip().casefold()
    sufixo_loja = ""
    if nome_loja and _norm(nome_loja) not in {"todas", "all", ""}:
        df = df[df["nome_loja"].astype(str).str.strip().str.casefold() == _norm(nome_loja)]
        sufixo_loja = f" – {nome_loja}"
    elif tipo_loja and _norm(tipo_loja) not in {"todas", "all", ""}:
        df = df[df["tipo_loja"].astype(str).str.strip().str.casefold() == _norm(tipo_loja)]
        sufixo_loja = f" – {tipo_loja}"

    if df.empty:
        return px.bar(title=f"Sem dados para {ano}{sufixo_mes}{sufixo_loja}")

    # --- agregação ---
    s = (
        df.groupby("tipo_cupom")["numero_celular"]
          .nunique()
          .reset_index(name="valor")
          .sort_values("valor", ascending=False)
    )

    total = s["valor"].sum()
    s["pct"] = (s["valor"] / total).fillna(0.0) if total > 0 else 0.0

    titulo = f"Distribuição por Tipo de Cupom – {ano}{sufixo_mes}{sufixo_loja}"

    # =======================
    # MODO PERCENTUAL
    # =======================
    if modo.lower() == "percentual":
        fig = px.pie(
            s,
            names="tipo_cupom",
            values="pct",
            title=titulo + " (Percentual)",
            hole=0.35
        )
        fig.update_traces(
            textposition="inside",
            texttemplate="%{label}<br>%{percent:.1%}",
            hovertemplate="<b>%{label}</b><br>Participação: %{percent:.1%}<extra></extra>"
        )
        fig.update_layout(height=500, legend_title_text="Tipo de Cupom")
        return fig

    # =======================
    # MODO AMBOS OU VALORES
    # =======================
    s["texto"] = (
        s["valor"].astype(int).astype(str)
        if modo.lower() == "valores"
        else s.apply(lambda r: f'{int(r["valor"])} ({r["pct"]:.1%})', axis=1)
    )

    fig = px.pie(
        s,
        names="tipo_cupom",
        values="valor",
        title=titulo,
        hole=0.35
    )
    fig.update_traces(
        textposition="inside",
        texttemplate="%{label}<br>%{customdata}",
        customdata=s["texto"],
        hovertemplate="<b>%{label}</b><br>Capturas: %{value:d}<br>Participação: %{percent:.1%}<extra></extra>"
    )
    fig.update_layout(height=500, legend_title_text="Tipo de Cupom")
    return fig
