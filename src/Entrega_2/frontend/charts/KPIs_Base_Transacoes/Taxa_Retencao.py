from __future__ import annotations
from datetime import date, timedelta
from calendar import monthrange

import pandas as pd
# Mantido caso você use gráficos em outras partes deste módulo futuramente
import plotly.express as px  # noqa: F401

from utils.filtros import (
    MESES_PT,                          # noqa: F401
    garantir_coluna_data,
    converter_mes,                     # noqa: F401
    filtrar_lojas_e_categorias,
    filtrar_por_ano_e_mes,             # noqa: F401
    sufixo_titulo,                     # noqa: F401
)

# -----------------------------------------------------
# Compat de nomes legados -> nomes padronizados
# -----------------------------------------------------
def _resolver_filtros(nomes_lojas, categorias, **kwargs):
    if nomes_lojas is None:
        nomes_lojas = kwargs.pop("nome_estabelecimento", None)
    if categorias is None:
        categorias = kwargs.pop("categoria_estabelecimento", None)
    return nomes_lojas, categorias

# -----------------------------------------------------
# Helpers de período
# -----------------------------------------------------
def _next_month_year(ano: int, mes: int) -> tuple[int, int]:
    """Retorna (ano, mes) do mês seguinte."""
    if mes == 12:
        return ano + 1, 1
    return ano, mes + 1

def _next_iso_year_week(ano_iso: int, semana: int) -> tuple[int, int] | tuple[None, None]:
    """Dado (ano_iso, semana), retorna (ano_iso2, semana2) da próxima semana ISO."""
    try:
        monday = date.fromisocalendar(int(ano_iso), int(semana), 1)
    except ValueError:
        return None, None
    nxt = monday + timedelta(days=7)
    iso = nxt.isocalendar()
    return int(iso[0]), int(iso[1])

# =====================================================
# TAXA DE RETENÇÃO MENSAL — média no período (M -> M+1)
# =====================================================
def taxa_retencao_mensal(
    df: pd.DataFrame,
    ano: int,
    mes,
    nomes_lojas=None,
    categorias=None,
    coluna_data: str = "data",
    **kwargs,
) -> dict:
    """
    Calcula a MÉDIA de retenção mensal ao longo do período contido no DF (já filtrado fora),
    iterando sobre todos os pares mês->mês seguinte presentes.

    Retorna:
      {
        "coorte": soma_das_coortes_validas,
        "retidos": soma_dos_retidos,
        "taxa": media_simples_das_taxas,
        "mes_base": primeiro_mes_base, "mes_follow": primeiro_mes_follow,
        "ano_base": primeiro_ano_base, "ano_follow": primeiro_ano_follow,
        "periodos": qtd_pares_considerados,
        "detalhes": [ {ano, mes, ano2, mes2, coorte, retidos, taxa}, ... ]
      }
    """
    dff = garantir_coluna_data(df, coluna_data)
    nomes_lojas, categorias = _resolver_filtros(nomes_lojas, categorias, **kwargs)
    dff = filtrar_lojas_e_categorias(dff, nomes_lojas, categorias)
    if dff.empty:
        return {"coorte": 0, "retidos": 0, "taxa": 0.0, "periodos": 0}

    dff["_ano"] = dff[coluna_data].dt.year.astype(int)
    dff["_mes"] = dff[coluna_data].dt.month.astype(int)
    pares = sorted(dff[["_ano", "_mes"]].drop_duplicates().itertuples(index=False, name=None))

    detalhes, soma_coorte, soma_retidos, taxas = [], 0, 0, []
    for i in range(len(pares) - 1):
        ano1, mes1 = pares[i]
        ano2, mes2 = pares[i + 1]
        a_next, m_next = _next_month_year(ano1, mes1)
        if (ano2, mes2) != (a_next, m_next):
            continue

        base = dff[(dff["_ano"] == ano1) & (dff["_mes"] == mes1)]
        follow = dff[(dff["_ano"] == ano2) & (dff["_mes"] == mes2)]

        set_base = set(base["celular"].dropna().astype(str).unique())
        n_coorte = len(set_base)
        if n_coorte == 0:
            continue

        set_follow = set(follow["celular"].dropna().astype(str).unique())
        retidos = len(set_base.intersection(set_follow))
        taxa = retidos / n_coorte

        detalhes.append({
            "ano": int(ano1), "mes": int(mes1),
            "ano2": int(ano2), "mes2": int(mes2),
            "coorte": n_coorte, "retidos": retidos, "taxa": float(taxa),
        })
        soma_coorte += n_coorte
        soma_retidos += retidos
        taxas.append(taxa)

    if not detalhes:
        return {"coorte": 0, "retidos": 0, "taxa": 0.0, "periodos": 0}

    primeiro = detalhes[0]
    media_taxa = float(sum(taxas) / len(taxas))
    return {
        "coorte": int(soma_coorte),
        "retidos": int(soma_retidos),
        "taxa": media_taxa,
        "mes_base": primeiro["mes"],
        "mes_follow": primeiro["mes2"],
        "ano_base": primeiro["ano"],
        "ano_follow": primeiro["ano2"],
        "periodos": len(detalhes),
        "detalhes": detalhes,
    }

