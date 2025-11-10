import streamlit as st
import pandas as pd
from datetime import datetime


import plotly.graph_objects as go
import matplotlib.figure as mpl_fig

# === IMPORTS DOS COMPONENTES ===
from components.aba_perfil_players.aba_perfil_players import render_aba_players
from components.aba_perfil_transacoes.aba_perfil_transacoes import render_aba_perfil_transacoes
from components.aba_perfil_cupons.aba_perfil_cupons import render_aba_perfil_cupons

from utils.report_export import construir_pdf_relatorio  # PDF
from utils.auto_download import trigger_download          # download automático
from api_client import get_all_json_df

import utils.thema_plotly

# =========================
# Configuração
# =========================
st.set_page_config(page_title="Dashboard – CEO", layout="wide")
st.title("Dashboard – CEO")

hide_menu_style = """
    <style>
    div[data-testid="stSidebarNav"] li:first-child {display: none;}
    </style>
"""
st.markdown(hide_menu_style, unsafe_allow_html=True)

# =========================
# Carga de bases (exemplo local; ajuste para API quando for integrar)
# =========================
CACHE_TTL = 3600  # 1 hora

@st.cache_data(show_spinner=False, ttl=CACHE_TTL)
def load_players():
    return get_all_json_df("/players", max_pages=None)

@st.cache_data(show_spinner=False, ttl=CACHE_TTL)
def load_lojas():
    return get_all_json_df("/lojas", max_pages=None)

@st.cache_data(show_spinner=False, ttl=CACHE_TTL)
def load_transacoes():
    return get_all_json_df("/transacoes", max_pages=None)

@st.cache_data(show_spinner=False, ttl=CACHE_TTL)
def load_simulacao():
    return get_all_json_df("/simulacao", max_pages=None)

def _safe(call, nome: str) -> pd.DataFrame:
    try:
        df = call()
        return df if isinstance(df, pd.DataFrame) else pd.DataFrame()
    except Exception as e:
        st.error(f"Erro ao carregar {nome}: {e}")
        return pd.DataFrame()

# ---------- Variáveis finais ----------
df_players    = _safe(load_players,    "players")
df_lojas      = _safe(load_lojas,      "lojas")
df_transacoes = _safe(load_transacoes, "transações")
df_simulacao  = _safe(load_simulacao,  "simulação")

# ---------- Forçar atualização ----------
if st.button("↻ Atualizar dados"):
    st.cache_data.clear()
    st.rerun()

# Garantir datetime nas bases que dependem de 'data'
for _df in (df_lojas, df_transacoes):
    if "data" in _df.columns:
        _df["data"] = pd.to_datetime(_df["data"], errors="coerce")
        _df.dropna(subset=["data"], inplace=True)
    else:
        st.error("Uma das bases não possui a coluna 'data'.")
        st.stop()

# =========================
# Filtros de período (sidebar)
# =========================
st.sidebar.markdown("### Filtros de período")
df_base = df_lojas.copy()
if df_base.empty:
    st.sidebar.error("Sem dados válidos em 'data' na base de lojas.")
    st.stop()

min_dt = df_base["data"].min().normalize()
max_dt = df_base["data"].max().normalize()

anos_disponiveis = sorted(df_base["data"].dt.year.unique().astype(int))
meses_pt = {1:"Janeiro",2:"Fevereiro",3:"Março",4:"Abril",5:"Maio",6:"Junho",
            7:"Julho",8:"Agosto",9:"Setembro",10:"Outubro",11:"Novembro",12:"Dezembro"}
mes_pt_to_int = {v:k for k, v in meses_pt.items()}

# Ano (intervalo)
if len(anos_disponiveis) == 1:
    ano_unico = int(anos_disponiveis[0])
    st.sidebar.markdown(f"**Ano (fixo – dados de teste):** {ano_unico}")
    anos_sel = (ano_unico, ano_unico)
else:
    anos_sel = st.sidebar.slider(
        "Ano (intervalo)",
        min_value=int(min(anos_disponiveis)),
        max_value=int(max(anos_disponiveis)),
        value=(int(min(anos_disponiveis)), int(max(anos_disponiveis))),
        step=1,
        key="ano_intervalo",
    )

# Meses dentro do range de anos
meses_no_range = (
    df_base[df_base["data"].dt.year.between(anos_sel[0], anos_sel[1])]
    ["data"].dt.month.unique()
)
meses_no_range = sorted([int(m) for m in (meses_no_range if len(meses_no_range) else range(1, 13))])
opcoes_meses_pt = [meses_pt[m] for m in meses_no_range]

