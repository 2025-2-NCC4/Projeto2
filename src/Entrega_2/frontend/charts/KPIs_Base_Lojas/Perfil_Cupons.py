# charts/KPIs_Base_Lojas/Perfil_Cupons.py
from __future__ import annotations
import pandas as pd
import plotly.express as px

from utils.filtros import (
    MESES_PT,
    garantir_coluna_data,
    converter_mes,
    filtrar_por_ano_e_mes,
    filtrar_lojas_e_categorias,
    sufixo_titulo,
    texto_valores,
)

# =================================================
# Tipo de Cupom (gráfico de pizza)
# =================================================
def tipo_cupom(
    df: pd.DataFrame,
    ano: int,
    mes=None,
    nomes_lojas=None,
    categorias=None,
    modo: str = "valores",
    coluna_data: str = "data",
):
    """
    Exibe a distribuição de capturas por tipo de cupom.
    Aceita filtros de mês, loja e categoria.
    """
    obrigatorias = {"celular", "tipo_cupom", coluna_data}
    if not obrigatorias.issubset(df.columns):
        faltantes = ", ".join(sorted(obrigatorias - set(df.columns)))
        return px.bar(title=f"Colunas obrigatórias ausentes: {faltantes}")

    dff = garantir_coluna_data(df, coluna_data)
    m = converter_mes(mes)
    dff = filtrar_por_ano_e_mes(dff, ano=int(ano), mes=m, coluna_data=coluna_data)
    dff = filtrar_lojas_e_categorias(dff, nomes_lojas, categorias)
    suf = sufixo_titulo(nomes_lojas, categorias)

    subt = f"{MESES_PT[m]} {ano}" if m else f"{ano}"
    if dff.empty:
        return px.bar(title=f"Distribuição por Tipo de Cupom – {subt}{suf} (sem dados)")

    s = (
        dff.groupby("tipo_cupom")["celular"]
           .nunique()
           .reset_index(name="valor")
           .sort_values("valor", ascending=False)
    )
    total = s["valor"].sum()
    s["pct"] = (s["valor"] / total).fillna(0.0) if total > 0 else 0.0
    titulo = f"Distribuição por Tipo de Cupom – {subt}{suf}"

    if str(modo).lower() == "percentual":
        fig = px.pie(
            s, names="tipo_cupom", values="pct",
            title=titulo + " (Percentual)", hole=0.35
        )
        fig.update_traces(
            textposition="inside",
            texttemplate="%{label}<br>%{percent:.1%}",
            hovertemplate="<b>%{label}</b><br>Participação: %{percent:.1%}<extra></extra>",
        )
        fig.update_layout(height=500, legend_title_text="Tipo de Cupom")
        return fig

    s["texto"] = texto_valores(s, col_valor="valor", col_pct="pct", modo=modo)
    fig = px.pie(
        s, names="tipo_cupom", values="valor",
        title=titulo, hole=0.35
    )
    fig.update_traces(
        textposition="inside",
        texttemplate="%{label}<br>%{customdata}",
        customdata=s["texto"],
        hovertemplate="<b>%{label}</b><br>Capturas: %{value:d}<br>Participação: %{percent:.1%}<extra></extra>",
    )
    fig.update_layout(height=500, legend_title_text="Tipo de Cupom")
    return fig


