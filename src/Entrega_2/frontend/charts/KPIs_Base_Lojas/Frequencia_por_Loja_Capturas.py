import pandas as pd
import numpy as np
import plotly.express as px

def frequencia_diaria_filtrada(df, mes, ano, nome_loja=None, tipo_loja=None, modo="valores"):
    df = df.copy()
    df["data_captura"] = pd.to_datetime(df["data_captura"], errors="coerce")
    df = df.dropna(subset=["data_captura"])

    def _norm(x): return str(x).strip().casefold()
    sufixo = ""
    if nome_loja and _norm(nome_loja) not in {"todas","all",""}:
        df = df[df["nome_loja"].astype(str).str.strip().str.casefold() == _norm(nome_loja)]
        sufixo = f" – {nome_loja}"
    elif tipo_loja and _norm(tipo_loja) not in {"todas","all",""}:
        df = df[df["tipo_loja"].astype(str).str.strip().str.casefold() == _norm(tipo_loja)]
        sufixo = f" – {tipo_loja}"

    meses_pt = {1:"Janeiro",2:"Fevereiro",3:"Março",4:"Abril",5:"Maio",6:"Junho",7:"Julho",8:"Agosto",9:"Setembro",10:"Outubro",11:"Novembro",12:"Dezembro"}
    mes_num = int(mes) if not isinstance(mes, str) else {v.lower(): k for k, v in meses_pt.items()}.get(mes.lower(), 0)
    if mes_num not in range(1,13):
        return px.bar(title=f"Mês inválido: {mes}")

    df = df[(df["data_captura"].dt.year == ano) & (df["data_captura"].dt.month == mes_num)]
    if df.empty:
        return px.bar(title=f"Sem dados para {meses_pt.get(mes_num, mes)} {ano}{sufixo}")

    s = (df.groupby("data_captura")["numero_celular"].nunique()
           .reset_index(name="valor").sort_values("data_captura"))
    s["dia"] = s["data_captura"].dt.day
    total = s["valor"].sum()
    s["pct"] = (s["valor"] / total).fillna(0.0) if total > 0 else 0.0

    if modo.lower() == "percentual":
        fig = px.bar(s, x="dia", y="pct",
                     text=s["pct"].map(lambda x: f"{x:.1%}"),
                     color="pct", color_continuous_scale="Blues",
                     title=f"Frequência Diária de Capturas – {meses_pt[mes_num]} {ano}{sufixo}",
                     labels={"dia":"Dias","pct":"% do total"})
        fig.update_layout(height=500, xaxis=dict(tickmode="linear", tick0=1, dtick=1), yaxis_tickformat=".0%")
        return fig

    text_series = s["valor"].astype(int).astype(str) if modo.lower() == "valores" \
                  else s.apply(lambda r: f'{int(r["valor"])}  ({r["pct"]:.1%})', axis=1)

    fig = px.bar(s, x="dia", y="valor",
                 text=text_series, color="valor", color_continuous_scale="Blues",
                 title=f"Frequência Diária de Capturas – {meses_pt[mes_num]} {ano}{sufixo}",
                 labels={"dia":"Dias","valor":"Capturas"})
    fig.update_layout(height=500, xaxis=dict(tickmode="linear", tick0=1, dtick=1))
    return fig

