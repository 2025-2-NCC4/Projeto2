import streamlit as st
import pandas as pd
from datetime import datetime

import utils.thema_plotly

# --- Tipos de figuras suportadas + helper de debug/filtragem ---
from typing import Dict, Any, List, Tuple
try:
    import plotly.graph_objects as go
except Exception:
    go = None
try:
    import matplotlib.figure as mpl_fig
except Exception:
    mpl_fig = None

def _debug_e_filtrar_figs(figs: Dict[str, Any]) -> List[Tuple[str, Any]]:
    """Mostra os tipos no app e retorna apenas (titulo, figura) suportados."""
    tipos = {t: (type(f).__name__ if f is not None else "NoneType") for t, f in (figs or {}).items()}
    with st.expander("DEBUG: tipos retornados pelas funções de aba", expanded=False):
        st.json(tipos)

    secoes: List[Tuple[str, Any]] = []
    for t, f in (figs or {}).items():
        if (go is not None and isinstance(f, go.Figure)) or (mpl_fig is not None and isinstance(f, mpl_fig.Figure)):
            secoes.append((t, f))
    if not secoes:
        st.warning("Nenhuma figura válida retornada (Plotly ou Matplotlib). Verifique a função da aba quando export=True.")
    return secoes

from components.aba_financeiro.aba_financeiro import render_aba_financeiro
from components.aba_repasse.aba_repasse import render_aba_repasse
from components.aba_liquidez.aba_liquidez import render_aba_liquidez

from utils.report_export import construir_pdf_relatorio  # PDF
from utils.auto_download import trigger_download          # download automático
from api_client import get_all_json_df

# ---------- Config da página ----------
st.set_page_config(page_title="Dashboard – CFO", layout="wide")
st.title("Dashboard - CFO")

hide_menu_style = """
    <style>
    div[data-testid="stSidebarNav"] li:first-child {display: none;}
    </style>
"""
st.markdown(hide_menu_style, unsafe_allow_html=True)

# =========================
# Carga de bases via API (cacheadas)
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

# ---------- Botão para forçar atualização ----------
if st.button("↻ Atualizar dados"):
    st.cache_data.clear()
    st.rerun()

# =====================================================
# Base de trabalho do CFO: transações
# =====================================================
df = df_transacoes.copy()

if df.empty:
    st.warning("Não há dados em **transações** para exibir.")
    st.stop()

# ---------- Normalizações básicas ----------
df.columns = [str(c).strip().lower() for c in df.columns]

if "nome_estabelecimento" in df.columns:
    df["nome_estabelecimento"] = df["nome_estabelecimento"].astype(str).str.strip()

if "data" not in df.columns:
    st.error("A base de transações não possui a coluna obrigatória **'data'**.")
    st.stop()

df["data"] = pd.to_datetime(df["data"], errors="coerce")
df.dropna(subset=["data"], inplace=True)
if df.empty:
    st.warning("Após normalização de datas, não restaram linhas válidas.")
    st.stop()

if "categoria_estabelecimento" not in df.columns:
    for alt in ("categoria", "categoria_loja", "categoria_estab", "cat"):
        if alt in df.columns:
            df["categoria_estabelecimento"] = df[alt].astype(str).str.strip()
            break

# =====================================================
# Filtros (sidebar)
# =====================================================
st.sidebar.markdown("### Filtros de período")

min_dt = df["data"].min().normalize()
max_dt = df["data"].max().normalize()

anos_disponiveis = sorted(df["data"].dt.year.dropna().astype(int).unique())
if not anos_disponiveis:
    st.warning("Não há anos disponíveis na coluna 'data'.")
    st.stop()

meses_pt = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}
mes_pt_to_int = {v: k for k, v in meses_pt.items()}

# Ano (intervalo)
if len(anos_disponiveis) == 1:
    ano_unico = int(anos_disponiveis[0])
    st.sidebar.markdown(f"**Ano (fixo):** {ano_unico}")
    anos_sel = (ano_unico, ano_unico)
else:
    anos_sel = st.sidebar.slider(
        "Ano (intervalo)",
        min_value=int(min(anos_disponiveis)),
        max_value=int(max(anos_disponiveis)),
        value=(int(min(anos_disponiveis)), int(max(anos_disponiveis))),
        step=1,
        key="ano_intervalo_cfo",
    )

# Meses do range
meses_no_range = (
    df[df["data"].dt.year.between(anos_sel[0], anos_sel[1])]["data"].dt.month.unique()
)
meses_no_range = sorted([int(m) for m in (meses_no_range if len(meses_no_range) else range(1, 13))])
opcoes_meses_pt = [meses_pt[m] for m in meses_no_range]

# Mês (intervalo)
if len(set(meses_no_range)) <= 1 and meses_no_range:
    mes_unico_num = meses_no_range[0]
    st.sidebar.markdown(f"**Mês (fixo):** {meses_pt[mes_unico_num]}")
    meses_sel = (mes_unico_num, mes_unico_num)
else:
    meses_sel_pt = st.sidebar.select_slider(
        "Mês (intervalo)",
        options=opcoes_meses_pt,
        value=(opcoes_meses_pt[0], opcoes_meses_pt[-1]),
        key="mes_intervalo_cfo",
    )
    meses_sel = (mes_pt_to_int[meses_sel_pt[0]], mes_pt_to_int[meses_sel_pt[1]])

# Dia (intervalo)
datas_sel = st.sidebar.date_input(
    "Dia (intervalo)",
    value=(min_dt.date(), max_dt.date()),
    min_value=min_dt.date(),
    max_value=max_dt.date(),
    format="DD/MM/YYYY",
    key="dias_intervalo_cfo",
)

