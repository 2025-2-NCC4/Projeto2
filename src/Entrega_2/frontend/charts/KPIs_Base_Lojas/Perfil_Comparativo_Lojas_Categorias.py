# charts/KPIs_Base_Lojas/Perfil_Comparativo_Lojas_Categorias.py
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


# -------------------------------------------------
# Util interno: validação de colunas obrigatórias
# -------------------------------------------------
def _checar_colunas(df: pd.DataFrame, obrigatorias: set[str]) -> list[str]:
    return sorted(list(obrigatorias - set(df.columns)))


# =================================================
# Lojas por número de capturas (mês/ano)
# =================================================
def usuarios_loja(
    df: pd.DataFrame,
    mes,
    ano: int,
    modo: str = "valores",
    nomes_lojas=None,
    categorias=None,
    coluna_data: str = "data",
):
    """
    Barras horizontais por loja (número de celulares únicos) no mês/ano.
    Aceita filtros opcionais de lojas/categorias do estabelecimento.
    """
    faltantes = _checar_colunas(df, {"celular", "nome_estabelecimento", coluna_data})
    if faltantes:
        return px.bar(title=f"Colunas obrigatórias ausentes: {', '.join(faltantes)}")

    dff = garantir_coluna_data(df, coluna_data)
    dff = filtrar_lojas_e_categorias(dff, nomes_lojas, categorias)

    m = converter_mes(mes)
    if m is None or m not in range(1, 13):
        return px.bar(title=f"Mês inválido: {mes}{sufixo_titulo(nomes_lojas, categorias)}")

    dff = filtrar_por_ano_e_mes(dff, ano=int(ano), mes=m, coluna_data=coluna_data)
    suf = sufixo_titulo(nomes_lojas, categorias)

    if dff.empty:
        return px.bar(title=f"Lojas por Número de Capturas – {MESES_PT[m]} {ano}{suf} (sem dados)")

    s = (
        dff.groupby("nome_estabelecimento")["celular"]
           .nunique()
           .sort_values(ascending=False)
           .reset_index(name="valor")
    )
    total = s["valor"].sum()
    s["pct"] = (s["valor"] / total).fillna(0.0) if total > 0 else 0.0
    titulo = f"Lojas por Número de Capturas – {MESES_PT[m]} {ano}{suf}"

    if str(modo).lower() == "percentual":
        fig = px.bar(
            s, y="nome_estabelecimento", x="pct", orientation="h",
            text=s["pct"].map(lambda x: f"{x:.1%}"),
            color="pct", color_continuous_scale="Blues",
            title=titulo + " (Percentual)",
            labels={"nome_estabelecimento": "Lojas", "pct": "% do total"},
        )
        fig.update_layout(height=500, xaxis_tickformat=".0%")
        return fig

    # "valores" ou "ambos"
    fig = px.bar(
        s, y="nome_estabelecimento", x="valor", orientation="h",
        text=texto_valores(s, col_valor="valor", col_pct="pct", modo=modo),
        color="valor", color_continuous_scale="Blues",
        title=titulo,
        labels={"nome_estabelecimento": "Lojas", "valor": "Capturas"},
    )
    fig.update_layout(height=500)
    return fig


# =================================================
# Categorias por número de capturas (mês/ano)
# =================================================
def capturas_categoria(
    df: pd.DataFrame,
    mes,
    ano: int,
    modo: str = "valores",
    nomes_lojas=None,
    categorias=None,
    coluna_data: str = "data",
):
    """
    Barras horizontais por categoria (número de celulares únicos) no mês/ano.
    Aceita filtros opcionais de lojas/categorias do estabelecimento.
    """
    faltantes = _checar_colunas(df, {"celular", "categoria_estabelecimento", coluna_data})
    if faltantes:
        return px.bar(title=f"Colunas obrigatórias ausentes: {', '.join(faltantes)}")

    dff = garantir_coluna_data(df, coluna_data)
    dff = filtrar_lojas_e_categorias(dff, nomes_lojas, categorias)

    m = converter_mes(mes)
    if m is None or m not in range(1, 13):
        return px.bar(title=f"Mês inválido: {mes}{sufixo_titulo(nomes_lojas, categorias)}")

    dff = filtrar_por_ano_e_mes(dff, ano=int(ano), mes=m, coluna_data=coluna_data)
    suf = sufixo_titulo(nomes_lojas, categorias)

    if dff.empty:
        return px.bar(title=f"Categorias por Número de Capturas – {MESES_PT[m]} {ano}{suf} (sem dados)")

    s = (
        dff.groupby("categoria_estabelecimento")["celular"]
           .nunique()
           .sort_values(ascending=False)
           .reset_index(name="valor")
    )
    total = s["valor"].sum()
    s["pct"] = (s["valor"] / total).fillna(0.0) if total > 0 else 0.0
    titulo = f"Categorias por Número de Capturas – {MESES_PT[m]} {ano}{suf}"

    if str(modo).lower() == "percentual":
        fig = px.bar(
            s, y="categoria_estabelecimento", x="pct", orientation="h",
            text=s["pct"].map(lambda x: f"{x:.1%}"),
            color="pct", 
            # color_continuous_scale="Blues",
            title=titulo + " (Percentual)",
            labels={"categoria_estabelecimento": "Categorias", "pct": "% do total"},
        )
        fig.update_layout(height=500, xaxis_tickformat=".0%")
        return fig

    # "valores" ou "ambos"
    fig = px.bar(
        s, y="categoria_estabelecimento", x="valor", orientation="h",
        text=texto_valores(s, col_valor="valor", col_pct="pct", modo=modo),
        color="valor", 
        # color_contínuo_scale="Blues",  # <- OBS: se seu Plotly estiver PT, mantenha "color_continuous_scale"
        title=titulo,
        labels={"categoria_estabelecimento": "Categorias", "valor": "Capturas"},
    )
    # Corrige possível typo no parâmetro acima em ambientes EN: use "color_continuous_scale"
    fig.update_layout(height=500)
    return fig