def frequencia_semanal_filtrada(df, ano, nome_loja=None, tipo_loja=None, modo="valores"):
    df = df.copy()
    df["data_captura"] = pd.to_datetime(df["data_captura"], errors="coerce")
    df = df.dropna(subset=["data_captura"])
    df = df[df["data_captura"].dt.year == ano]

    def _norm(x): return str(x).strip().casefold()
    sufixo = ""
    if nome_loja and _norm(nome_loja) not in {"todas","all",""}:
        df = df[df["nome_loja"].astype(str).str.strip().str.casefold() == _norm(nome_loja)]
        sufixo = f" – {nome_loja}"
    elif tipo_loja and _norm(tipo_loja) not in {"todas","all",""}:
        df = df[df["tipo_loja"].astype(str).str.strip().str.casefold() == _norm(tipo_loja)]
        sufixo = f" – {tipo_loja}"

    if df.empty:
        return px.bar(title=f"Sem dados para {ano}{sufixo}")

    df["semana"] = df["data_captura"].dt.isocalendar().week
    g = df.groupby("semana")["numero_celular"].nunique().reset_index(name="valor")
    semanas_ano = pd.DataFrame({"semana": range(1, 54)})
    g = semanas_ano.merge(g, on="semana", how="left").fillna(0)
    g["valor"] = g["valor"].astype(int)
    g["semana_label"] = g["semana"].apply(lambda x: f"Semana {x}")
    total = g["valor"].sum()
    g["pct"] = (g["valor"] / total).fillna(0.0) if total > 0 else 0.0

    if modo.lower() == "percentual":
        fig = px.bar(g, x="semana_label", y="pct",
                     text=g["pct"].map(lambda x: f"{x:.1%}"),
                     color="pct", color_continuous_scale="Blues",
                     title=f"Frequência Semanal de Capturas – {ano}{sufixo}",
                     labels={"semana_label":"Semanas","pct":"% do total"})
        fig.update_layout(height=480, xaxis=dict(showgrid=False, tickangle=-45), yaxis_tickformat=".0%")
        return fig

    text_series = g["valor"].astype(int).astype(str) if modo.lower() == "valores" \
                  else g.apply(lambda r: f'{int(r["valor"])}  ({r["pct"]:.1%})', axis=1)

    fig = px.bar(g, x="semana_label", y="valor",
                 text=text_series, color="valor", color_continuous_scale="Blues",
                 title=f"Frequência Semanal de Capturas – {ano}{sufixo}",
                 labels={"semana_label":"Semanas","valor":"Capturas"})
    fig.update_layout(height=480, xaxis=dict(showgrid=False, tickangle=-45))
    return fig

def frequencia_dia_semana_ano_filtrada(df, ano, nome_loja=None, tipo_loja=None, modo="valores"):
    df = df.copy()
    df["data_captura"] = pd.to_datetime(df["data_captura"], errors="coerce")
    df = df.dropna(subset=["data_captura"])
    df = df[df["data_captura"].dt.year == ano]

    def _norm(x): return str(x).strip().casefold()
    sufixo = ""
    if nome_loja and _norm(nome_loja) not in {"todas", "all", ""}:
        df = df[df["nome_loja"].astype(str).str.strip().str.casefold() == _norm(nome_loja)]
        sufixo = f" – {nome_loja}"
    elif tipo_loja and _norm(tipo_loja) not in {"todas", "all", ""}:
        df = df[df["tipo_loja"].astype(str).str.strip().str.casefold() == _norm(tipo_loja)]
        sufixo = f" – {tipo_loja}"

    if df.empty:
        return px.bar(title=f"Sem dados disponíveis para {ano}{sufixo}")

    dias_pt = {0:"Segunda",1:"Terça",2:"Quarta",3:"Quinta",4:"Sexta",5:"Sábado",6:"Domingo"}

    df["dia_semana_num"] = df["data_captura"].dt.dayofweek
    g = (df.groupby("dia_semana_num")["numero_celular"]
           .nunique()
           .reset_index(name="valor"))

    base_dias = pd.DataFrame({"dia_semana_num": range(0, 7)})
    g = base_dias.merge(g, on="dia_semana_num", how="left").fillna(0)
    g["valor"] = g["valor"].astype(int)
    g["dia_label"] = g["dia_semana_num"].map(dias_pt)

    total = g["valor"].sum()
    g["pct"] = (g["valor"] / total).fillna(0.0) if total > 0 else 0.0

    if modo.lower() == "percentual":
        fig = px.bar(
            g, x="dia_label", y="pct",
            text=g["pct"].map(lambda x: f"{x:.1%}"),
            color="pct", color_continuous_scale="Blues",
            title=f"Frequência de Capturas por Dia da Semana – {ano}{sufixo}",
            labels={"dia_label":"Dia da Semana","pct":"% do total"},
        )
        fig.update_layout(height=480, xaxis=dict(showgrid=False), yaxis_tickformat=".0%")
        return fig

    text_series = g["valor"].astype(int).astype(str) if modo.lower() == "valores" \
                  else g.apply(lambda r: f'{int(r["valor"])}  ({r["pct"]:.1%})', axis=1)

    fig = px.bar(
        g, x="dia_label", y="valor",
        text=text_series, color="valor", color_continuous_scale="Blues",
        title=f"Frequência de Capturas por Dia da Semana – {ano}{sufixo}",
        labels={"dia_label":"Dia da Semana","valor":"Capturas"},
    )
    fig.update_layout(height=480, xaxis=dict(showgrid=False))
    return fig

