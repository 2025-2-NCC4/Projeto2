# pages/1_CEO.py
import streamlit as st
import pandas as pd
from components.aba_players import render_aba_players
from components.aba_lojas import render_aba_lojas

# =========================
# Configuração
# =========================
st.set_page_config(page_title="Dashboard – CEO", layout="wide")
st.title("Dashboard – CEO")

# =========================
# Carga de bases (exemplo local; ajuste para API quando for integrar)
# =========================
df_players    = pd.read_csv(r"base_de_dados\base_players.csv", sep=",")
df_lojas      = pd.read_csv(r"base_de_dados\base_lojas.csv", sep=",")
df_transacoes = pd.read_csv(r"base_de_dados\base_transacoes.csv", sep=",")
df_simulacao  = pd.read_csv(r"base_de_dados\base_simulacao.csv", sep=",")

# Garantir datetime
if "data" in df_lojas.columns:
    df_lojas["data"] = pd.to_datetime(df_lojas["data"], errors="coerce")
    df_lojas = df_lojas.dropna(subset=["data"])
else:
    st.error("A base de lojas não possui a coluna 'data'.")
    st.stop()

# =========================
# Filtros (período e lojas) — iguais ao original
# =========================
st.sidebar.markdown("### Filtros de período")

df_base = df_lojas.copy()
df_base["data"] = pd.to_datetime(df_base["data"], errors="coerce")
df_base = df_base.dropna(subset=["data"])
if df_base.empty:
    st.sidebar.error("Sem dados válidos em 'data'.")
    st.stop()

min_dt = df_base["data"].min().normalize()
max_dt = df_base["data"].max().normalize()

anos_disponiveis = sorted(df_base["data"].dt.year.unique().astype(int))
meses_disponiveis = sorted(df_base["data"].dt.month.unique().astype(int))
meses_pt = {1:"Janeiro",2:"Fevereiro",3:"Março",4:"Abril",5:"Maio",6:"Junho",
            7:"Julho",8:"Agosto",9:"Setembro",10:"Outubro",11:"Novembro",12:"Dezembro"}
mes_pt_to_int = {v:k for k, v in meses_pt.items()}

# Ano
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

# Mês dentro do range de anos
meses_no_range = (
    df_base[df_base["data"].dt.year.between(anos_sel[0], anos_sel[1])]
    ["data"].dt.month.unique()
)
meses_no_range = sorted([int(m) for m in meses_no_range])
opcoes_meses_pt = [meses_pt[m] for m in (meses_no_range or list(range(1, 13)))]

if len(set(meses_no_range)) <= 1:
    mes_unico_num = meses_no_range[0] if meses_no_range else min(meses_disponiveis or [7])
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

# Dia (intervalo de datas)
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

# Modo
modo = st.sidebar.selectbox("Exibir como:", ["Valores", "Percentual", "Ambos"], index=0).lower()

# Máscara final + escolha de ano/mês para funções
mask = df_base["data"].dt.year.between(anos_sel[0], anos_sel[1])
mask &= df_base["data"].dt.month.between(meses_sel[0], meses_sel[1])
mask &= df_base["data"].between(pd.to_datetime(d_ini), pd.to_datetime(d_fim))
df_filtrado = df_base.loc[mask].copy()

ano_escolhido = int(anos_sel[1])
mes_escolhido = int(meses_sel[1])

if len(anos_disponiveis) == 1 or len(set(meses_no_range)) <= 1:
    st.sidebar.caption(
        "Filtros exibidos em modo **fixo** por limitação da base de teste. "
        "No deploy oficial, os controles serão intervalares."
    )

# Filtros de Loja/Categoria
st.sidebar.markdown("---")
st.sidebar.markdown("### Filtros de Loja/Categoria")
opcoes_lojas = sorted(df_base["nome_estabelecimento"].dropna().unique()) if "nome_estabelecimento" in df_base.columns else []
opcoes_categ = sorted(df_base["categoria_estabelecimento"].dropna().unique()) if "categoria_estabelecimento" in df_base.columns else []


filtro_nome = st.sidebar.multiselect("Lojas", opcoes_lojas, default=[])
filtro_categ = st.sidebar.multiselect("Categorias", opcoes_categ, default=[])

def _aplica_filtros_adicionais(df):
    dff = df.copy()
    if filtro_nome and "nome_estabelecimento" in dff.columns:
        dff = dff[dff["nome_estabelecimento"].isin(filtro_nome)]
    if filtro_categ and "categoria_estabelecimento" in dff.columns:
        dff = dff[dff["categoria_estabelecimento"].isin(filtro_categ)]
    if filtro_categ and "categoria_estabelecimento" in dff.columns:
        dff = dff[dff["categoria_estabelecimento"].isin(filtro_categ)]
    return dff

df_filtrado = _aplica_filtros_adicionais(df_filtrado)

# =========================
# TABS → chama componentes
# =========================
aba1, aba2 = st.tabs(["Perfil dos Players", "Perfil das Lojas"])

with aba1:
    render_aba_players(df_players)

with aba2:
    render_aba_lojas(
        df_filtrado=df_filtrado,
        ano_escolhido=ano_escolhido,
        mes_escolhido=mes_escolhido,
        modo=modo,
        filtro_nome=filtro_nome or None,
        filtro_categ=filtro_categ or None,
    )
