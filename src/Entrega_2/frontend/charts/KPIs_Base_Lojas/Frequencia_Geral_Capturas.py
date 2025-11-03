import pandas as pd
import numpy as np
import plotly.express as px



def frequencia_diaria(df, mes, ano):
    df = df.copy()
    df["data_captura"] = pd.to_datetime(df["data_captura"], errors="coerce")
    df = df.dropna(subset=["data_captura"])

    meses_pt = {
        1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
        5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
        9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
    }

    # Permitir nome ou número do mês
    if isinstance(mes, str):
        mes_num = {v.lower(): k for k, v in meses_pt.items()}.get(mes.lower())
    else:
        mes_num = int(mes)

    if mes_num not in range(1, 13):
        return px.bar(title=f"Mês inválido: {mes}")

    df = df[(df["data_captura"].dt.year == ano) & (df["data_captura"].dt.month == mes_num)]

    if df.empty:
        return px.bar(title=f"Sem dados para {meses_pt[mes_num]} {ano}")

    s = (
        df.groupby("data_captura")["numero_celular"]
        .nunique()
        .reset_index(name="usuarios_unicos")
        .sort_values("data_captura")
    )
    s["dia"] = s["data_captura"].dt.day

    fig = px.bar(
        data_frame=s,
        x="dia",
        y="usuarios_unicos",
        text_auto=True,
        color="usuarios_unicos",
        color_continuous_scale="Blues",
        title=f"Frequência Diária de Captura - {meses_pt[mes_num]} {ano}",
        labels={"dia": "Dias", "usuarios_unicos": "Capturas"},
    )

    fig.update_layout(height=500, xaxis=dict(tickmode="linear", tick0=1, dtick=1))
    return fig

def frequencia_semanal(df, ano):
    df = df.copy()
    df["data_captura"] = pd.to_datetime(df["data_captura"], errors="coerce")
    df = df.dropna(subset=["data_captura"])
    df = df[df["data_captura"].dt.year == ano]

    df["semana"] = df["data_captura"].dt.isocalendar().week
    semanal = df.groupby("semana")["numero_celular"].nunique().reset_index(name="usuarios_unicos")

    semanas_ano = pd.DataFrame({"semana": range(1, 54)})
    semanal = semanas_ano.merge(semanal, on="semana", how="left").fillna(0)
    semanal["usuarios_unicos"] = semanal["usuarios_unicos"].astype(int)
    semanal["semana_label"] = semanal["semana"].apply(lambda x: f"Semana {x}")

    fig = px.bar(
        semanal,
        x="semana_label",
        y="usuarios_unicos",
        text_auto=True,
        color="usuarios_unicos",
        color_continuous_scale="Blues",
        title=f"Frequência Semanal de Capturas – {ano}",
        labels={"semana_label": "Semanas", "usuarios_unicos": "Capturas"},
    )

    fig.update_layout(
        height=480,
        xaxis=dict(showgrid=False, tickangle=-45),
        yaxis_title="Capturas",
    )
    return fig

def frequencia_mensal(df, ano):
    df = df.copy()
    df["data_captura"] = pd.to_datetime(df["data_captura"], errors="coerce")
    df = df.dropna(subset=["data_captura"])
    df = df[df["data_captura"].dt.year == ano]

    if df.empty:
        return px.bar(title=f"Sem dados disponíveis para {ano}")

    meses_pt = {
        1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
        5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
        9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
    }

    # Agrupar usuários únicos por mês
    df["mes_num"] = df["data_captura"].dt.month
    mensal = (
        df.groupby("mes_num")["numero_celular"]
        .nunique()
        .reset_index(name="usuarios_unicos")
    )

    # Garantir que todos os 12 meses apareçam
    base_meses = pd.DataFrame({"mes_num": range(1, 13)})
    mensal = base_meses.merge(mensal, on="mes_num", how="left").fillna(0)
    mensal["usuarios_unicos"] = mensal["usuarios_unicos"].astype(int)
    mensal["mes_label"] = mensal["mes_num"].map(meses_pt)

    fig = px.bar(
        mensal,
        x="mes_label",
        y="usuarios_unicos",
        text_auto=True,
        color="usuarios_unicos",
        color_continuous_scale="Blues",
        title=f"Frequência Mensal de Captura – {ano}",
        labels={"mes_label": "Meses", "usuarios_unicos": "Capturas"},
    )

    fig.update_layout(height=480, xaxis=dict(showgrid=False, tickangle=-45))
    return fig

def frequencia_ano(df):
    df = df.copy()
    df["data_captura"] = pd.to_datetime(df["data_captura"], errors="coerce")
    df = df.dropna(subset=["data_captura"])

    if df.empty:
        return px.bar(title="Sem dados disponíveis na base")

    # Agrupar usuários únicos por ano
    df["ano"] = df["data_captura"].dt.year
    anual = (
        df.groupby("ano")["numero_celular"]
        .nunique()
        .reset_index(name="usuarios_unicos")
        .sort_values("ano")
    )

    fig = px.bar(
        anual,
        x="ano",
        y="usuarios_unicos",
        text_auto=True,
        color="usuarios_unicos",
        color_continuous_scale="Blues",
        title="Frequência Anual de Capturas",
        labels={"ano": "Anos", "usuarios_unicos": "Capturas"},
    )

    fig.update_layout(
        height=480,
        xaxis=dict(showgrid=False),
        yaxis_title="Capturas"
    )

    return fig

def medias_frequencia(df, mes, ano):
    df = df.copy()
    df["data_captura"] = pd.to_datetime(df["data_captura"], errors="coerce")
    df = df.dropna(subset=["data_captura"])

    meses_pt = {
        1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
        5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
        9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
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
        primeiro_dia = df_ma["data_captura"].min().replace(day=1)
        ultimo_dia = (primeiro_dia + pd.offsets.MonthEnd(0))
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
        inicio_ano = df_ano["data_captura"].min().replace(month=1, day=1)
        fim_ano = df_ano["data_captura"].max().replace(month=12, day=31)
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