def frequencia_dia_semana_mes_filtrada(df, ano, mes=None, nome_loja=None, tipo_loja=None, modo="valores"):
    df = df.copy()
    df["data_captura"] = pd.to_datetime(df["data_captura"], errors="coerce")
    df = df.dropna(subset=["data_captura"])
    df = df[df["data_captura"].dt.year == ano]

    def _norm(x): return str(x).strip().casefold()
    sufixo_loja = ""
    if nome_loja and _norm(nome_loja) not in {"todas", "all", ""}:
        df = df[df["nome_loja"].astype(str).str.strip().str.casefold() == _norm(nome_loja)]
        sufixo_loja = f" – {nome_loja}"
    elif tipo_loja and _norm(tipo_loja) not in {"todas", "all", ""}:
        df = df[df["tipo_loja"].astype(str).str.strip().str.casefold() == _norm(tipo_loja)]
        sufixo_loja = f" – {tipo_loja}"

    meses_pt = {1:"Janeiro",2:"Fevereiro",3:"Março",4:"Abril",5:"Maio",6:"Junho",
                7:"Julho",8:"Agosto",9:"Setembro",10:"Outubro",11:"Novembro",12:"Dezembro"}
    sufixo_mes = ""
    if mes:
        mes_num = int(mes) if not isinstance(mes, str) else {v.lower(): k for k, v in meses_pt.items()}.get(mes.lower())
        if mes_num in range(1, 13):
            df = df[df["data_captura"].dt.month == mes_num]
            sufixo_mes = f" – {meses_pt[mes_num]}"
        else:
            return px.bar(title=f"Mês inválido: {mes}")

    if df.empty:
        return px.bar(title=f"Sem dados disponíveis para {ano}{sufixo_mes}{sufixo_loja}")

    dias_pt = {0:"Segunda",1:"Terça",2:"Quarta",3:"Quinta",4:"Sexta",5:"Sábado",6:"Domingo"}

    df["dia_semana_num"] = df["data_captura"].dt.dayofweek
    g = (df.groupby("dia_semana_num")["numero_celular"]
           .nunique()
           .reset_index(name="valor"))

    base_dias = pd.DataFrame({"dia_semana_num": range(0, 7)})
    g = base_dias.merge(g, on="dia_semana_num", how="left").fillna(0)
    g["valor"] = g["valor"].astype(int)
    g["dia_label"] = g["dia_semana_num"].map(dias_pt)

    total = g["valor"].sum()
    g["pct"] = (g["valor"] / total).fillna(0.0) if total > 0 else 0.0

    titulo = f"Frequência de Capturas por Dia da Semana – {ano}{sufixo_mes}{sufixo_loja}"

    if modo.lower() == "percentual":
        fig = px.bar(
            g, x="dia_label", y="pct",
            text=g["pct"].map(lambda x: f"{x:.1%}"),
            color="pct", color_continuous_scale="Blues",
            title=titulo, labels={"dia_label":"Dia da Semana","pct":"% do total"},
        )
        fig.update_layout(height=480, xaxis=dict(showgrid=False), yaxis_tickformat=".0%")
        return fig

    text_series = g["valor"].astype(int).astype(str) if modo.lower() == "valores" \
                  else g.apply(lambda r: f'{int(r["valor"])}  ({r["pct"]:.1%})', axis=1)

    fig = px.bar(
        g, x="dia_label", y="valor",
        text=text_series, color="valor", color_continuous_scale="Blues",
        title=titulo, labels={"dia_label":"Dia da Semana","valor":"Capturas"},
    )
    fig.update_layout(height=480, xaxis=dict(showgrid=False))
    return fig

