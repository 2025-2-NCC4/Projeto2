import streamlit as st
from charts.KPIs_Base_Lojas.Perfil_Frequencia_Capturas import (
    frequencia_ano_filtrada,
    frequencia_dia_semana_ano_filtrada,
    frequencia_dia_semana_mes_filtrada,
    frequencia_mensal_filtrada,
    frequencia_semanal_filtrada,
    frequencia_diaria_filtrada,
    medias_frequencia_filtrada,
)
from charts.KPIs_Base_Lojas.Perfil_Comparativo_Lojas_Categorias import (
    usuarios_loja,
    capturas_categoria,
    estabelecimentos_por_categoria,
    lista_estabelecimentos_por_categoria,
    resumo_parceiros,
)
from charts.KPIs_Base_Lojas.Perfil_Cupons import (
    cupons_por_categoria,
    cupons_por_loja,
    tipo_cupom,
)

def render_aba_perfil_cupons(
    df_filtrado,
    ano_escolhido: int,
    mes_escolhido: int,
    modo: str,
    filtro_nome=None,   # lista/None -> nomes_lojas
    filtro_tipo=None,   # lista/None -> categorias (categoria_estabelecimento)
    filtro_categ=None,  # legado/opcional (não usado)
    export: bool = False,
):
    

    """Renderiza a aba 'Perfil de Cupons/Capturas'. Se export=True, retorna {titulo: fig}."""
    figs = {}

    if not export:
        st.subheader("Perfil de Cupons/Capturas")
        aba1, aba2, aba3 = st.tabs(["Frequência de Capturas", "Perfil de Lojas/Categorias", "Perfil de Cupons"])

    # ---------- ABA 1: Frequências ----------
    def _aba_freq():
        loc_figs = {}
        try:
            kpi = medias_frequencia_filtrada(
                df_filtrado, mes_escolhido, ano_escolhido,
                nomes_lojas=filtro_nome or None,
                categorias=filtro_tipo or None,
            )
            # KPI não entra no PDF como gráfico; se quiser, use no resumo do relatório
        except Exception as e:
            if not export: st.warning(f"Não foi possível calcular 'medias_frequencia_filtrada': {e}")

        def _safe_build(title, fn):
            try:
                fig = fn()
                if fig: loc_figs[title] = fig
                if not export: st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                if not export: st.warning(f"Erro no gráfico '{title}': {e}")

        if not export:
            c5, c6 = st.columns(2)
            with c5:
                _safe_build(
                    "Frequência Diária (mês/ano)",
                    lambda: frequencia_diaria_filtrada(
                        df_filtrado, mes_escolhido, ano_escolhido,
                        nomes_lojas=filtro_nome or None, categorias=filtro_tipo or None, modo=modo
                    ),
                )
            with c6:
                _safe_build(
                    "Frequência Semanal (ano)",
                    lambda: frequencia_semanal_filtrada(
                        df_filtrado, ano_escolhido,
                        nomes_lojas=filtro_nome or None, categorias=filtro_tipo or None, modo=modo
                    ),
                )
            c7, c8 = st.columns(2)
            with c7:
                _safe_build(
                    "Frequência Mensal (ano)",
                    lambda: frequencia_mensal_filtrada(
                        df_filtrado, ano_escolhido,
                        nomes_lojas=filtro_nome or None, categorias=filtro_tipo or None, modo=modo
                    ),
                )
            with c8:
                _safe_build(
                    "Frequência por Ano (base)",
                    lambda: frequencia_ano_filtrada(
                        df_filtrado,
                        nomes_lojas=filtro_nome or None, categorias=filtro_tipo or None, modo=modo
                    ),
                )
            c9, c10 = st.columns(2)
            with c9:
                _safe_build(
                    "Dia da Semana (mês selecionado)",
                    lambda: frequencia_dia_semana_mes_filtrada(
                        df_filtrado, ano_escolhido, mes_escolhido,
                        nomes_lojas=filtro_nome or None, categorias=filtro_tipo or None, modo=modo
                    ),
                )
            with c10:
                _safe_build(
                    "Dia da Semana (ano selecionado)",
                    lambda: frequencia_dia_semana_ano_filtrada(
                        df_filtrado, ano_escolhido,
                        nomes_lojas=filtro_nome or None, categorias=filtro_tipo or None, modo=modo
                    ),
                )
        else:
            # Em export, apenas coleta as figuras (sem layout em colunas)
            _safe_build(
                "Frequência Diária (mês/ano)",
                lambda: frequencia_diaria_filtrada(
                    df_filtrado, mes_escolhido, ano_escolhido,
                    nomes_lojas=filtro_nome or None, categorias=filtro_tipo or None, modo=modo
                ),
            )
            _safe_build(
                "Frequência Semanal (ano)",
                lambda: frequencia_semanal_filtrada(
                    df_filtrado, ano_escolhido,
                    nomes_lojas=filtro_nome or None, categorias=filtro_tipo or None, modo=modo
                ),
            )
            _safe_build(
                "Frequência Mensal (ano)",
                lambda: frequencia_mensal_filtrada(
                    df_filtrado, ano_escolhido,
                    nomes_lojas=filtro_nome or None, categorias=filtro_tipo or None, modo=modo
                ),
            )
            _safe_build(
                "Frequência por Ano (base)",
                lambda: frequencia_ano_filtrada(
                    df_filtrado,
                    nomes_lojas=filtro_nome or None, categorias=filtro_tipo or None, modo=modo
                ),
            )
            _safe_build(
                "Dia da Semana (mês selecionado)",
                lambda: frequencia_dia_semana_mes_filtrada(
                    df_filtrado, ano_escolhido, mes_escolhido,
                    nomes_lojas=filtro_nome or None, categorias=filtro_tipo or None, modo=modo
                ),
            )
            _safe_build(
                "Dia da Semana (ano selecionado)",
                lambda: frequencia_dia_semana_ano_filtrada(
                    df_filtrado, ano_escolhido,
                    nomes_lojas=filtro_nome or None, categorias=filtro_tipo or None, modo=modo
                ),
            )
        return loc_figs

    # ---------- ABA 2: Lojas/Categorias ----------
    def _aba_lojas_categ():
        loc_figs = {}
        try:
            # KPIs de contagem não geram figura
            resumo_parceiros(
                df_filtrado, mes_escolhido, ano_escolhido,
                nomes_lojas=filtro_nome or None, categorias=filtro_tipo or None,
            )
        except Exception as e:
            if not export: st.warning(f"Erro no 'resumo_parceiros': {e}")

        def _plot(title, fn):
            try:
                fig = fn()
                if fig: loc_figs[title] = fig
                if not export: st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                if not export: st.warning(f"Erro no gráfico '{title}': {e}")

        if not export:
            c11, c12 = st.columns(2)
            with c11:
                _plot(
                    "Usuários por Loja (mês/ano)",
                    lambda: usuarios_loja(
                        df_filtrado, mes_escolhido, ano_escolhido, modo=modo,
                        nomes_lojas=filtro_nome or None, categorias=filtro_tipo or None
                    ),
                )
            with c12:
                _plot(
                    "Capturas por Categoria (mês/ano)",
                    lambda: capturas_categoria(
                        df_filtrado, mes_escolhido, ano_escolhido, modo=modo,
                        nomes_lojas=filtro_nome or None, categorias=filtro_tipo or None
                    ),
                )
            _plot(
                "Estabelecimentos por Categoria (mês/ano)",
                lambda: estabelecimentos_por_categoria(
                    df_filtrado, mes_escolhido, ano_escolhido, modo=modo,
                    nomes_lojas=filtro_nome or None, categorias=filtro_tipo or None
                ),
            )
            # lista_estabelecimentos_por_categoria é texto -> não vai para PDF
        else:
            _plot(
                "Usuários por Loja (mês/ano)",
                lambda: usuarios_loja(
                    df_filtrado, mes_escolhido, ano_escolhido, modo=modo,
                    nomes_lojas=filtro_nome or None, categorias=filtro_tipo or None
                ),
            )
            _plot(
                "Capturas por Categoria (mês/ano)",
                lambda: capturas_categoria(
                    df_filtrado, mes_escolhido, ano_escolhido, modo=modo,
                    nomes_lojas=filtro_nome or None, categorias=filtro_tipo or None
                ),
            )
            _plot(
                "Estabelecimentos por Categoria (mês/ano)",
                lambda: estabelecimentos_por_categoria(
                    df_filtrado, mes_escolhido, ano_escolhido, modo=modo,
                    nomes_lojas=filtro_nome or None, categorias=filtro_tipo or None
                ),
            )
        return loc_figs

    # ---------- ABA 3: Cupons ----------
    def _aba_cupons():
        loc_figs = {}
        def _plot(title, fn):
            try:
                fig = fn()
                if fig: loc_figs[title] = fig
                if not export: st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                if not export: st.warning(f"Erro no gráfico '{title}': {e}")

        _plot(
            "Tipos de Cupom (composição)",
            lambda: tipo_cupom(
                df_filtrado, ano_escolhido, mes=mes_escolhido,
                nomes_lojas=filtro_nome or None, categorias=filtro_tipo or None, modo=modo
            ),
        )
        _plot(
            "Cupons por Loja (mês/ano)",
            lambda: cupons_por_loja(
                df_filtrado, mes=mes_escolhido, ano=ano_escolhido, modo=modo,
                nomes_lojas=filtro_nome or None, categorias=filtro_tipo or None
            ),
        )
        _plot(
            "Cupons por Categoria (mês/ano)",
            lambda: cupons_por_categoria(
                df_filtrado, mes=mes_escolhido, ano=ano_escolhido, modo=modo,
                nomes_lojas=filtro_nome or None, categorias=filtro_tipo or None
            ),
        )
        return loc_figs

    if not export:
        with aba1: figs.update(_aba_freq())
        with aba2: figs.update(_aba_lojas_categ())
        with aba3: figs.update(_aba_cupons())
        return None
    else:
        figs.update(_aba_freq())
        figs.update(_aba_lojas_categ())
        figs.update(_aba_cupons())
        return figs