# =====================================================
# TAXA DE RETENÇÃO ANUAL — média no período (Y -> Y+1)
# =====================================================
def taxa_retencao_anual(
    df: pd.DataFrame,
    ano: int,
    nomes_lojas=None,
    categorias=None,
    coluna_data: str = "data",
    **kwargs,
) -> dict:
    """MÉDIA de retenção ANUAL ao longo do período contido no DF (pares ano -> ano+1)."""
    dff = garantir_coluna_data(df, coluna_data)
    nomes_lojas, categorias = _resolver_filtros(nomes_lojas, categorias, **kwargs)
    dff = filtrar_lojas_e_categorias(dff, nomes_lojas, categorias)
    if dff.empty:
        return {"coorte": 0, "retidos": 0, "taxa": 0.0, "periodos": 0}

    dff["_ano"] = dff[coluna_data].dt.year.astype(int)
    anos = sorted(dff["_ano"].drop_duplicates().astype(int).tolist())

    detalhes, soma_coorte, soma_retidos, taxas = [], 0, 0, []
    for i in range(len(anos) - 1):
        y1 = int(anos[i])
        y2 = int(anos[i + 1])
        if y2 != y1 + 1:
            continue

        base = dff[dff["_ano"] == y1]
        follow = dff[dff["_ano"] == y2]

        set_base = set(base["celular"].dropna().astype(str).unique())
        n_coorte = len(set_base)
        if n_coorte == 0:
            continue

        set_follow = set(follow["celular"].dropna().astype(str).unique())
        retidos = len(set_base.intersection(set_follow))
        taxa = retidos / n_coorte

        detalhes.append({
            "ano": y1, "ano2": y2,
            "coorte": n_coorte, "retidos": retidos, "taxa": float(taxa),
        })
        soma_coorte += n_coorte
        soma_retidos += retidos
        taxas.append(taxa)

    if not detalhes:
        return {"coorte": 0, "retidos": 0, "taxa": 0.0, "periodos": 0}

    primeiro = detalhes[0]
    media_taxa = float(sum(taxas) / len(taxas))
    return {
        "coorte": int(soma_coorte),
        "retidos": int(soma_retidos),
        "taxa": media_taxa,
        "ano_base": primeiro["ano"],
        "ano_follow": primeiro["ano2"],
        "periodos": len(detalhes),
        "detalhes": detalhes,
    }