def frequencia_mensal_filtrada(df, ano, nome_loja=None, tipo_loja=None, modo="valores"):
    df = df.copy()
    df["data_captura"] = pd.to_datetime(df["data_captura"], errors="coerce")
    df = df.dropna(subset=["data_captura"])
    df = df[df["data_captura"].dt.year == ano]

    def _norm(x): return str(x).strip().casefold()
    sufixo = ""
    if nome_loja and _norm(nome_loja) not in {"todas","all",""}:
        df = df[df["nome_loja"].astype(str).str.strip().str.casefold() == _norm(nome_loja)]
        sufixo = f" – {nome_loja}"
    elif tipo_loja and _norm(tipo_loja) not in {"todas","all",""}:
        df = df[df["tipo_loja"].astype(str).str.strip().str.casefold() == _norm(tipo_loja)]
        sufixo = f" – {tipo_loja}"

    if df.empty:
        return px.bar(title=f"Sem dados disponíveis para {ano}{sufixo}")

    meses_pt = {1:"Janeiro",2:"Fevereiro",3:"Março",4:"Abril",5:"Maio",6:"Junho",7:"Julho",8:"Agosto",9:"Setembro",10:"Outubro",11:"Novembro",12:"Dezembro"}
    df["mes_num"] = df["data_captura"].dt.month
    g = (df.groupby("mes_num")["numero_celular"].nunique()
           .reindex(range(1,13), fill_value=0)
           .reset_index(name="valor"))
    g["mes_label"] = g["mes_num"].map(meses_pt)
    total = g["valor"].sum()
    g["pct"] = (g["valor"] / total).fillna(0.0) if total > 0 else 0.0

    if modo.lower() == "percentual":
        fig = px.bar(g, x="mes_label", y="pct",
                     text=g["pct"].map(lambda x: f"{x:.1%}"),
                     color="pct", color_continuous_scale="Blues",
                     title=f"Frequência Mensal de Capturas – {ano}{sufixo}",
                     labels={"mes_label":"Meses","pct":"% do total"})
        fig.update_layout(height=480, xaxis=dict(showgrid=False, tickangle=-45), yaxis_tickformat=".0%")
        return fig

    text_series = g["valor"].astype(int).astype(str) if modo.lower() == "valores" \
                  else g.apply(lambda r: f'{int(r["valor"])}  ({r["pct"]:.1%})', axis=1)

    fig = px.bar(g, x="mes_label", y="valor",
                 text=text_series, color="valor", color_continuous_scale="Blues",
                 title=f"Frequência Mensal de Capturas – {ano}{sufixo}",
                 labels={"mes_label":"Meses","valor":"Capturas"})
    fig.update_layout(height=480, xaxis=dict(showgrid=False, tickangle=-45))
    return fig

def frequencia_ano_filtrada(df, nome_loja=None, tipo_loja=None, modo="valores"):
    df = df.copy()
    df["data_captura"] = pd.to_datetime(df["data_captura"], errors="coerce")
    df = df.dropna(subset=["data_captura"])

    def _norm(x): return str(x).strip().casefold()
    sufixo = ""
    if nome_loja and _norm(nome_loja) not in {"todas","all",""}:
        df = df[df["nome_loja"].astype(str).str.strip().str.casefold() == _norm(nome_loja)]
        sufixo = f" – {nome_loja}"
    elif tipo_loja and _norm(tipo_loja) not in {"todas","all",""}:
        df = df[df["tipo_loja"].astype(str).str.strip().str.casefold() == _norm(tipo_loja)]
        sufixo = f" – {tipo_loja}"

    if df.empty:
        return px.bar(title=f"Sem dados disponíveis{sufixo}")

    df["ano"] = df["data_captura"].dt.year
    g = (df.groupby("ano")["numero_celular"].nunique()
           .reset_index(name="valor").sort_values("ano"))
    total = g["valor"].sum()
    g["pct"] = (g["valor"] / total).fillna(0.0) if total > 0 else 0.0

    if modo.lower() == "percentual":
        fig = px.bar(g, x="ano", y="pct",
                     text=g["pct"].map(lambda x: f"{x:.1%}"),
                     color="pct", color_continuous_scale="Blues",
                     title=f"Frequência Anual de Capturas{sufixo}",
                     labels={"ano":"Anos","pct":"% do total"})
        fig.update_layout(height=480, xaxis=dict(showgrid=False), yaxis_tickformat=".0%")
        return fig

    text_series = g["valor"].astype(int).astype(str) if modo.lower() == "valores" \
                  else g.apply(lambda r: f'{int(r["valor"])}  ({r["pct"]:.1%})', axis=1)

    fig = px.bar(g, x="ano", y="valor",
                 text=text_series, color="valor", color_continuous_scale="Blues",
                 title=f"Frequência Anual de Capturas{sufixo}",
                 labels={"ano":"Anos","valor":"Capturas"})
    fig.update_layout(height=480, xaxis=dict(showgrid=False))
    return fig