# =================================================
# Tipo de Cupom por Loja (gráfico de barras)
# =================================================
def cupons_por_loja(
    df: pd.DataFrame,
    mes,
    ano: int,
    modo: str = "valores",
    nomes_lojas=None,
    categorias=None,
    coluna_data: str = "data",
):
    """
    Exibe barras agrupadas por loja, segmentadas por tipo de cupom.
    """
    obrigatorias = {"celular", "tipo_cupom", "nome_estabelecimento", coluna_data}
    if not obrigatorias.issubset(df.columns):
        faltantes = ", ".join(sorted(obrigatorias - set(df.columns)))
        return px.bar(title=f"Colunas obrigatórias ausentes: {faltantes}")

    dff = garantir_coluna_data(df, coluna_data)
    m = converter_mes(mes)
    dff = filtrar_por_ano_e_mes(dff, ano=int(ano), mes=m, coluna_data=coluna_data)
    dff = filtrar_lojas_e_categorias(dff, nomes_lojas, categorias)
    suf = sufixo_titulo(nomes_lojas, categorias)

    if m is None:
        return px.bar(title=f"Mês inválido: {mes}{suf}")
    if dff.empty:
        return px.bar(title=f"Tipo de Cupom por Loja — {MESES_PT[m]} {ano}{suf} (sem dados)")

    g = (
        dff.groupby(["nome_estabelecimento", "tipo_cupom"])["celular"]
           .nunique()
           .reset_index(name="valor")
    )
    tot_loja = g.groupby("nome_estabelecimento")["valor"].transform("sum")
    g["pct"] = (g["valor"] / tot_loja).fillna(0.0)
    titulo = f"Tipo de Cupom por Loja — {MESES_PT[m]} {ano}{suf}"

    if str(modo).lower() == "percentual":
        fig = px.bar(
            g, x="nome_estabelecimento", y="pct", color="tipo_cupom",
            barmode="group", text=g["pct"].map(lambda x: f"{x:.1%}"),
            labels={"nome_estabelecimento": "Loja", "pct": "% na loja", "tipo_cupom": "Tipo de Cupom"},
            title=titulo + " (Percentual)",
        )
        fig.update_layout(xaxis_tickangle=-30, height=520, yaxis_tickformat=".0%")
        return fig

    g["texto"] = g.apply(
        lambda r: f"{int(r['valor'])} ({r['pct']:.1%})" if modo.lower() == "ambos" else f"{int(r['valor'])}",
        axis=1,
    )
    fig = px.bar(
        g, x="nome_estabelecimento", y="valor", color="tipo_cupom",
        barmode="group", text="texto",
        labels={"nome_estabelecimento": "Loja", "valor": "Capturas (players únicos)", "tipo_cupom": "Tipo de Cupom"},
        title=titulo,
    )
    fig.update_layout(xaxis_tickangle=-30, height=520)
    return fig


# =================================================
# Tipo de Cupom por Categoria (gráfico de barras)
# =================================================
def cupons_por_categoria(
    df: pd.DataFrame,
    mes,
    ano: int,
    modo: str = "valores",
    nomes_lojas=None,
    categorias=None,
    coluna_data: str = "data",
):
    """
    Exibe barras agrupadas por categoria, segmentadas por tipo de cupom.
    """
    obrigatorias = {"celular", "tipo_cupom", "categoria_estabelecimento", coluna_data}
    if not obrigatorias.issubset(df.columns):
        faltantes = ", ".join(sorted(obrigatorias - set(df.columns)))
        return px.bar(title=f"Colunas obrigatórias ausentes: {faltantes}")

    dff = garantir_coluna_data(df, coluna_data)
    m = converter_mes(mes)
    dff = filtrar_por_ano_e_mes(dff, ano=int(ano), mes=m, coluna_data=coluna_data)
    dff = filtrar_lojas_e_categorias(dff, nomes_lojas, categorias)
    suf = sufixo_titulo(nomes_lojas, categorias)

    if m is None:
        return px.bar(title=f"Mês inválido: {mes}{suf}")
    if dff.empty:
        return px.bar(title=f"Tipo de Cupom por Categoria — {MESES_PT[m]} {ano}{suf} (sem dados)")

    g = (
        dff.groupby(["categoria_estabelecimento", "tipo_cupom"])["celular"]
           .nunique()
           .reset_index(name="valor")
    )
    tot_cat = g.groupby("categoria_estabelecimento")["valor"].transform("sum")
    g["pct"] = (g["valor"] / tot_cat).fillna(0.0)
    titulo = f"Tipo de Cupom por Categoria — {MESES_PT[m]} {ano}{suf}"

    if str(modo).lower() == "percentual":
        fig = px.bar(
            g, x="categoria_estabelecimento", y="pct", color="tipo_cupom",
            barmode="group", text=g["pct"].map(lambda x: f"{x:.1%}"),
            labels={"categoria_estabelecimento": "Categoria", "pct": "% na categoria", "tipo_cupom": "Tipo de Cupom"},
            title=titulo + " (Percentual)",
        )
        fig.update_layout(xaxis_tickangle=-30, height=520, yaxis_tickformat=".0%")
        return fig

    g["texto"] = g.apply(
        lambda r: f"{int(r['valor'])} ({r['pct']:.1%})" if modo.lower() == "ambos" else f"{int(r['valor'])}",
        axis=1,
    )
    fig = px.bar(
        g, x="categoria_estabelecimento", y="valor", color="tipo_cupom",
        barmode="group", text="texto",
        labels={"categoria_estabelecimento": "Categoria", "valor": "Capturas (players únicos)", "tipo_cupom": "Tipo de Cupom"},
        title=titulo,
    )
    fig.update_layout(xaxis_tickangle=-30, height=520)
    return fig