# ===========================================================
# TAXA DE RETENÇÃO SEMANAL — média (semana ISO -> semana+1)
# ===========================================================
def taxa_retencao_semanal(
    df: pd.DataFrame,
    ano_iso: int,
    semana: int,
    nomes_lojas=None,
    categorias=None,
    coluna_data: str = "data",
    **kwargs,
) -> dict:
    """MÉDIA de retenção SEMANAL (ISO) ao longo do período contido no DF."""
    dff = garantir_coluna_data(df, coluna_data)
    nomes_lojas, categorias = _resolver_filtros(nomes_lojas, categorias, **kwargs)
    dff = filtrar_lojas_e_categorias(dff, nomes_lojas, categorias)
    if dff.empty:
        return {"coorte": 0, "retidos": 0, "taxa": 0.0, "periodos": 0}

    iso = dff[coluna_data].dt.isocalendar()
    dff["_iso_year"] = iso.year.astype(int)
    dff["_iso_week"] = iso.week.astype(int)
    pares = sorted(dff[["_iso_year", "_iso_week"]].drop_duplicates().itertuples(index=False, name=None))

    detalhes, soma_coorte, soma_retidos, taxas = [], 0, 0, []
    for i in range(len(pares) - 1):
        y1, w1 = pares[i]
        y2, w2 = pares[i + 1]
        ny, nw = _next_iso_year_week(y1, w1)
        if ny is None or (ny, nw) != (y2, w2):
            continue

        base = dff[(dff["_iso_year"] == y1) & (dff["_iso_week"] == w1)]
        follow = dff[(dff["_iso_year"] == y2) & (dff["_iso_week"] == w2)]

        set_base = set(base["celular"].dropna().astype(str).unique())
        n_coorte = len(set_base)
        if n_coorte == 0:
            continue

        set_follow = set(follow["celular"].dropna().astype(str).unique())
        retidos = len(set_base.intersection(set_follow))
        taxa = retidos / n_coorte

        detalhes.append({
            "ano_iso": int(y1), "semana": int(w1),
            "ano_iso2": int(y2), "semana2": int(w2),
            "coorte": n_coorte, "retidos": retidos, "taxa": float(taxa),
        })
        soma_coorte += n_coorte
        soma_retidos += retidos
        taxas.append(taxa)

    if not detalhes:
        return {"coorte": 0, "retidos": 0, "taxa": 0.0, "periodos": 0}

    primeiro = detalhes[0]
    media_taxa = float(sum(taxas) / len(taxas))
    return {
        "coorte": int(soma_coorte),
        "retidos": int(soma_retidos),
        "taxa": media_taxa,
        "ano_iso_base": primeiro["ano_iso"],
        "semana_base": primeiro["semana"],
        "ano_iso_follow": primeiro["ano_iso2"],
        "semana_follow": primeiro["semana2"],
        "periodos": len(detalhes),
        "detalhes": detalhes,
    }

# =====================================================
# TAXA DE RETENÇÃO DIÁRIA — média no período (D -> D+1)
# =====================================================
def taxa_retencao_diaria(
    df: pd.DataFrame,
    data_base,                 # mantido por compatibilidade da assinatura
    nomes_lojas=None,
    categorias=None,
    coluna_data: str = "data",
    **kwargs,
) -> dict:
    """
    MÉDIA de retenção DIÁRIA ao longo do período contido no DF,
    iterando sobre todos os pares dia->dia seguinte presentes.

    Observação: o parâmetro 'data_base' é mantido por compatibilidade,
    porém o cálculo percorre todas as datas do DF (filtrado) para obter a média.
    """
    dff = garantir_coluna_data(df, coluna_data)
    nomes_lojas, categorias = _resolver_filtros(nomes_lojas, categorias, **kwargs)
    dff = filtrar_lojas_e_categorias(dff, nomes_lojas, categorias)
    if dff.empty:
        return {"coorte": 0, "retidos": 0, "taxa": 0.0, "periodos": 0}

    dff["_dia"] = dff[coluna_data].dt.normalize()
    dias = sorted(dff["_dia"].drop_duplicates().tolist())
    set_dias = set(dias)

    detalhes, soma_coorte, soma_retidos, taxas = [], 0, 0, []
    for d in dias:
        next_d = d + pd.Timedelta(days=1)
        if next_d not in set_dias:
            continue

        base = dff[dff["_dia"] == d]
        follow = dff[dff["_dia"] == next_d]

        set_base = set(base["celular"].dropna().astype(str).unique())
        n_coorte = len(set_base)
        if n_coorte == 0:
            continue

        set_follow = set(follow["celular"].dropna().astype(str).unique())
        retidos = len(set_base.intersection(set_follow))
        taxa = retidos / n_coorte

        detalhes.append({
            "dia": d.date().isoformat(),
            "dia2": next_d.date().isoformat(),
            "coorte": n_coorte, "retidos": retidos, "taxa": float(taxa),
        })
        soma_coorte += n_coorte
        soma_retidos += retidos
        taxas.append(taxa)

    if not detalhes:
        return {"coorte": 0, "retidos": 0, "taxa": 0.0, "periodos": 0}

    primeiro = detalhes[0]
    media_taxa = float(sum(taxas) / len(taxas))
    return {
        "coorte": int(soma_coorte),
        "retidos": int(soma_retidos),
        "taxa": media_taxa,
        "dia_base": primeiro["dia"],
        "dia_follow": primeiro["dia2"],
        "periodos": len(detalhes),
        "detalhes": detalhes,
    }

