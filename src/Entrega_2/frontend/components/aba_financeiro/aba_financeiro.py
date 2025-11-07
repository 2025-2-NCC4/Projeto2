import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

#  Helpers gerais 
def _to_num(df, cols):
    d = df.copy()
    for c in cols:
        if c in d.columns:
            d[c] = pd.to_numeric(d[c], errors="coerce")
    return d

def _fmt_br(x):
    try:
        return f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "—"

def _aplica_filtros(df, lojas=None, categorias=None):
    dff = df.copy()
    if lojas and "nome_estabelecimento" in dff.columns:
        dff = dff[dff["nome_estabelecimento"].isin(lojas)]
    if categorias and "categoria_estabelecimento" in dff.columns:
        dff = dff[dff["categoria_estabelecimento"].isin(categorias)]
    return dff

def _prep(df):
    d = df.copy()
    if "data" in d.columns:
        d["data"] = pd.to_datetime(d["data"], errors="coerce")
        d = d.dropna(subset=["data"])
    d = _to_num(d, ["valor_cupom", "repasse_picmoney"])
    d["lucro_bruto"] = d.get("valor_cupom", 0) - d.get("repasse_picmoney", 0)
    d["comissao_picmoney"] = np.where(
        d.get("valor_cupom", 0) > 0,
        d.get("repasse_picmoney", 0) / d.get("valor_cupom", 1),
        np.nan
    )
    return d

# KPIs 
def kpis_financeiro(df):
    """KPIs gerais (sem repetir os de repasse)."""
    receita = df["valor_cupom"].sum() if "valor_cupom" in df.columns else np.nan
    custo   = df["repasse_picmoney"].sum() if "repasse_picmoney" in df.columns else np.nan
    lucro   = df["lucro_bruto"].sum() if "lucro_bruto" in df.columns else (
        receita - custo if pd.notna(receita) and pd.notna(custo) else np.nan
    )
    margem  = (lucro/receita) if (pd.notna(lucro) and pd.notna(receita) and receita>0) else np.nan
    trans   = len(df)
    ticket  = (receita/trans) if (pd.notna(receita) and trans>0) else np.nan

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Receita Bruta (R$)", _fmt_br(receita) if pd.notna(receita) else "—")
    c2.metric("Custo PicMoney (R$)", _fmt_br(custo) if pd.notna(custo) else "—")
    c3.metric("Lucro Bruto (R$)", _fmt_br(lucro) if pd.notna(lucro) else "—")
    c4.metric("Margem Bruta (%)", f"{margem*100:.2f}%" if pd.notna(margem) else "—")
    c5.metric("Ticket Médio (R$)", _fmt_br(ticket) if pd.notna(ticket) else "—")
    c6.metric("Transações", f"{trans:,}".replace(",", "."))

#  Comparativos SEMANAIS 
def _col_receita_custo_lucro_semana(df):
    if "data" not in df.columns: return None
    d = df.copy()
    d["semana"] = d["data"].dt.to_period("W-MON").dt.start_time
    g = d.groupby("semana").agg(
        receita=("valor_cupom","sum"),
        custo=("repasse_picmoney","sum"),
        lucro=("lucro_bruto","sum")
    ).reset_index()
    g = g.melt(id_vars="semana", value_vars=["receita","custo","lucro"],
               var_name="Indicador", value_name="R$")
    fig = px.bar(
        g, x="semana", y="R$", color="Indicador", barmode="group",
        title="Receita × Custo × Lucro por Semana",
        labels={"semana":"Semana","R$":"R$"}
    )
    return fig

def _col_comissao_picmoney_semana(df):
    if "data" not in df.columns: return None
    d = df.copy()
    d["semana"] = d["data"].dt.to_period("W-MON").dt.start_time
    g = d.groupby("semana")["comissao_picmoney"].mean().reset_index()
    fig = px.bar(
        g, x="semana", y="comissao_picmoney",
        title="Comissão PicMoney Média por Semana (%)",
        labels={"semana":"Semana","comissao_picmoney":"%"}
    )
    fig.update_layout(yaxis_tickformat=".0%")
    return fig

#  Séries DIÁRIAS 
def _lin_receita_custo_lucro_diario(df):
    if "data" not in df.columns: return None
    d = df.copy()
    d["dia"] = d["data"].dt.to_period("D").dt.to_timestamp()
    g = d.groupby("dia").agg(
        receita=("valor_cupom","sum"),
        custo=("repasse_picmoney","sum"),
        lucro=("lucro_bruto","sum")
    ).reset_index()
    g = g.melt(id_vars="dia", value_vars=["receita","custo","lucro"],
               var_name="Indicador", value_name="R$")
    fig = px.line(
        g, x="dia", y="R$", color="Indicador", markers=True,
        title="Receita × Custo × Lucro por Dia",
        labels={"dia":"Dia","R$":"R$"}
    )
    return fig

def _lin_ticket_medio_diario(df):
    if "data" not in df.columns: return None
    d = df.copy()
    d["dia"] = d["data"].dt.to_period("D").dt.to_timestamp()
    g = d.groupby("dia").agg(
        receita=("valor_cupom","sum"),
        trans=("valor_cupom","size")
    ).reset_index()
    g["ticket_medio"] = np.where(g["trans"]>0, g["receita"]/g["trans"], np.nan)
    fig = px.line(
        g, x="dia", y="ticket_medio", markers=True,
        title="Ticket Médio por Dia (R$)",
        labels={"dia":"Dia","ticket_medio":"R$"}
    )
    return fig