# Mês (intervalo)
if len(set(meses_no_range)) <= 1 and meses_no_range:
    mes_unico_num = meses_no_range[0]
    st.sidebar.markdown(f"**Mês (fixo – dados de teste):** {meses_pt[mes_unico_num]}")
    meses_sel = (mes_unico_num, mes_unico_num)
else:
    meses_sel_pt = st.sidebar.select_slider(
        "Mês (intervalo)",
        options=opcoes_meses_pt,
        value=(opcoes_meses_pt[0], opcoes_meses_pt[-1]),
        key="mes_intervalo",
    )
    meses_sel = (mes_pt_to_int[meses_sel_pt[0]], mes_pt_to_int[meses_sel_pt[1]])

# Dia (intervalo)
datas_sel = st.sidebar.date_input(
    "Dia (intervalo)",
    value=(min_dt.date(), max_dt.date()),
    min_value=min_dt.date(),
    max_value=max_dt.date(),
    format="DD/MM/YYYY",
    key="dias_intervalo",
)
if isinstance(datas_sel, tuple):
    d_ini, d_fim = datas_sel
else:
    d_ini = datas_sel
    d_fim = datas_sel
if pd.to_datetime(d_ini) > pd.to_datetime(d_fim):
    d_ini, d_fim = d_fim, d_ini

# Modo de exibição
modo = st.sidebar.radio(
    "Exibir como:",
    ["Percentual", "Valores", "Ambos"],
    index=0
).lower()


# =========================
# Filtros de Loja/Categoria (sidebar)
# =========================
st.sidebar.markdown("---")
st.sidebar.markdown("### Filtros de Loja/Categoria")

opcoes_lojas = sorted(df_lojas["nome_estabelecimento"].dropna().unique()) if "nome_estabelecimento" in df_lojas.columns else []
opcoes_categ = sorted(df_lojas["categoria_estabelecimento"].dropna().unique()) if "categoria_estabelecimento" in df_lojas.columns else []

filtro_nome  = st.sidebar.multiselect("Lojas", opcoes_lojas, default=[])
filtro_categ = st.sidebar.multiselect("Categorias", opcoes_categ, default=[])

def _aplica_filtros_adicionais(df):
    dff = df.copy()
    if filtro_nome and "nome_estabelecimento" in dff.columns:
        dff = dff[dff["nome_estabelecimento"].isin(filtro_nome)]
    if filtro_categ and "categoria_estabelecimento" in dff.columns:
        dff = dff[dff["categoria_estabelecimento"].isin(filtro_categ)]
    return dff

# =========================
# MÁSCARAS DE PERÍODO/DATA
# =========================
mask_lojas = (
    df_lojas["data"].dt.year.between(anos_sel[0], anos_sel[1]) &
    df_lojas["data"].dt.month.between(meses_sel[0], meses_sel[1]) &
    df_lojas["data"].between(pd.to_datetime(d_ini), pd.to_datetime(d_fim))
)
df_lojas_filtrado = _aplica_filtros_adicionais(df_lojas.loc[mask_lojas].copy())

mask_trans = (
    df_transacoes["data"].dt.year.between(anos_sel[0], anos_sel[1]) &
    df_transacoes["data"].dt.month.between(meses_sel[0], meses_sel[1]) &
    df_transacoes["data"].between(pd.to_datetime(d_ini), pd.to_datetime(d_fim))
)
df_trans_filtrado = _aplica_filtros_adicionais(df_transacoes.loc[mask_trans].copy())

ano_escolhido = int(anos_sel[1])
mes_escolhido = int(meses_sel[1])

if len(anos_disponiveis) == 1 or len(set(meses_no_range)) <= 1:
    st.sidebar.caption(
        "Filtros exibidos em modo **fixo** por limitação da base de teste. "
        "No deploy oficial, os controles serão intervalares."
    )

# =========================
# ABAS
# =========================
aba1, aba2, aba3 = st.tabs(["Perfil dos Players", "Perfil Cupons", "Taxa de Retenção"])