# =====================================================
# MÉDIA DE USUÁRIOS ÚNICOS POR PERÍODO (sem gráficos)
# =====================================================
def _aplica_filtros_basicos(df, coluna_data, nomes_lojas, categorias, **kwargs):
    dff = garantir_coluna_data(df, coluna_data)
    if nomes_lojas is None:
        nomes_lojas = kwargs.pop("nome_estabelecimento", None)
    if categorias is None:
        categorias = kwargs.pop("categoria_estabelecimento", None)
    dff = filtrar_lojas_e_categorias(dff, nomes_lojas, categorias)
    return dff

def media_usuarios_unicos_anual(
    df, 
    nomes_lojas=None, categorias=None,
    coluna_data: str = "data", **kwargs
) -> dict:
    """Média de usuários únicos por ANO no df (já filtrado externamente)."""
    dff = _aplica_filtros_basicos(df, coluna_data, nomes_lojas, categorias, **kwargs)
    if dff.empty: 
        return {"media": 0.0, "periodos": 0, "detalhes": []}

    dff["_ano"] = dff[coluna_data].dt.year.astype(int)
    g = (dff.groupby("_ano")["celular"]
            .nunique()
            .reset_index(name="usuarios")
            .sort_values("_ano"))
    media = float(g["usuarios"].mean()) if not g.empty else 0.0

    detalhes = []
    for _, row in g.iterrows():
        detalhes.append({"ano": int(row["_ano"]), "usuarios": int(row["usuarios"])})

    return {"media": media, "periodos": len(detalhes), "detalhes": detalhes}


def media_usuarios_unicos_mensal(
    df, 
    nomes_lojas=None, categorias=None,
    coluna_data: str = "data", **kwargs
) -> dict:
    """Média de usuários únicos por MÊS (YYYY-MM)."""
    dff = _aplica_filtros_basicos(df, coluna_data, nomes_lojas, categorias, **kwargs)
    if dff.empty: 
        return {"media": 0.0, "periodos": 0, "detalhes": []}

    dff["_ano"] = dff[coluna_data].dt.year.astype(int)
    dff["_mes"] = dff[coluna_data].dt.month.astype(int)
    g = (dff.groupby(["_ano","_mes"])["celular"]
            .nunique()
            .reset_index(name="usuarios")
            .sort_values(["_ano","_mes"]))
    media = float(g["usuarios"].mean()) if not g.empty else 0.0

    detalhes = []
    for _, row in g.iterrows():
        detalhes.append({
            "ano": int(row["_ano"]),
            "mes": int(row["_mes"]),
            "usuarios": int(row["usuarios"])
        })

    return {"media": media, "periodos": len(detalhes), "detalhes": detalhes}


def media_usuarios_unicos_semanal_iso(
    df, 
    nomes_lojas=None, categorias=None,
    coluna_data: str = "data", **kwargs
) -> dict:
    """Média de usuários únicos por SEMANA ISO (ano_iso, semana)."""
    dff = _aplica_filtros_basicos(df, coluna_data, nomes_lojas, categorias, **kwargs)
    if dff.empty: 
        return {"media": 0.0, "periodos": 0, "detalhes": []}

    iso = dff[coluna_data].dt.isocalendar()
    dff["_iso_year"] = iso.year.astype(int)
    dff["_iso_week"] = iso.week.astype(int)
    g = (dff.groupby(["_iso_year","_iso_week"])["celular"]
            .nunique()
            .reset_index(name="usuarios")
            .sort_values(["_iso_year","_iso_week"]))
    media = float(g["usuarios"].mean()) if not g.empty else 0.0

    detalhes = []
    for _, row in g.iterrows():
        detalhes.append({
            "ano_iso": int(row["_iso_year"]),
            "semana": int(row["_iso_week"]),
            "usuarios": int(row["usuarios"])
        })

    return {"media": media, "periodos": len(detalhes), "detalhes": detalhes}


