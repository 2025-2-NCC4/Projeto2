import pandas as pd
import numpy as np
import plotly.express as px

# =========================
# Helpers compartilhados
# =========================
MESES_PT = {
    1:"Janeiro",2:"Fevereiro",3:"Março",4:"Abril",5:"Maio",6:"Junho",
    7:"Julho",8:"Agosto",9:"Setembro",10:"Outubro",11:"Novembro",12:"Dezembro"
}
MESES_INV = {v.lower(): k for k, v in MESES_PT.items()}
DIAS_PT = {0:"Segunda",1:"Terça",2:"Quarta",3:"Quinta",4:"Sexta",5:"Sábado",6:"Domingo"}

def _norm_str(x: str) -> str:
    return str(x).strip().casefold()

def _as_list_norm(x):
    """Converte None/str/list para lista normalizada (casefold/strip).
    Trata 'todas'/'all'/'' como vazio (sem filtro)."""
    if x is None:
        return []
    if isinstance(x, (list, tuple, set)):
        vals = [_norm_str(v) for v in x if _norm_str(v) not in {"", "todas", "all"}]
        return list(dict.fromkeys(vals))  # unique, stable
    # str simples
    v = _norm_str(x)
    if v in {"", "todas", "all"}:
        return []
    return [v]

def _apply_store_filters(df, nome_estabelecimento=None, categoria_estabelecimento=None):
    dff = df.copy()
    lojas = _as_list_norm(nome_estabelecimento)
    tipos = _as_list_norm(categoria_estabelecimento)

    if lojas and "nome_estabelecimento" in dff.columns:
        dff = dff[
            dff["nome_estabelecimento"].astype(str).str.strip().str.casefold().isin(lojas)
        ]
    if tipos and "categoria_estabelecimento" in dff.columns:
        dff = dff[
            dff["categoria_estabelecimento"].astype(str).str.strip().str.casefold().isin(tipos)
        ]
    return dff

def _label_sufixo(nome_estabelecimento=None, categoria_estabelecimento=None):
    """Constroi sufixo de título a partir dos filtros (lista ou str)."""
    lojas = _as_list_norm(nome_estabelecimento)
    tipos = _as_list_norm(categoria_estabelecimento)
    sufixos = []
    if lojas:
        sufixos.append(" / ".join(lojas))
    if tipos:
        sufixos.append(" / ".join(tipos))
    return f" – {', '.join(sufixos)}" if sufixos else ""

def _parse_mes(mes):
    """Aceita int (1-12) ou nome PT-BR."""
    if mes is None:
        return None
    if isinstance(mes, (int, np.integer)):
        return int(mes) if 1 <= int(mes) <= 12 else None
    if isinstance(mes, str):
        m = MESES_INV.get(mes.lower())
        return m if m in range(1, 13) else None
    try:
        m = int(mes)
        return m if 1 <= m <= 12 else None
    except Exception:
        return None

def _modo_text_series(df_vals, y_col="valor", pct_col="pct", modo="valores"):
    m = _norm_str(modo)
    if m == "percentual":
        return df_vals[pct_col].map(lambda x: f"{x:.1%}")
    if m == "ambos":
        return df_vals.apply(lambda r: f'{int(r[y_col])}  ({r[pct_col]:.1%})', axis=1)
    # default: valores
    return df_vals[y_col].astype(int).astype(str)

# =========================
# Funções de frequência
# =========================
def frequencia_diaria_filtrada(df, mes, ano, nome_estabelecimento=None, categoria_estabelecimento=None, modo="valores"):
    dff = df.copy()
    dff["data"] = pd.to_datetime(dff["data"], errors="coerce")
    dff = dff.dropna(subset=["data"])
    dff = _apply_store_filters(dff, nome_estabelecimento, categoria_estabelecimento)
    sufixo = _label_sufixo(nome_estabelecimento, categoria_estabelecimento)

    mes_num = _parse_mes(mes)
    if mes_num is None:
        return px.bar(title=f"Mês inválido: {mes}")

    dff = dff[(dff["data"].dt.year == int(ano)) & (dff["data"].dt.month == mes_num)]
    if dff.empty:
        return px.bar(title=f"Sem dados para {MESES_PT.get(mes_num, mes)} {ano}{sufixo}")

    # Agrupar por dia (normalizado a data)
    s = (
        dff.groupby(dff["data"].dt.date)["celular"]
           .nunique()
           .reset_index(name="valor")
           .sort_values("data")
    )
    s["dia"] = pd.to_datetime(s["data"]).dt.day
    total = s["valor"].sum()
    s["pct"] = (s["valor"] / total).fillna(0.0) if total > 0 else 0.0

    m = _norm_str(modo)
    y, label_y = ("pct", "% do total") if m == "percentual" else ("valor", "Capturas")
    fig = px.bar(
        s, x="dia", y=y,
        text=_modo_text_series(s, y_col="valor", pct_col="pct", modo=m),
        color=y, color_continuous_scale="Blues",
        title=f"Frequência Diária de Capturas – {MESES_PT[mes_num]} {ano}{sufixo}",
        labels={"dia":"Dias", y: label_y}
    )
    fig.update_layout(height=500, xaxis=dict(tickmode="linear", tick0=1, dtick=1),
                      yaxis_tickformat=".0%" if m == "percentual" else None)
    return fig