with aba1:
    # Render normal
    render_aba_players(df_players)

    # Exportação (um botão que gera e baixa)
    st.subheader("Exportar relatório – Perfil dos Players")
    params_report = {
        "Perfil": "CEO",
        "Anos": f"{anos_sel[0]}–{anos_sel[1]}",
        "Meses": f"{meses_sel[0]}–{meses_sel[1]}",
        "Período": f"{pd.to_datetime(d_ini).date()} a {pd.to_datetime(d_fim).date()}",
        "Modo": modo,
        "Lojas": filtro_nome or ["(todas)"],
        "Categorias": filtro_categ or ["(todas)"],
    }
    if st.button("Gerar relatório (PDF) – Players"):
        figs = render_aba_players(df_players, export=True) or {}
        secoes = list(figs.items())
        pdf = construir_pdf_relatorio(
            titulo="Relatório – Perfil dos Players (CEO)",
            params=params_report,
            secoes=secoes,
            resumo_kpis=None,
            figs_per_page=6,  # 1 coluna (default no util), até 6 gráficos por página
            cols=1,
            cell_img_max_h_cm=8.5,
        )
        fname = f"relatorio_ceo_players_{datetime.now():%Y%m%d_%H%M}.pdf"
        trigger_download(pdf, fname)
        st.success("Relatório gerado e download iniciado.")

with aba2:
    # Render normal
    render_aba_perfil_cupons(
        df_filtrado=df_lojas_filtrado,
        ano_escolhido=ano_escolhido,
        mes_escolhido=mes_escolhido,
        modo=modo,
        filtro_nome=filtro_nome or None,
        filtro_tipo=filtro_categ or None,
    )

    # Exportação (um botão que gera e baixa)
    st.subheader("Exportar relatório – Perfil de Cupons/Capturas")
    params_report = {
        "Perfil": "CEO",
        "Anos": f"{anos_sel[0]}–{anos_sel[1]}",
        "Meses": f"{meses_sel[0]}–{meses_sel[1]}",
        "Período": f"{pd.to_datetime(d_ini).date()} a {pd.to_datetime(d_fim).date()}",
        "Modo": modo,
        "Lojas": filtro_nome or ["(todas)"],
        "Categorias": filtro_categ or ["(todas)"],
    }
    if st.button("Gerar relatório (PDF) – Cupons"):
        figs = render_aba_perfil_cupons(
            df_filtrado=df_lojas_filtrado,
            ano_escolhido=ano_escolhido,
            mes_escolhido=mes_escolhido,
            modo=modo,
            filtro_nome=filtro_nome or None,
            filtro_tipo=filtro_categ or None,
            export=True,
        ) or {}
        secoes = list(figs.items())
        pdf = construir_pdf_relatorio(
            titulo="Relatório – Perfil de Cupons (CEO)",
            params=params_report,
            secoes=secoes,
            resumo_kpis=None,
            figs_per_page=6,
            cols=1,
            cell_img_max_h_cm=8.5,
        )
        fname = f"relatorio_ceo_cupons_{datetime.now():%Y%m%d_%H%M}.pdf"
        trigger_download(pdf, fname)
        st.success("Relatório gerado e download iniciado.")

with aba3:
    # Render normal
    render_aba_perfil_transacoes(
        df_filtrado=df_trans_filtrado,
        ano_escolhido=ano_escolhido,
        mes_escolhido=mes_escolhido,
        modo=modo,
        filtro_nome=filtro_nome or None,
        filtro_tipo=filtro_categ or None,
    )

    # Exportação (um botão que gera e baixa)
    st.subheader("Exportar relatório – Taxa de Retenção")
    params_report = {
        "Perfil": "CEO",
        "Anos": f"{anos_sel[0]}–{anos_sel[1]}",
        "Meses": f"{meses_sel[0]}–{meses_sel[1]}",
        "Período": f"{pd.to_datetime(d_ini).date()} a {pd.to_datetime(d_fim).date()}",
        "Modo": "percentual (fixo no gráfico de defasagem)",
        "Lojas": filtro_nome or ["(todas)"],
        "Categorias": filtro_categ or ["(todas)"],
    }
    if st.button("Gerar relatório (PDF) – Retenção"):
        figs = render_aba_perfil_transacoes(
            df_filtrado=df_trans_filtrado,
            ano_escolhido=ano_escolhido,
            mes_escolhido=mes_escolhido,
            modo=modo,
            filtro_nome=filtro_nome or None,
            filtro_tipo=filtro_categ or None,
            export=True,
        ) or {}
        secoes = list(figs.items())
        pdf = construir_pdf_relatorio(
            titulo="Relatório – Taxa de Retenção (CEO)",
            params=params_report,
            secoes=secoes,
            resumo_kpis=None,
            figs_per_page=6,
            cols=1,
            cell_img_max_h_cm=8.5,
        )
        fname = f"relatorio_ceo_retencao_{datetime.now():%Y%m%d_%H%M}.pdf"
        trigger_download(pdf, fname)
        st.success("Relatório gerado e download iniciado.")