def _lin_transacoes_diario(df):
    if "data" not in df.columns: return None
    d = df.copy()
    d["dia"] = d["data"].dt.to_period("D").dt.to_timestamp()
    g = d.groupby("dia")["valor_cupom"].size().reset_index(name="transacoes")
    fig = px.line(
        g, x="dia", y="transacoes", markers=True,
        title="Transações por Dia",
        labels={"dia":"Dia","transacoes":"Transações"}
    )
    return fig

#  Receita por Dia da Semana 
def _col_receita_dia_semana(df):
    if "data" not in df.columns or "valor_cupom" not in df.columns: return None
    d = df.copy()
    d["dow"] = d["data"].dt.dayofweek  # 0=Seg ... 6=Dom
    mapa = {0:"Segunda",1:"Terça",2:"Quarta",3:"Quinta",4:"Sexta",5:"Sábado",6:"Domingo"}
    g = d.groupby("dow")["valor_cupom"].sum().reset_index()
    g["dia_semana"] = g["dow"].map(mapa)
    ordem = ["Segunda","Terça","Quarta","Quinta","Sexta","Sábado","Domingo"]
    g = g.sort_values("dow")
    g["Label"] = g["valor_cupom"].map(_fmt_br)
    fig = px.bar(
        g, x="dia_semana", y="valor_cupom", text="Label",
        title="Receita por Dia da Semana (R$)",
        labels={"dia_semana":"Dia da Semana","valor_cupom":"R$"},
        category_orders={"dia_semana": ordem}
    )
    fig.update_traces(textposition="outside")
    return fig

#  Render da aba 
def render_aba_financeiro(df_filtrado: pd.DataFrame, lojas=None, categorias=None):
    """Aba Financeiro: KPIs + semanais em colunas + séries diárias + receita por DOW."""
    dff = _aplica_filtros(df_filtrado, lojas, categorias)
    dff = _prep(dff)

    st.subheader("KPIs Financeiros")
    kpis_financeiro(dff)

    # Visão por Semana 
    st.markdown("### Visão Semanal")
    c1, c2 = st.columns(2)
    with c1:
        fig = _col_receita_custo_lucro_semana(dff)
        if fig: st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = _col_comissao_picmoney_semana(dff)
        if fig: st.plotly_chart(fig, use_container_width=True)

    # Séries diárias 
    st.markdown("### Séries Diárias")
    d1, d2 = st.columns(2)
    with d1:
        fig = _lin_receita_custo_lucro_diario(dff)
        if fig: st.plotly_chart(fig, use_container_width=True)
    with d2:
        fig = _lin_ticket_medio_diario(dff)
        if fig: st.plotly_chart(fig, use_container_width=True)

    fig = _lin_transacoes_diario(dff)
    if fig: st.plotly_chart(fig, use_container_width=True)

    # Margem por loja e participação do lucro por categoria 
    st.markdown("### Rentabilidade por Loja e Categoria")
    r1, r2 = st.columns(2)
    with r1:
        fig = _col_margem_media_por_loja(dff, top=15, min_receita=10000)
        if fig: st.plotly_chart(fig, use_container_width=True)
    with r2:
        fig = _col_participacao_lucro_por_categoria(dff, min_lucro=0)
        if fig: st.plotly_chart(fig, use_container_width=True)


    # Receita por Dia da Semana 
    st.markdown("### Distribuição Semanal")
    fig = _col_receita_dia_semana(dff)
    if fig: st.plotly_chart(fig, use_container_width=True)

def _col_margem_media_por_loja(df, top=15, min_receita=10000):
    """
    Margem média por loja = sum(lucro_bruto) / sum(valor_cupom).
    Usa ponderação pela receita (evita distorção de média simples).
    Filtra lojas com receita mínima para reduzir ruído.
    """
    req = {"nome_estabelecimento", "valor_cupom", "lucro_bruto"}
    if not req.issubset(df.columns): 
        return None

    g = (df.groupby("nome_estabelecimento")
           .agg(receita=("valor_cupom","sum"),
                lucro=("lucro_bruto","sum"))
           .reset_index())
    g = g[g["receita"] >= min_receita].copy()
    if g.empty:
        return None

    g["margem"] = np.where(g["receita"] > 0, g["lucro"] / g["receita"], np.nan)
    g = g.dropna(subset=["margem"]).sort_values("margem", ascending=False).head(top)
    g["pct_label"] = (g["margem"]*100).round(2).astype(str) + "%"

    fig = px.bar(
        g, x="nome_estabelecimento", y="margem", text="pct_label",
        title="Margem Média por Loja (%)",
        labels={"nome_estabelecimento": "Estabelecimento", "margem": "%"}
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(yaxis_tickformat=".0%")
    return fig


def _col_participacao_lucro_por_categoria(df, min_lucro=0):
    """
    Participação de cada categoria no lucro bruto total.
    Mostra % do lucro total por 'categoria_estabelecimento'.
    """
    req = {"categoria_estabelecimento", "lucro_bruto"}
    if not req.issubset(df.columns):
        return None

    g = (df.groupby("categoria_estabelecimento")["lucro_bruto"]
           .sum().reset_index().rename(columns={"lucro_bruto":"lucro"}))
    g = g[g["lucro"] > min_lucro].copy()
    if g.empty:
        return None

    total = g["lucro"].sum()
    if total <= 0:
        return None

    g["participacao"] = g["lucro"] / total
    g = g.sort_values("participacao", ascending=False)
    g["pct_label"] = (g["participacao"]*100).round(2).astype(str) + "%"

    fig = px.bar(
        g, x="categoria_estabelecimento", y="participacao", text="pct_label",
        title="Participação no Lucro Bruto por Categoria (%)",
        labels={"categoria_estabelecimento": "Categoria", "participacao": "%"}
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(yaxis_tickformat=".0%")
    return fig