def frequencia_semanal_filtrada(df, ano, nome_estabelecimento=None, categoria_estabelecimento=None, modo="valores"):
    dff = df.copy()
    dff["data"] = pd.to_datetime(dff["data"], errors="coerce")
    dff = dff.dropna(subset=["data"])
    dff = dff[dff["data"].dt.year == int(ano)]
    dff = _apply_store_filters(dff, nome_estabelecimento, categoria_estabelecimento)
    sufixo = _label_sufixo(nome_estabelecimento, categoria_estabelecimento)

    if dff.empty:
        return px.bar(title=f"Sem dados para {ano}{sufixo}")

    dff["semana"] = dff["data"].dt.isocalendar().week.astype(int)
    g = dff.groupby("semana")["celular"].nunique().reset_index(name="valor")
    semanas_ano = pd.DataFrame({"semana": range(1, 54)})
    g = semanas_ano.merge(g, on="semana", how="left").fillna(0)
    g["valor"] = g["valor"].astype(int)
    g["semana_label"] = g["semana"].apply(lambda x: f"Semana {x}")
    total = g["valor"].sum()
    g["pct"] = (g["valor"] / total).fillna(0.0) if total > 0 else 0.0

    m = _norm_str(modo)
    y, label_y = ("pct", "% do total") if m == "percentual" else ("valor", "Capturas")
    fig = px.bar(
        g, x="semana_label", y=y,
        text=_modo_text_series(g, y_col="valor", pct_col="pct", modo=m),
        color=y, color_continuous_scale="Blues",
        title=f"Frequência Semanal de Capturas – {ano}{sufixo}",
        labels={"semana_label":"Semanas", y: label_y}
    )
    fig.update_layout(height=480, xaxis=dict(showgrid=False, tickangle=-45),
                      yaxis_tickformat=".0%" if m == "percentual" else None)
    return fig

def frequencia_dia_semana_ano_filtrada(df, ano, nome_estabelecimento=None, categoria_estabelecimento=None, modo="valores"):
    dff = df.copy()
    dff["data"] = pd.to_datetime(dff["data"], errors="coerce")
    dff = dff.dropna(subset=["data"])
    dff = dff[dff["data"].dt.year == int(ano)]
    dff = _apply_store_filters(dff, nome_estabelecimento, categoria_estabelecimento)
    sufixo = _label_sufixo(nome_estabelecimento, categoria_estabelecimento)

    if dff.empty:
        return px.bar(title=f"Sem dados disponíveis para {ano}{sufixo}")

    dff["dia_semana_num"] = dff["data"].dt.dayofweek
    g = dff.groupby("dia_semana_num")["celular"].nunique().reset_index(name="valor")
    base_dias = pd.DataFrame({"dia_semana_num": range(0, 7)})
    g = base_dias.merge(g, on="dia_semana_num", how="left").fillna(0)
    g["valor"] = g["valor"].astype(int)
    g["dia_label"] = g["dia_semana_num"].map(DIAS_PT)
    total = g["valor"].sum()
    g["pct"] = (g["valor"] / total).fillna(0.0) if total > 0 else 0.0

    m = _norm_str(modo)
    y, label_y = ("pct", "% do total") if m == "percentual" else ("valor", "Capturas")
    fig = px.bar(
        g, x="dia_label", y=y,
        text=_modo_text_series(g, y_col="valor", pct_col="pct", modo=m),
        color=y, color_continuous_scale="Blues",
        title=f"Frequência de Capturas por Dia da Semana – {ano}{sufixo}",
        labels={"dia_label":"Dia da Semana", y: label_y}
    )
    fig.update_layout(height=480, xaxis=dict(showgrid=False),
                      yaxis_tickformat=".0%" if m == "percentual" else None)
    return fig

