# charts/KPIs_Base_Lojas/Perfil_Frequencia_Capturas.py
from __future__ import annotations

import pandas as pd
import plotly.express as px

from utils.filtros import (
    MESES_PT, DIAS_PT,
    garantir_coluna_data,
    converter_mes,
    filtrar_lojas_e_categorias,
    filtrar_por_ano_e_mes,
    sufixo_titulo,
    texto_valores,
)

# =====================================================
# FREQUÊNCIA DIÁRIA
# =====================================================
def frequencia_diaria_filtrada(
    df,
    mes,
    ano,
    nomes_lojas=None,
    categorias=None,
    modo="valores",
    coluna_data="data",
):
    dff = garantir_coluna_data(df, coluna_data)
    dff = filtrar_lojas_e_categorias(dff, nomes_lojas, categorias)
    m = converter_mes(mes)
    suf = sufixo_titulo(nomes_lojas, categorias)

    if m is None:
        return px.bar(title=f"Mês inválido: {mes}{suf}")

    dff = filtrar_por_ano_e_mes(dff, ano, m, coluna_data)
    if dff.empty:
        return px.bar(title=f"Sem dados para {MESES_PT[m]} {ano}{suf}")

    g = (
        dff.groupby(dff[coluna_data].dt.date)["celular"]
           .nunique()
           .reset_index(name="valor")
           .sort_values(coluna_data)
    )
    g["dia"] = pd.to_datetime(g[coluna_data]).dt.day
    total = g["valor"].sum()
    g["pct"] = (g["valor"] / total).fillna(0.0) if total > 0 else 0.0

    y = "pct" if str(modo).lower() == "percentual" else "valor"
    fig = px.bar(
        g, x="dia", y=y,
        text=texto_valores(g, col_valor="valor", col_pct="pct", modo=modo),
        color=y, color_continuous_scale="Blues",
        title=f"Frequência Diária de Capturas – {MESES_PT[m]} {ano}{suf}",
        labels={"dia": "Dia", y: ("% do total" if y == "pct" else "Capturas")},
    )
    if y == "pct":
        fig.update_layout(yaxis_tickformat=".0%")
    fig.update_layout(height=500, xaxis=dict(tickmode="linear", tick0=1, dtick=1))
    return fig


# =====================================================
# FREQUÊNCIA SEMANAL
# =====================================================
def frequencia_semanal_filtrada(
    df,
    ano,
    nomes_lojas=None,
    categorias=None,
    modo="valores",
    coluna_data="data",
):
    dff = garantir_coluna_data(df, coluna_data)
    dff = filtrar_lojas_e_categorias(dff, nomes_lojas, categorias)
    dff = filtrar_por_ano_e_mes(dff, ano, None, coluna_data)
    suf = sufixo_titulo(nomes_lojas, categorias)

    if dff.empty:
        return px.bar(title=f"Sem dados para {ano}{suf}")

    dff["semana"] = dff[coluna_data].dt.isocalendar().week.astype(int)
    g = (
        dff.groupby("semana")["celular"]
           .nunique()
           .reset_index(name="valor")
           .sort_values("semana")
    )
    total = g["valor"].sum()
    g["pct"] = (g["valor"] / total).fillna(0.0) if total > 0 else 0.0
    g["semana_label"] = g["semana"].apply(lambda x: f"Semana {x}")

    y = "pct" if str(modo).lower() == "percentual" else "valor"
    fig = px.bar(
        g, x="semana_label", y=y,
        text=texto_valores(g, col_valor="valor", col_pct="pct", modo=modo),
        color=y, color_continuous_scale="Blues",
        title=f"Frequência Semanal de Capturas – {ano}{suf}",
        labels={"semana_label": "Semana", y: ("% do total" if y == "pct" else "Capturas")},
    )
    if y == "pct":
        fig.update_layout(yaxis_tickformat=".0%")
    fig.update_layout(height=480, xaxis=dict(tickangle=-45))
    return fig