def media_usuarios_unicos_diaria(
    df, 
    nomes_lojas=None, categorias=None,
    coluna_data: str = "data", **kwargs
) -> dict:
    """Média de usuários únicos por DIA (YYYY-MM-DD)."""
    dff = _aplica_filtros_basicos(df, coluna_data, nomes_lojas, categorias, **kwargs)
    if dff.empty: 
        return {"media": 0.0, "periodos": 0, "detalhes": []}

    dff["_dia"] = dff[coluna_data].dt.normalize()
    g = (dff.groupby("_dia")["celular"]
            .nunique()
            .reset_index(name="usuarios")
            .sort_values("_dia"))
    media = float(g["usuarios"].mean()) if not g.empty else 0.0

    detalhes = []
    for _, row in g.iterrows():
        detalhes.append({
            "dia": row["_dia"].date().isoformat(),
            "usuarios": int(row["usuarios"])
        })

    return {"media": media, "periodos": len(detalhes), "detalhes": detalhes}


def _mes_int(mes):
    """Aceita int (1..12) ou nome em PT ('Novembro') e retorna int 1..12."""
    if isinstance(mes, int):
        return mes
    mapa = {
        "janeiro":1,"fevereiro":2,"março":3,"marco":3,"abril":4,"maio":5,"junho":6,
        "julho":7,"agosto":8,"setembro":9,"outubro":10,"novembro":11,"dezembro":12
    }
    return mapa.get(str(mes).strip().lower())

def _limites_mes(ano: int, mes: int):
    """Retorna (primeiro_dia, ultimo_dia) do mês/ano."""
    inicio = pd.Timestamp(year=int(ano), month=int(mes), day=1).normalize()
    if mes == 12:
        fim = pd.Timestamp(year=int(ano)+1, month=1, day=1) - pd.Timedelta(days=1)
    else:
        fim = pd.Timestamp(year=int(ano), month=int(mes)+1, day=1) - pd.Timedelta(days=1)
    return inicio.normalize(), fim.normalize()

def retencao_por_defasagem_dias(
    df: pd.DataFrame,
    ano: int,
    mes,                               # int 1..12 ou nome PT
    max_defasagem_dias: int | None = None,
    nomes_lojas=None,
    categorias=None,
    coluna_data: str = "data",
) -> pd.DataFrame:
    mes = _mes_int(mes)
    if not mes:
        raise ValueError("Parâmetro 'mes' deve ser 1..12 ou nome PT (ex.: 'Novembro').")

    dff = garantir_coluna_data(df, coluna_data)
    dff = filtrar_lojas_e_categorias(dff, nomes_lojas, categorias)
    if dff.empty:
        return pd.DataFrame(columns=["janela_dias","coorte","retidos","taxa"])

    # recorte do mês/ano
    dff["_ano"] = dff[coluna_data].dt.year
    dff["_mes"] = dff[coluna_data].dt.month
    dff = dff[(dff["_ano"] == int(ano)) & (dff["_mes"] == int(mes))].copy()
    if dff.empty:
        return pd.DataFrame(columns=["janela_dias","coorte","retidos","taxa"])

    d_inicio, d_fim = _limites_mes(int(ano), int(mes))
    dias_no_mes = (d_fim - d_inicio).days + 1

    # se max_defasagem_dias não for passado, usa o limite do mês
    if max_defasagem_dias is None or max_defasagem_dias > dias_no_mes:
        max_defasagem_dias = dias_no_mes - 1  # último intervalo possível

    # granularidade de dias por usuário
    dff["_dia"] = dff[coluna_data].dt.normalize()
    user_day = dff[["celular","_dia"]].dropna().drop_duplicates()

    base = user_day.rename(columns={"_dia":"dia_base"})
    resultados = []

    for k in range(1, int(max_defasagem_dias) + 1):
        limite_comp = d_fim - pd.Timedelta(days=k)
        elegiveis = base[base["dia_base"] <= limite_comp]

        if elegiveis.empty:
            resultados.append({"janela_dias": k, "coorte": 0, "retidos": 0, "taxa": 0.0})
            continue

        elegiveis = elegiveis.copy()
        elegiveis["dia_follow"] = elegiveis["dia_base"] + pd.Timedelta(days=k)
        follow = user_day.rename(columns={"_dia":"dia_follow"})
        pares = elegiveis.merge(follow, on=["celular","dia_follow"], how="inner")

        coorte_k = len(elegiveis)
        retidos_k = len(pares)
        taxa_k = (retidos_k / coorte_k) if coorte_k > 0 else 0.0

        resultados.append({
            "janela_dias": k,
            "coorte": int(coorte_k),
            "retidos": int(retidos_k),
            "taxa": float(taxa_k),
        })

    return pd.DataFrame(resultados)


