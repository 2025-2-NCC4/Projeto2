# pages/1_CEO.py
import streamlit as st
import pandas as pd

# === IMPORTS DOS COMPONENTES (corrigidos) ===
from components.aba_perfil_players.aba_perfil_players import render_aba_players
from components.aba_perfil_transacoes.aba_perfil_transacoes import render_aba_perfil_transacoes
from components.aba_perfil_cupons.aba_perfil_cupons import render_aba_perfil_cupons

from api_client import get_all_json_df

# =========================
# Configuração
# =========================
st.set_page_config(page_title="Dashboard – CEO", layout="wide")
st.title("Dashboard – CEO")

# =========================
# Carga de bases (exemplo local; ajuste para API quando for integrar)
# =========================
# Opcional: ajuste TTL do cache (em segundos)
CACHE_TTL = 3600  # 1 hora

# ---------- Loaders cacheados (um por base) ----------
@st.cache_data(show_spinner=False, ttl=CACHE_TTL)
def load_players():
    # Busca todas as linhas de /players com paginação interna
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

# ---------- (Opcional) utilitário seguro ----------
def _safe(call, nome: str) -> pd.DataFrame:
    try:
        df = call()
        # garante DataFrame mesmo se API voltar lista vazia
        return df if isinstance(df, pd.DataFrame) else pd.DataFrame()
    except Exception as e:
        st.error(f"Erro ao carregar {nome}: {e}")
        return pd.DataFrame()

# ---------- Variáveis finais (como você pediu) ----------
df_players    = _safe(load_players,    "players")
df_lojas      = _safe(load_lojas,      "lojas")
df_transacoes = _safe(load_transacoes, "transações")
df_simulacao  = _safe(load_simulacao,  "simulação")

# ---------- (Opcional) botão para forçar atualização ----------
# Coloque o botão onde preferir na página
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

# Use df_lojas como base para a UI de período (você pode trocar por df_transacoes se preferir)
df_base = df_lojas.copy()
if df_base.empty:
    st.sidebar.error("Sem dados válidos em 'data' na base de lojas.")
    st.stop()

min_dt = df_base["data"].min().normalize()
max_dt = df_base["data"].max().normalize()

anos_disponiveis = sorted(df_base["data"].dt.year.unique().astype(int))
meses_disponiveis = sorted(df_base["data"].dt.month.unique().astype(int))
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

# Mês dentro do range de anos
meses_no_range = (
    df_base[df_base["data"].dt.year.between(anos_sel[0], anos_sel[1])]
    ["data"].dt.month.unique()
)
meses_no_range = sorted([int(m) for m in meses_no_range])
opcoes_meses_pt = [meses_pt[m] for m in (meses_no_range or list(range(1, 12+1)))]

if len(set(meses_no_range)) <= 1 and meses_no_range:
    mes_unico_num = meses_no_range[0]
    st.sidebar.markdown(f"**Mês (fixo – dados de teste):** {meses_pt[mes_unico_num]}")
    meses_sel = (mes_unico_num, mes_unico_num)
else:
    meses_sel_pt = st.sidebar.select_slider(
        "Mês (intervalo)",
        options=opcoes_meses_pt,
        value=(opcoes_meses_pt[0], opcoes_meses_pt[-1]) if opcoes_meses_pt else ("Janeiro", "Dezembro"),
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

# Modo de exibição
modo = st.sidebar.selectbox("Exibir como:", ["Valores", "Percentual", "Ambos"], index=0).lower()

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
# MÁSCARAS DE PERÍODO E DATA PARA CADA BASE
# =========================
# Para LOJAS/CUPONS (usam df_lojas):
mask_lojas = (
    df_lojas["data"].dt.year.between(anos_sel[0], anos_sel[1]) &
    df_lojas["data"].dt.month.between(meses_sel[0], meses_sel[1]) &
    df_lojas["data"].between(pd.to_datetime(d_ini), pd.to_datetime(d_fim))
)
df_lojas_filtrado = _aplica_filtros_adicionais(df_lojas.loc[mask_lojas].copy())

# Para TRANSAÇÕES (retenção usa df_transacoes):
mask_trans = (
    df_transacoes["data"].dt.year.between(anos_sel[0], anos_sel[1]) &
    df_transacoes["data"].dt.month.between(meses_sel[0], meses_sel[1]) &
    df_transacoes["data"].between(pd.to_datetime(d_ini), pd.to_datetime(d_fim))
)
df_trans_filtrado = _aplica_filtros_adicionais(df_transacoes.loc[mask_trans].copy())

# Ano/Mês escolhidos para funções (use o fim do range)
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
    render_aba_players(df_players)

with aba2:
    # Usa a BASE DE LOJAS (gráficos de frequência, comparativos, cupons etc.)
    render_aba_perfil_cupons(
        df_filtrado=df_lojas_filtrado,
        ano_escolhido=ano_escolhido,
        mes_escolhido=mes_escolhido,
        modo=modo,
        # componentes já usam 'nomes_lojas'/'categorias' internamente;
        # aqui passamos os valores do sidebar:
        filtro_nome=filtro_nome or None,
        filtro_tipo=filtro_categ or None,   # <— importante: passe como filtro_tipo para manter compatibilidade
    )

with aba3:
    render_aba_perfil_transacoes(
        df_filtrado=df_trans_filtrado,
        ano_escolhido=ano_escolhido,
        mes_escolhido=mes_escolhido,
        modo=modo,
        filtro_nome=filtro_nome or None,
        filtro_tipo=filtro_categ or None,
    )
