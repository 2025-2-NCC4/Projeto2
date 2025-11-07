import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# ---------- Config da página ----------
st.set_page_config(page_title="Dashboard – CFO", layout="wide")
st.title("Dashboard – CFO")

# ---------- Permitir import de components/charts quando rodar de /pages ----------
HERE = Path(__file__).resolve()
PROJECT_ROOT = HERE.parent.parent  
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from components.aba_financeiro.aba_financeiro import render_aba_financeiro
from components.aba_repasse.aba_repasse import render_aba_repasse
from components.aba_liquidez.aba_liquidez import render_aba_liquidez

# =========================
# Carga das bases 
# =========================
df = None
for p in ("base_de_dados/base_transacoes.csv", "base_transacoes.csv"):
    try:
        df = pd.read_csv(p)
        break
    except Exception:
        pass

if df is None:
    st.error("Não foi possível carregar 'base_transacoes.csv'.")
    st.stop()

# ---------- Normalizações para garantir filtros ----------
# normaliza nomes e chaves
df.columns = [c.strip().lower() for c in df.columns]
if "nome_estabelecimento" in df.columns:
    df["nome_estabelecimento"] = df["nome_estabelecimento"].astype(str).str.strip()

# datas coerentes
if "data" not in df.columns:
    st.error("A base de transações não possui a coluna 'data'.")
    st.stop()
df["data"] = pd.to_datetime(df["data"], errors="coerce")
df.dropna(subset=["data"], inplace=True)

# harmoniza a coluna de categoria em 'categoria_estabelecimento'
if "categoria_estabelecimento" not in df.columns:
    for alt in ("categoria", "categoria_loja", "categoria_estab", "cat"):
        if alt in df.columns:
            df["categoria_estabelecimento"] = df[alt]
            break

# =========================
# Filtros de período (sidebar)
# =========================
st.sidebar.markdown("### Filtros de período")

df_base = df.copy()
df_base["data"] = pd.to_datetime(df_base["data"], errors="coerce")
df_base = df_base.dropna(subset=["data"])
min_dt = df_base["data"].min().normalize()
max_dt = df_base["data"].max().normalize()

anos_disponiveis = sorted(df_base["data"].dt.year.unique().astype(int))

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

# Mês dentro do range de anos
meses_no_range = (
    df_base[df_base["data"].dt.year.between(anos_sel[0], anos_sel[1])]
    ["data"].dt.month.unique()
)
meses_no_range = sorted([int(m) for m in (meses_no_range or list(range(1, 13)))])
opcoes_meses_pt = [meses_pt[m] for m in meses_no_range] if meses_no_range else list(meses_pt.values())

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

# Normaliza datas (aceita único dia)
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

# ---------- Filtros adicionais ----------
st.sidebar.markdown("---")
st.sidebar.markdown("### Filtros de Loja/Categoria")

lojas = sorted(df["nome_estabelecimento"].dropna().astype(str).str.strip().unique()) if "nome_estabelecimento" in df.columns else []
# tenta popular categorias de forma robusta
categorias = []
if "categoria_estabelecimento" in df.columns:
    categorias = sorted(df["categoria_estabelecimento"].dropna().astype(str).str.strip().unique())

filtro_lojas = st.sidebar.multiselect("Lojas", lojas, default=[])
filtro_cat   = st.sidebar.multiselect("Categorias", categorias, default=[])

# ---------- Aplica máscara robusta ----------
mask = (
    df["data"].dt.year.between(anos_sel[0], anos_sel[1]) &
    df["data"].dt.month.between(meses_sel[0], meses_sel[1]) &
    df["data"].dt.normalize().between(d_ini, d_fim)
)
df_filtrado = df.loc[mask].copy()
if filtro_lojas:
    df_filtrado = df_filtrado[df_filtrado["nome_estabelecimento"].astype(str).str.strip().isin(filtro_lojas)]
if filtro_cat and "categoria_estabelecimento" in df_filtrado.columns:
    df_filtrado = df_filtrado[df_filtrado["categoria_estabelecimento"].astype(str).str.strip().isin(filtro_cat)]

# ---------- Abas (Financeiro primeiro) ----------
tab1, tab2, tab3 = st.tabs(["Financeiro", "Repasse", "Liquidez"])

with tab1:
    render_aba_financeiro(df_filtrado, lojas=filtro_lojas or None, categorias=filtro_cat or None)

with tab2:
    render_aba_repasse(df_filtrado, lojas=filtro_lojas or None, categorias=filtro_cat or None)

with tab3:
    render_aba_liquidez(df_filtrado, lojas=filtro_lojas or None, categorias=filtro_cat or None)