def grafico_retencao_por_defasagem(
    df: pd.DataFrame,
    ano: int,
    mes,                               # int 1..12 ou nome PT
    max_defasagem_dias: int | None = None,
    nomes_lojas=None,
    categorias=None,
    coluna_data: str = "data",
    modo: str = "percentual",          # "percentual" | "valores" | "ambos"
):
    """
    Gera um gráfico de LINHA com a taxa por defasagem (k dias), ajustando o limite
    automaticamente ao número de dias do mês quando necessário. Destaca o pico.
    """
    # Calcula a tabela base já respeitando o limite de dias do mês (quando None)
    res = retencao_por_defasagem_dias(
        df, ano, mes, max_defasagem_dias,
        nomes_lojas=nomes_lojas,
        categorias=categorias,
        coluna_data=coluna_data,
    )
    if res.empty or len(res) == 0:
        return px.line(title="Retenção por defasagem – sem dados")

    modo_norm = str(modo or "").strip().lower()
    if modo_norm not in {"percentual", "valores", "ambos"}:
        modo_norm = "percentual"

    # Eixo Y conforme modo
    y_col = "taxa" if modo_norm == "percentual" else "retidos"

    fig = px.line(
        res, x="janela_dias", y=y_col,
        markers=True,
        labels={
            "janela_dias": "Defasagem (dias)",
            y_col: "Taxa de Retenção" if y_col == "taxa" else "Retidos (contagem)"
        },
        title="Retenção por defasagem de dias (retorno exato após k dias)",
    )

    # Rótulos
    if modo_norm == "percentual":
        fig.update_traces(text=res["taxa"].map(lambda v: f"{v*100:.1f}%"),
                          textposition="top center",
                          hovertemplate="k=%{x}<br>Taxa=%{y:.2%}<extra></extra>")
        fig.update_yaxes(tickformat=".0%")
    elif modo_norm == "valores":
        fig.update_traces(text=res["retidos"].astype(str),
                          textposition="top center",
                          hovertemplate="k=%{x}<br>Retidos=%{y}<extra></extra>")
    else:  # "ambos"
        textos = res.apply(lambda r: f"{r['retidos']}  •  {r['taxa']*100:.1f}%", axis=1)
        fig.update_traces(text=textos, textposition="top center",
                          hovertemplate=(
                              "k=%{x}"
                              "<br>Retidos=%{customdata[0]}"
                              "<br>Taxa=%{y:.2%}<extra></extra>"
                          ),
                          customdata=res[["retidos"]].to_numpy())
        # Em "ambos" o y continua sendo 'taxa' (para eixo em %)
        if y_col != "taxa":
            # se veio em 'valores', força eixo percentual
            fig.update_yaxes(tickformat=".0%")

    # Pico (k com maior taxa)
    try:
        idx_pico = int(res["taxa"].idxmax())
        k_pico = int(res.loc[idx_pico, "janela_dias"])
        taxa_pico = float(res.loc[idx_pico, "taxa"])
        fig.add_vline(x=k_pico, line_dash="dot", opacity=0.5)
        fig.add_annotation(
            x=k_pico, y=taxa_pico if y_col == "taxa" else res.loc[idx_pico, "retidos"],
            text=f"Pico em k={k_pico} ({taxa_pico*100:.1f}%)",
            showarrow=True, arrowhead=2, yshift=10
        )
    except Exception:
        pass

    fig.update_layout(height=420, xaxis=dict(dtick=1))
    return fig