# =================================================
# número de estabelecimentos por Categoria
# =================================================
def estabelecimentos_por_categoria(
    df: pd.DataFrame,
    mes,
    ano: int,
    modo: str = "valores",
    nomes_lojas=None,
    categorias=None,
    coluna_data: str = "data",
):
    obrigatorias = {"nome_estabelecimento", "categoria_estabelecimento", coluna_data}
    faltantes = obrigatorias - set(df.columns)
    if faltantes:
        return px.bar(title=f"Colunas obrigatórias ausentes: {', '.join(sorted(faltantes))}")

    dff = garantir_coluna_data(df, coluna_data)
    dff = filtrar_lojas_e_categorias(dff, nomes_lojas, categorias)

    m = converter_mes(mes)
    if m is None or m not in range(1, 13):
        return px.bar(title=f"Mês inválido: {mes}{sufixo_titulo(nomes_lojas, categorias)}")

    dff = filtrar_por_ano_e_mes(dff, ano=int(ano), mes=m, coluna_data=coluna_data)
    suf = sufixo_titulo(nomes_lojas, categorias)

    if dff.empty:
        return px.bar(title=f"Estabelecimentos por Categoria – {MESES_PT[m]} {ano}{suf} (sem dados)")

    # conta estabelecimentos distintos por categoria
    g = (
        dff.groupby("categoria_estabelecimento")["nome_estabelecimento"]
           .nunique()
           .reset_index(name="valor")
           .sort_values("valor", ascending=False)
    )
    total = g["valor"].sum()
    g["pct"] = (g["valor"] / total).fillna(0.0) if total > 0 else 0.0

    titulo = f"Estabelecimentos por Categoria – {MESES_PT[m]} {ano}{suf}"
    y = "pct" if str(modo).lower() == "percentual" else "valor"

    fig = px.bar(
        g, y="categoria_estabelecimento", x=y, orientation="h",
        text=(g["pct"].map(lambda x: f"{x:.1%}") if y == "pct" else g["valor"].astype(int).astype(str)),
        color=y, color_continuous_scale="Blues",
        title=(titulo + " (Percentual)" if y == "pct" else titulo),
        labels={
            "categoria_estabelecimento": "Categoria",
            y: ("% do total" if y == "pct" else "Estabelecimentos distintos"),
        },
    )
    if y == "pct":
        fig.update_layout(xaxis_tickformat=".0%")
    fig.update_layout(height=520)
    return fig

def lista_estabelecimentos_por_categoria(
    df: pd.DataFrame,
    mes=None,
    ano=None,
    nomes_lojas=None,
    categorias=None,
    coluna_data: str = "data",
) -> dict:
    obrigatorias = {"nome_estabelecimento", "categoria_estabelecimento"}
    faltantes = obrigatorias - set(df.columns)
    if faltantes:
        return {f"Colunas ausentes: {', '.join(sorted(faltantes))}": []}

    dff = garantir_coluna_data(df, coluna_data)
    dff = filtrar_lojas_e_categorias(dff, nomes_lojas, categorias)

    if ano:
        m = converter_mes(mes)
        dff = filtrar_por_ano_e_mes(dff, ano=int(ano), mes=m, coluna_data=coluna_data)

    if dff.empty:
        return {"Sem dados disponíveis": []}

    grupos = (
        dff.groupby("categoria_estabelecimento")["nome_estabelecimento"]
           .unique()
           .apply(lambda arr: sorted(arr))
           .to_dict()
    )
    return grupos


# =================================================
# Resumo de parceiros (totais distintos no mês/ano)
# =================================================
def resumo_parceiros(
    df: pd.DataFrame,
    mes,
    ano: int,
    nomes_lojas=None,
    categorias=None,
    coluna_data: str = "data",
) -> tuple[int, int]:
    """
    Retorna (total_lojas_distintas, total_categorias_distintas) no mês/ano,
    aplicando filtros opcionais de lojas/categorias.
    """
    faltantes = _checar_colunas(df, {"nome_estabelecimento", "categoria_estabelecimento", coluna_data})
    if faltantes:
        return 0, 0

    dff = garantir_coluna_data(df, coluna_data)
    dff = filtrar_lojas_e_categorias(dff, nomes_lojas, categorias)

    m = converter_mes(mes)
    if m is None or m not in range(1, 13):
        return 0, 0

    dff = filtrar_por_ano_e_mes(dff, ano=int(ano), mes=m, coluna_data=coluna_data)
    if dff.empty:
        return 0, 0

    total_lojas = int(dff["nome_estabelecimento"].nunique())
    total_categorias = int(dff["categoria_estabelecimento"].nunique())
    return total_lojas, total_categorias