# =====================================================
# FREQUÊNCIA POR DIA DA SEMANA (ANO)
# =====================================================
def frequencia_dia_semana_ano_filtrada(
    df,
    ano,
    nomes_lojas=None,
    categorias=None,
    modo="valores",
    coluna_data="data",
):
    dff = garantir_coluna_data(df, coluna_data)
    dff = filtrar_lojas_e_categorias(dff, nomes_lojas, categorias)
    dff = filtrar_por_ano_e_mes(dff, ano, None, coluna_data)
    suf = sufixo_titulo(nomes_lojas, categorias)

    if dff.empty:
        return px.bar(title=f"Sem dados disponíveis para {ano}{suf}")

    dff["dow"] = dff[coluna_data].dt.dayofweek
    g = (
        dff.groupby("dow")["celular"]
           .nunique()
           .reset_index(name="valor")
           .sort_values("dow")
    )
    total = g["valor"].sum()
    g["pct"] = (g["valor"] / total).fillna(0.0) if total > 0 else 0.0
    g["dia_label"] = g["dow"].map(DIAS_PT)

    y = "pct" if str(modo).lower() == "percentual" else "valor"
    fig = px.bar(
        g, x="dia_label", y=y,
        text=texto_valores(g, col_valor="valor", col_pct="pct", modo=modo),
        color=y, color_continuous_scale="Blues",
        title=f"Frequência de Capturas por Dia da Semana – {ano}{suf}",
        labels={"dia_label": "Dia da Semana", y: ("% do total" if y == "pct" else "Capturas")},
    )
    if y == "pct":
        fig.update_layout(yaxis_tickformat=".0%")
    fig.update_layout(height=480)
    return fig


# =====================================================
# FREQUÊNCIA POR DIA DA SEMANA (MÊS/ANO)
# =====================================================
def frequencia_dia_semana_mes_filtrada(
    df,
    ano,
    mes=None,
    nomes_lojas=None,
    categorias=None,
    modo="valores",
    coluna_data="data",
):
    dff = garantir_coluna_data(df, coluna_data)
    dff = filtrar_lojas_e_categorias(dff, nomes_lojas, categorias)
    m = converter_mes(mes)
    suf = sufixo_titulo(nomes_lojas, categorias)

    if m is None:
        return px.bar(title=f"Mês inválido: {mes}{suf}")

    dff = filtrar_por_ano_e_mes(dff, ano, m, coluna_data)
    if dff.empty:
        return px.bar(title=f"Sem dados para {MESES_PT[m]} {ano}{suf}")

    dff["dow"] = dff[coluna_data].dt.dayofweek
    g = (
        dff.groupby("dow")["celular"]
           .nunique()
           .reset_index(name="valor")
           .sort_values("dow")
    )
    total = g["valor"].sum()
    g["pct"] = (g["valor"] / total).fillna(0.0) if total > 0 else 0.0
    g["dia_label"] = g["dow"].map(DIAS_PT)

    y = "pct" if str(modo).lower() == "percentual" else "valor"
    fig = px.bar(
        g, x="dia_label", y=y,
        text=texto_valores(g, col_valor="valor", col_pct="pct", modo=modo),
        color=y, color_continuous_scale="Blues",
        title=f"Frequência de Capturas por Dia da Semana – {MESES_PT[m]} {ano}{suf}",
        labels={"dia_label": "Dia da Semana", y: ("% do total" if y == "pct" else "Capturas")},
    )
    if y == "pct":
        fig.update_layout(yaxis_tickformat=".0%")
    fig.update_layout(height=480)
    return fig


# =====================================================
# FREQUÊNCIA MENSAL
# =====================================================
def frequencia_mensal_filtrada(
    df,
    ano,
    nomes_lojas=None,
    categorias=None,
    modo="valores",
    coluna_data="data",
):
    dff = garantir_coluna_data(df, coluna_data)
    dff = filtrar_lojas_e_categorias(dff, nomes_lojas, categorias)
    dff = filtrar_por_ano_e_mes(dff, ano, None, coluna_data)
    suf = sufixo_titulo(nomes_lojas, categorias)

    if dff.empty:
        return px.bar(title=f"Sem dados disponíveis para {ano}{suf}")

    g = (
        dff.groupby(dff[coluna_data].dt.month)["celular"]
           .nunique()
           .reset_index(name="valor")
           .sort_values(coluna_data)
    )
    g["mes_label"] = g[coluna_data].map(MESES_PT)
    total = g["valor"].sum()
    g["pct"] = (g["valor"] / total).fillna(0.0) if total > 0 else 0.0

    y = "pct" if str(modo).lower() == "percentual" else "valor"
    fig = px.bar(
        g, x="mes_label", y=y,
        text=texto_valores(g, col_valor="valor", col_pct="pct", modo=modo),
        color=y, color_continuous_scale="Blues",
        title=f"Frequência Mensal de Capturas – {ano}{suf}",
        labels={"mes_label": "Mês", y: ("% do total" if y == "pct" else "Capturas")},
    )
    if y == "pct":
        fig.update_layout(yaxis_tickformat=".0%")
    fig.update_layout(height=480, xaxis=dict(tickangle=-45))
    return fig

