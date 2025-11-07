import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st


@st.cache_data(show_spinner=False)
def load_data():
    """Carrega base_transacoes com tolerância a ; e latin1, e parse de data/hora."""
    df = None
    for kwargs in (
        {"sep": ","},
        {"sep": ";"},
        {"encoding": "latin1", "sep": ","},
        {"encoding": "latin1", "sep": ";"}
    ):
        try:
            df = pd.read_csv("base_de_dados/base_transacoes.csv", **kwargs)
            break
        except Exception:
            try:
                df = pd.read_csv("base_transacoes.csv", **kwargs)
                break
            except Exception:
                df = None
    if df is None:
        st.error("Não foi possível carregar base_transacoes.csv")
        st.stop()
    # parse datas/horas
    if "data" in df.columns:
        df["data"] = pd.to_datetime(df["data"], errors="coerce")
    if "hora" in df.columns:
        df["hora"] = pd.to_datetime(df["hora"], format="%H:%M:%S", errors="coerce").dt.hour
    return df

def kpi_cards(df):
    # escolhe a melhor coluna de valor disponível
    col_valor = None
    for c in ["valor", "valor_cupom", "gmv", "valor_total"]:
        if c in df.columns:
            col_valor = c
            break

    trans = len(df)
    gmv = df[col_valor].sum() if col_valor else np.nan
    ticket = (gmv / trans) if (col_valor and trans > 0) else np.nan
    pct_cupom = (df["id_cupom"].notna().mean()*100) if "id_cupom" in df.columns else np.nan

    c1, c2, c3, c4 = st.columns(4)
    fmt = lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    c1.metric("GMV (R$)", fmt(gmv) if col_valor else "—")
    c2.metric("Transações", f"{trans:,}".replace(",", "."))
    c3.metric("Ticket Médio (R$)", fmt(ticket) if col_valor else "—")
    c4.metric("% com Cupom", f"{pct_cupom:.1f}%" if not np.isnan(pct_cupom) else "—")


def line_timeseries(df):
    """Série temporal de transações com labels PT-BR e eixos capitalizados."""
    d = (
        df.assign(dia=df["data"].dt.date)
          .groupby("dia")
          .size()
          .reset_index(name="transacoes")
    )
    fig = px.line(
        d,
        x="dia",
        y="transacoes",
        markers=True,
        title="Transações por Dia",
        labels={"dia": "Data", "transacoes": "Transações"},
    )
    fig.update_layout(xaxis_title="Data", yaxis_title="Transações")
    st.plotly_chart(fig, use_container_width=True)

def bar_estabelecimento(df, top=15):
    """Ranking de estabelecimentos por número de transações (labels PT-BR)."""
    col = "nome_estabelecimento"
    if col not in df.columns:
        return
    d = (df.groupby(col)
           .size()
           .reset_index(name="transacoes")
           .sort_values("transacoes", ascending=False)
           .head(top))
    d["label"] = d["transacoes"]
    fig = px.bar(
        d,
        x="transacoes",
        y=col,
        orientation="h",
        text="label",
        title="Top Estabelecimentos",
        labels={"transacoes": "Transações", col: "Estabelecimento"},
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(xaxis_title="Transações", yaxis_title="Estabelecimento")
    st.plotly_chart(fig, use_container_width=True)

def heatmap_hora_semana(df):
    """Heatmap Dia da Semana x Hora (PT-BR, desaturado com quantis e paleta suave)."""
    if "hora" not in df.columns:
        return

    tmp = df.copy()
    dias_pt = ["Segunda-feira", "Terça-feira", "Quarta-feira",
               "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
    tmp["dow_num"] = tmp["data"].dt.dayofweek  # 0=Seg, 6=Dom
    tmp["dow"] = tmp["dow_num"].map(dict(enumerate(dias_pt)))

    piv = (tmp.pivot_table(index="dow", columns="hora", values="celular",
                           aggfunc="count", fill_value=0)
              .reindex(dias_pt))

    # clipping mais forte para reduzir saturação
    vmin = float(np.nanpercentile(piv.values, 10))
    vmax = float(np.nanpercentile(piv.values, 90))
    if vmin == vmax:  # evita range inválido
        vmin = piv.values.min()
        vmax = piv.values.max()

    # paleta mais clara (OrRd) e range fixo
    fig = px.imshow(
        piv,
        aspect="auto",
        title="Mapa de Calor: Dia da Semana x Hora",
        labels={"x": "Hora", "y": "Dia da Semana", "color": "Transações"},
        color_continuous_scale="OrRd",
        zmin=vmin, zmax=vmax,
    )

    # bordas finas nos quadrados ajudam a leitura
    fig.update_traces(xgap=1, ygap=1)

    # deixa a barra coerente com o clipping
    fig.update_layout(coloraxis_colorbar=dict(
        title="Transações",
        tickformat="d"
    ))

    st.plotly_chart(fig, use_container_width=True)
    