def frequencia_dia_semana_mes_filtrada(df, ano, mes=None, nome_estabelecimento=None, categoria_estabelecimento=None, modo="valores"):
    dff = df.copy()
    dff["data"] = pd.to_datetime(dff["data"], errors="coerce")
    dff = dff.dropna(subset=["data"])
    dff = dff[dff["data"].dt.year == int(ano)]
    dff = _apply_store_filters(dff, nome_estabelecimento, categoria_estabelecimento)

    sufixo_loja = _label_sufixo(nome_estabelecimento, categoria_estabelecimento)
    sufixo_mes = ""
    if mes is not None:
        mes_num = _parse_mes(mes)
        if mes_num is None:
            return px.bar(title=f"Mês inválido: {mes}")
        dff = dff[dff["data"].dt.month == mes_num]
        sufixo_mes = f" – {MESES_PT[mes_num]}"

    if dff.empty:
        return px.bar(title=f"Sem dados disponíveis para {ano}{sufixo_mes}{sufixo_loja}")

    dff["dia_semana_num"] = dff["data"].dt.dayofweek
    g = dff.groupby("dia_semana_num")["celular"].nunique().reset_index(name="valor")
    base_dias = pd.DataFrame({"dia_semana_num": range(0, 7)})
    g = base_dias.merge(g, on="dia_semana_num", how="left").fillna(0)
    g["valor"] = g["valor"].astype(int)
    g["dia_label"] = g["dia_semana_num"].map(DIAS_PT)
    total = g["valor"].sum()
    g["pct"] = (g["valor"] / total).fillna(0.0) if total > 0 else 0.0

    titulo = f"Frequência de Capturas por Dia da Semana – {ano}{sufixo_mes}{sufixo_loja}"
    m = _norm_str(modo)
    y, label_y = ("pct", "% do total") if m == "percentual" else ("valor", "Capturas")
    fig = px.bar(
        g, x="dia_label", y=y,
        text=_modo_text_series(g, y_col="valor", pct_col="pct", modo=m),
        color=y, color_continuous_scale="Blues",
        title=titulo, labels={"dia_label":"Dia da Semana", y: label_y}
    )
    fig.update_layout(height=480, xaxis=dict(showgrid=False),
                      yaxis_tickformat=".0%" if m == "percentual" else None)
    return fig

def frequencia_mensal_filtrada(df, ano, nome_estabelecimento=None, categoria_estabelecimento=None, modo="valores"):
    dff = df.copy()
    dff["data"] = pd.to_datetime(dff["data"], errors="coerce")
    dff = dff.dropna(subset=["data"])
    dff = dff[dff["data"].dt.year == int(ano)]
    dff = _apply_store_filters(dff, nome_estabelecimento, categoria_estabelecimento)
    sufixo = _label_sufixo(nome_estabelecimento, categoria_estabelecimento)

    if dff.empty:
        return px.bar(title=f"Sem dados disponíveis para {ano}{sufixo}")

    dff["mes_num"] = dff["data"].dt.month
    g = (dff.groupby("mes_num")["celular"].nunique()
            .reindex(range(1,13), fill_value=0)
            .reset_index(name="valor"))
    g["mes_label"] = g["mes_num"].map(MESES_PT)
    total = g["valor"].sum()
    g["pct"] = (g["valor"] / total).fillna(0.0) if total > 0 else 0.0

    m = _norm_str(modo)
    y, label_y = ("pct", "% do total") if m == "percentual" else ("valor", "Capturas")
    fig = px.bar(
        g, x="mes_label", y=y,
        text=_modo_text_series(g, y_col="valor", pct_col="pct", modo=m),
        color=y, color_continuous_scale="Blues",
        title=f"Frequência Mensal de Capturas – {ano}{sufixo}",
        labels={"mes_label":"Meses", y: label_y}
    )
    fig.update_layout(height=480, xaxis=dict(showgrid=False, tickangle=-45),
                      yaxis_tickformat=".0%" if m == "percentual" else None)
    return fig