# =====================================================
# FREQUÊNCIA anual
# =====================================================
def frequencia_ano_filtrada(
    df,
    nomes_lojas=None,
    categorias=None,
    modo: str = "valores",
    coluna_data: str = "data",
):
    """
    Barras por ano de capturas (players únicos), com filtros centralizados.
    """
    dff = garantir_coluna_data(df, coluna_data)
    dff = filtrar_lojas_e_categorias(dff, nomes_lojas, categorias)
    suf = sufixo_titulo(nomes_lojas, categorias)

    if dff.empty:
        return px.bar(title=f"Sem dados disponíveis{suf}")

    dff["ano"] = dff[coluna_data].dt.year
    g = (
        dff.groupby("ano")["celular"]
           .nunique()
           .reset_index(name="valor")
           .sort_values("ano")
    )
    total = g["valor"].sum()
    g["pct"] = (g["valor"] / total).fillna(0.0) if total > 0 else 0.0

    y = "pct" if str(modo).lower() == "percentual" else "valor"
    fig = px.bar(
        g, x="ano", y=y,
        text=texto_valores(g, col_valor="valor", col_pct="pct", modo=modo),
        color=y, color_continuous_scale="Blues",
        title=f"Frequência Anual de Capturas{suf}",
        labels={"ano": "Anos", y: ("% do total" if y == "pct" else "Capturas")},
    )
    if y == "pct":
        fig.update_layout(yaxis_tickformat=".0%")
    fig.update_layout(height=480, xaxis=dict(showgrid=False))
    return fig


# =====================================================
# MÉDIAS DE FREQUÊNCIA
# =====================================================
def medias_frequencia_filtrada(
    df,
    mes,
    ano,
    nomes_lojas=None,
    categorias=None,
    coluna_data="data",
):
    """
    Calcula médias diária, semanal, mensal e anual de capturas (players únicos).
    """
    dff = garantir_coluna_data(df, coluna_data)
    dff = filtrar_lojas_e_categorias(dff, nomes_lojas, categorias)
    m = converter_mes(mes)

    if m is None:
        return {"media_diaria_mes_ano": 0.0, "media_semanal_ano": 0.0, "media_mensal_ano": 0.0, "media_anual": 0.0}

    # --- média diária no mês/ano
    dff_ma = filtrar_por_ano_e_mes(dff, ano, m, coluna_data)
    if dff_ma.empty:
        media_diaria = 0.0
    else:
        dias = pd.date_range(
            pd.Timestamp(year=int(ano), month=m, day=1),
            pd.Timestamp(year=int(ano), month=m, day=1) + pd.offsets.MonthEnd(0),
            freq="D",
        )
        g = (
            dff_ma.groupby(dff_ma[coluna_data].dt.date)["celular"]
                  .nunique()
                  .reindex(dias.date, fill_value=0)
        )
        media_diaria = float(g.mean())

    # --- média semanal (ano)
    dff_ano = filtrar_por_ano_e_mes(dff, ano, None, coluna_data)
    if dff_ano.empty:
        media_semanal = media_mensal = media_anual = 0.0
    else:
        s_sem = (
            dff_ano.set_index(coluna_data)
                   .groupby(pd.Grouper(freq="W-SUN"))["celular"]
                   .nunique()
        )
        media_semanal = float(s_sem.mean())

        s_mes = (
            dff_ano.groupby(dff_ano[coluna_data].dt.month)["celular"]
                   .nunique()
                   .reindex(range(1, 13), fill_value=0)
        )
        media_mensal = float(s_mes.mean())

        s_ano = (
            dff.groupby(dff[coluna_data].dt.year)["celular"]
               .nunique()
               .sort_index()
        )
        media_anual = float(s_ano.mean())

    return {
        "media_diaria_mes_ano": media_diaria,
        "media_semanal_ano": media_semanal,
        "media_mensal_ano": media_mensal,
        "media_anual": media_anual,
    }