def medias_frequencia_filtrada(df, mes, ano, nome_loja=None, tipo_loja=None):
    df = df.copy()
    df["data_captura"] = pd.to_datetime(df["data_captura"], errors="coerce")
    df = df.dropna(subset=["data_captura"])

    # --- filtro opcional por loja OU por tipo_loja (prioridade: nome_loja) ---
    def _norm(x): 
        return str(x).strip().casefold()

    if nome_loja is not None and _norm(nome_loja) not in {"todas", "all", ""}:
        alvo = _norm(nome_loja)
        df = df[df["nome_loja"].astype(str).str.strip().str.casefold() == alvo]
    elif tipo_loja is not None and _norm(tipo_loja) not in {"todas", "all", ""}:
        alvo = _norm(tipo_loja)
        df = df[df["tipo_loja"].astype(str).str.strip().str.casefold() == alvo]

    meses_pt = {
        1:"Janeiro",2:"Fevereiro",3:"Março",4:"Abril",5:"Maio",6:"Junho",
        7:"Julho",8:"Agosto",9:"Setembro",10:"Outubro",11:"Novembro",12:"Dezembro"
    }
    if isinstance(mes, str):
        mes_num = {v.lower(): k for k, v in meses_pt.items()}.get(mes.lower())
    else:
        mes_num = int(mes)

    # ------------------ MÉDIA DIÁRIA (mês/ano) ------------------
    df_ma = df[(df["data_captura"].dt.year == ano) & (df["data_captura"].dt.month == mes_num)]
    if df_ma.empty:
        media_diaria = 0.0
    else:
        primeiro_dia = pd.Timestamp(year=ano, month=mes_num, day=1)
        ultimo_dia = primeiro_dia + pd.offsets.MonthEnd(0)
        idx_dias = pd.date_range(primeiro_dia, ultimo_dia, freq="D")
        s_dia = (
            df_ma.groupby(df_ma["data_captura"].dt.date)["numero_celular"]
                 .nunique()
                 .reindex(idx_dias.date, fill_value=0)
        )
        media_diaria = float(s_dia.mean())

    # ------------------ MÉDIA SEMANAL (ano) ------------------
    df_ano = df[df["data_captura"].dt.year == ano]
    if df_ano.empty:
        media_semanal = 0.0
    else:
        inicio_ano = pd.Timestamp(year=ano, month=1, day=1)
        fim_ano = pd.Timestamp(year=ano, month=12, day=31)
        idx_sem = pd.date_range(inicio_ano, fim_ano, freq="W-SUN")
        s_sem = (
            df_ano.set_index("data_captura")
                  .groupby(pd.Grouper(freq="W-SUN"))["numero_celular"]
                  .nunique()
                  .reindex(idx_sem, fill_value=0)
        )
        media_semanal = float(s_sem.mean())

    # ------------------ MÉDIA MENSAL (ano) ------------------
    if df_ano.empty:
        media_mensal = 0.0
    else:
        s_mes = (
            df_ano.groupby(df_ano["data_captura"].dt.month)["numero_celular"]
                  .nunique()
                  .reindex(range(1, 13), fill_value=0)
        )
        media_mensal = float(s_mes.mean())

    # ------------------ MÉDIA ANUAL (toda base) ------------------
    s_ano = (
        df.groupby(df["data_captura"].dt.year)["numero_celular"]
          .nunique()
          .sort_index()
    )
    media_anual = float(s_ano.mean()) if not s_ano.empty else 0.0

    return {
        "media_diaria_mes_ano": media_diaria,
        "media_semanal_ano": media_semanal,
        "media_mensal_ano": media_mensal,
        "media_anual": media_anual
    }