def frequencia_ano_filtrada(df, nome_estabelecimento=None, categoria_estabelecimento=None, modo="valores"):
    dff = df.copy()
    dff["data"] = pd.to_datetime(dff["data"], errors="coerce")
    dff = dff.dropna(subset=["data"])
    dff = _apply_store_filters(dff, nome_estabelecimento, categoria_estabelecimento)
    sufixo = _label_sufixo(nome_estabelecimento, categoria_estabelecimento)

    if dff.empty:
        return px.bar(title=f"Sem dados disponíveis{sufixo}")

    dff["ano"] = dff["data"].dt.year
    g = (dff.groupby("ano")["celular"].nunique()
            .reset_index(name="valor").sort_values("ano"))
    total = g["valor"].sum()
    g["pct"] = (g["valor"] / total).fillna(0.0) if total > 0 else 0.0

    m = _norm_str(modo)
    y, label_y = ("pct", "% do total") if m == "percentual" else ("valor", "Capturas")
    fig = px.bar(
        g, x="ano", y=y,
        text=_modo_text_series(g, y_col="valor", pct_col="pct", modo=m),
        color=y, color_continuous_scale="Blues",
        title=f"Frequência Anual de Capturas{sufixo}",
        labels={"ano":"Anos", y: label_y}
    )
    fig.update_layout(height=480, xaxis=dict(showgrid=False),
                      yaxis_tickformat=".0%" if m == "percentual" else None)
    return fig

def medias_frequencia_filtrada(df, mes, ano, nome_estabelecimento=None, categoria_estabelecimento=None):
    dff = df.copy()
    dff["data"] = pd.to_datetime(dff["data"], errors="coerce")
    dff = dff.dropna(subset=["data"])
    dff = _apply_store_filters(dff, nome_estabelecimento, categoria_estabelecimento)

    mes_num = _parse_mes(mes)
    if mes_num is None:
        # mantém retorno válido mesmo com mês inválido
        return {"media_diaria_mes_ano": 0.0, "media_semanal_ano": 0.0,
                "media_mensal_ano": 0.0, "media_anual": 0.0}

    # ---- MÉDIA DIÁRIA (mês/ano) ----
    dff_ma = dff[(dff["data"].dt.year == int(ano)) & (dff["data"].dt.month == mes_num)]
    if dff_ma.empty:
        media_diaria = 0.0
    else:
        primeiro_dia = pd.Timestamp(year=int(ano), month=mes_num, day=1)
        ultimo_dia = primeiro_dia + pd.offsets.MonthEnd(0)
        idx_dias = pd.date_range(primeiro_dia, ultimo_dia, freq="D")
        s_dia = (
            dff_ma.groupby(dff_ma["data"].dt.date)["celular"]
                  .nunique()
                  .reindex(idx_dias.date, fill_value=0)
        )
        media_diaria = float(s_dia.mean())

    # ---- MÉDIA SEMANAL (ano) ----
    dff_ano = dff[dff["data"].dt.year == int(ano)]
    if dff_ano.empty:
        media_semanal = 0.0
    else:
        inicio_ano = pd.Timestamp(year=int(ano), month=1, day=1)
        fim_ano = pd.Timestamp(year=int(ano), month=12, day=31)
        idx_sem = pd.date_range(inicio_ano, fim_ano, freq="W-SUN")
        s_sem = (
            dff_ano.set_index("data")
                   .groupby(pd.Grouper(freq="W-SUN"))["celular"]
                   .nunique()
                   .reindex(idx_sem, fill_value=0)
        )
        media_semanal = float(s_sem.mean())

    # ---- MÉDIA MENSAL (ano) ----
    if dff_ano.empty:
        media_mensal = 0.0
    else:
        s_mes = (
            dff_ano.groupby(dff_ano["data"].dt.month)["celular"]
                   .nunique()
                   .reindex(range(1, 13), fill_value=0)
        )
        media_mensal = float(s_mes.mean())

    # ---- MÉDIA ANUAL (toda base) ----
    s_ano = dff.groupby(dff["data"].dt.year)["celular"].nunique().sort_index()
    media_anual = float(s_ano.mean()) if not s_ano.empty else 0.0

    return {
        "media_diaria_mes_ao": media_diaria,   # mantive chaves; ajuste se quiser outro nome
        "media_semanal_ano": media_semanal,
        "media_mensal_ano": media_mensal,
        "media_anual": media_anual
    }