if isinstance(datas_sel, (tuple, list)):
    if len(datas_sel) == 2:
        d_ini, d_fim = datas_sel
    elif len(datas_sel) == 1:
        d_ini, d_fim = datas_sel[0], datas_sel[0]
    else:
        d_ini, d_fim = min_dt.date(), max_dt.date()
else:
    d_ini, d_fim = datas_sel, datas_sel

d_ini = pd.to_datetime(d_ini).normalize()
d_fim = pd.to_datetime(d_fim).normalize()
if d_ini > d_fim:
    d_ini, d_fim = d_fim, d_ini

# Filtros adicionais
st.sidebar.markdown("---")
st.sidebar.markdown("### Filtros de Loja/Categoria")

lojas = sorted(df["nome_estabelecimento"].dropna().astype(str).str.strip().unique()) if "nome_estabelecimento" in df.columns else []
categorias = sorted(df["categoria_estabelecimento"].dropna().astype(str).str.strip().unique()) if "categoria_estabelecimento" in df.columns else []

filtro_lojas = st.sidebar.multiselect("Lojas", lojas, default=[])
filtro_cat   = st.sidebar.multiselect("Categorias", categorias, default=[])

# Aplica máscara
mask = (
    df["data"].dt.year.between(anos_sel[0], anos_sel[1]) &
    df["data"].dt.month.between(meses_sel[0], meses_sel[1]) &
    df["data"].dt.normalize().between(d_ini, d_fim)
)
df_filtrado = df.loc[mask].copy()

if filtro_lojas and "nome_estabelecimento" in df_filtrado.columns:
    df_filtrado = df_filtrado[
        df_filtrado["nome_estabelecimento"].astype(str).str.strip().isin(filtro_lojas)
    ]

if filtro_cat and "categoria_estabelecimento" in df_filtrado.columns:
    df_filtrado = df_filtrado[
        df_filtrado["categoria_estabelecimento"].astype(str).str.strip().isin(filtro_cat)
    ]

if df_filtrado.empty:
    st.info("Nenhum dado encontrado para os filtros selecionados.")

# =====================================================
# Abas principais
# =====================================================
tab1, tab2, tab3 = st.tabs(["Financeiro", "Repasse", "Liquidez"])

# ---------- parâmetros comuns para o PDF ----------
params_base = {
    "Perfil": "CFO",
    "Anos": f"{anos_sel[0]}–{anos_sel[1]}",
    "Meses": f"{meses_sel[0]}–{meses_sel[1]}",
    "Período": f"{pd.to_datetime(d_ini).date()} a {pd.to_datetime(d_fim).date()}",
    "Lojas": filtro_lojas or ["(todas)"],
    "Categorias": filtro_cat or ["(todas)"],
}

with tab1:
    # Render normal
    render_aba_financeiro(df_filtrado, lojas=filtro_lojas or None, categorias=filtro_cat or None)

    # Exportação (um botão que gera e baixa)
    st.subheader("Exportar relatório – Financeiro")
    if st.button("Gerar relatório (PDF) – Financeiro"):
        figs = render_aba_financeiro(
            df_filtrado,
            lojas=filtro_lojas or None,
            categorias=filtro_cat or None,
            export=True
        ) or {}
        secoes = _debug_e_filtrar_figs(figs)
        pdf = construir_pdf_relatorio(
            titulo="Relatório – Financeiro (CFO)",
            params=params_base,
            secoes=secoes,
            resumo_kpis=None,
            figs_per_page=6,
            cols=1,
            cell_img_max_h_cm=8.5,
        )
        fname = f"relatorio_cfo_financeiro_{datetime.now():%Y%m%d_%H%M}.pdf"
        trigger_download(pdf, fname)
        st.success("Relatório gerado e download iniciado.")

with tab2:
    # Render normal
    render_aba_repasse(df_filtrado, lojas=filtro_lojas or None, categorias=filtro_cat or None)

    # Exportação (um botão que gera e baixa)
    st.subheader("Exportar relatório – Repasse")
    if st.button("Gerar relatório (PDF) – Repasse"):
        figs = render_aba_repasse(
            df_filtrado,
            lojas=filtro_lojas or None,
            categorias=filtro_cat or None,
            export=True
        ) or {}
        secoes = _debug_e_filtrar_figs(figs)
        pdf = construir_pdf_relatorio(
            titulo="Relatório – Repasse (CFO)",
            params=params_base,
            secoes=secoes,
            resumo_kpis=None,
            figs_per_page=6,
            cols=1,
            cell_img_max_h_cm=8.5,
        )
        fname = f"relatorio_cfo_repasse_{datetime.now():%Y%m%d_%H%M}.pdf"
        trigger_download(pdf, fname)
        st.success("Relatório gerado e download iniciado.")

with tab3:
    # Render normal
    render_aba_liquidez(df_filtrado, lojas=filtro_lojas or None, categorias=filtro_cat or None)

    # Exportação (um botão que gera e baixa)
    st.subheader("Exportar relatório – Liquidez")
    if st.button("Gerar relatório (PDF) – Liquidez"):
        figs = render_aba_liquidez(
            df_filtrado,
            lojas=filtro_lojas or None,
            categorias=filtro_cat or None,
            export=True
        ) or {}
        secoes = _debug_e_filtrar_figs(figs)
        pdf = construir_pdf_relatorio(
            titulo="Relatório – Liquidez (CFO)",
            params=params_base,
            secoes=secoes,
            resumo_kpis=None,
            figs_per_page=6,
            cols=1,
            cell_img_max_h_cm=8.5,
        )
        fname = f"relatorio_cfo_liquidez_{datetime.now():%Y%m%d_%H%M}.pdf"
        trigger_download(pdf, fname)
        st.success("Relatório gerado e download iniciado.")
