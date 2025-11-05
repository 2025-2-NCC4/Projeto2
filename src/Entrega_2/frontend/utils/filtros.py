# utils/filtros.py
from __future__ import annotations
import pandas as pd
import numpy as np
from typing import Iterable, List, Optional, Tuple

# ----------------------------
# 🔤 Constantes de referência
# ----------------------------
MESES_PT = {
    1:"Janeiro",2:"Fevereiro",3:"Março",4:"Abril",5:"Maio",6:"Junho",
    7:"Julho",8:"Agosto",9:"Setembro",10:"Outubro",11:"Novembro",12:"Dezembro"
}
MESES_INVERSO = {v.lower(): k for k, v in MESES_PT.items()}

DIAS_PT = {
    0:"Segunda",1:"Terça",2:"Quarta",3:"Quinta",4:"Sexta",5:"Sábado",6:"Domingo"
}

# ----------------------------
# 🔧 Normalização de valores
# ----------------------------
def normalizar_texto(valor: object) -> str:
    """Padroniza texto para minúsculas e remove espaços."""
    return str(valor).strip().casefold()

def lista_normalizada(itens: Optional[Iterable]) -> List[str]:
    """Garante que o valor seja uma lista padronizada e limpa ('todas' -> vazio)."""
    if itens is None:
        return []
    if isinstance(itens, (list, tuple, set)):
        return [
            normalizar_texto(v)
            for v in itens
            if normalizar_texto(v) not in {"", "todas", "all"}
        ]
    v = normalizar_texto(itens)
    return [] if v in {"", "todas", "all"} else [v]

# ----------------------------
# 🗓️ Tratamento de datas
# ----------------------------
def garantir_coluna_data(df: pd.DataFrame, coluna: str = "data") -> pd.DataFrame:
    """Converte a coluna para datetime e remove valores nulos."""
    dff = df.copy()
    dff[coluna] = pd.to_datetime(dff[coluna], errors="coerce")
    return dff.dropna(subset=[coluna])

def converter_mes(mes) -> Optional[int]:
    """Aceita número ou nome em português e retorna o número do mês (1–12)."""
    if mes is None:
        return None
    if isinstance(mes, (int, np.integer)) and 1 <= int(mes) <= 12:
        return int(mes)
    if isinstance(mes, str):
        return MESES_INVERSO.get(mes.lower())
    try:
        m = int(mes)
        return m if 1 <= m <= 12 else None
    except Exception:
        return None

# ----------------------------
# 🏪 Filtros de negócio
# ----------------------------
def filtrar_lojas_e_categorias(
    df: pd.DataFrame,
    nomes_estabelecimentos: Optional[Iterable] = None,
    categorias: Optional[Iterable] = None
) -> pd.DataFrame:
    """Aplica filtros de nome e categoria de estabelecimento."""
    dff = df.copy()
    lojas = lista_normalizada(nomes_estabelecimentos)
    cats = lista_normalizada(categorias)

    if lojas and "nome_estabelecimento" in dff.columns:
        dff = dff[
            dff["nome_estabelecimento"].astype(str).str.strip().str.casefold().isin(lojas)
        ]
    if cats and "categoria_estabelecimento" in dff.columns:
        dff = dff[
            dff["categoria_estabelecimento"].astype(str).str.strip().str.casefold().isin(cats)
        ]
    return dff

def filtrar_por_ano_e_mes(
    df: pd.DataFrame,
    ano: int,
    mes: Optional[int] = None,
    coluna_data: str = "data"
) -> pd.DataFrame:
    """Filtra o DataFrame pelo ano e, opcionalmente, pelo mês."""
    dff = garantir_coluna_data(df, coluna_data)
    dff = dff[dff[coluna_data].dt.year == int(ano)]
    if mes is not None:
        dff = dff[dff[coluna_data].dt.month == int(mes)]
    return dff

# ----------------------------
# 🏷️ Geração de rótulos/títulos
# ----------------------------
def sufixo_titulo(
    nomes_lojas: Optional[Iterable] = None,
    categorias: Optional[Iterable] = None
) -> str:
    """Cria sufixo textual com filtros aplicados (para títulos de gráficos)."""
    lojas = lista_normalizada(nomes_lojas)
    cats = lista_normalizada(categorias)
    partes = []
    if lojas:
        partes.append(" / ".join(lojas))
    if cats:
        partes.append(" / ".join(cats))
    return f" – {', '.join(partes)}" if partes else ""

def texto_valores(df: pd.DataFrame, col_valor="valor", col_pct="pct", modo="valores"):
    """Retorna texto formatado para gráficos (valor, %, ou ambos)."""
    modo = normalizar_texto(modo)
    if modo == "percentual":
        return df[col_pct].map(lambda x: f"{x:.1%}")
    if modo == "ambos":
        return df.apply(lambda r: f"{int(r[col_valor])} ({r[col_pct]:.1%})", axis=1)
    return df[col_valor].astype(int).astype(str)
