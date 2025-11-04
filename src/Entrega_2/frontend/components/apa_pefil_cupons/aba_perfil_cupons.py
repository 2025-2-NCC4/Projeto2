# components/aba_lojas.py
import streamlit as st
from charts.KPIs_Base_Lojas.Frequencia_por_Loja_Capturas import (
    frequencia_ano_filtrada,
    frequencia_dia_semana_ano_filtrada,
    frequencia_dia_semana_mes_filtrada,
    frequencia_mensal_filtrada,
    frequencia_semanal_filtrada,
    frequencia_diaria_filtrada,
    medias_frequencia_filtrada,
)
from charts.KPIs_Base_Lojas.Comparativos_Lojas import (
    capturas_categoria,
    cupons_por_categoria,
    cupons_por_loja,
    heatmap_capturas_mapa,
    resumo_parceiros,
    tipo_cupom,
    usuarios_loja,
)

def render_aba_perfil_cupons(
    df_filtrado,
    ano_escolhido: int,
    mes_escolhido: int,
    modo: str,
    filtro_nome=None,          # lista/None
    filtro_tipo=None,          # lista/None (categoria_estabelecimento)
    filtro_categ=None,         # legado/opcional (não usado aqui)
    filtro_tipo_cupom=None,    # <<-- ADICIONADO
):
    """Renderiza a aba 'Perfil das Lojas' com base nos filtros e período."""
    st.subheader("Perfil de Cupons/Capturas")
    aba1, aba2, aba3 = st.tabs(["Frequência de Capturas", "Perfil de Lojas/Categorias", "Perfil de Cupons"])

    # ---------------------------
    # ABA 1 — Frequências
    # ---------------------------
    with aba1:
        # KPIs (cards)
        try:
            kpi = medias_frequencia_filtrada(
                df_filtrado,
                mes_escolhido,
                ano_escolhido,
                nome_estabelecimento=filtro_nome or None,
                categoria_estabelecimento=filtro_tipo or None,
            )
            st.write("Resumo de Frequência (médias):")
            media_diaria  = float(kpi.get("media_diaria_mes_ano", 0))
            media_semanal = float(kpi.get("media_semanal_ano", 0))
            media_mensal  = float(kpi.get("media_mensal_ano", 0))
            media_anual   = float(kpi.get("media_anual", 0))
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Média Diária (mês/ano)", f"{media_diaria:.1f}")
            c2.metric("Média Semanal (ano)",    f"{media_semanal:.1f}")
            c3.metric("Média Mensal (ano)",     f"{media_mensal:.1f}")
            c4.metric("Média Anual (base)",     f"{media_anual:.1f}")
        except Exception as e:
            st.warning(f"Não foi possível calcular 'medias_frequencia_filtrada': {e}")

        c5, c6 = st.columns(2)
        with c5:
            try:
                st.plotly_chart(
                    frequencia_diaria_filtrada(
                        df_filtrado,
                        mes_escolhido,
                        ano_escolhido,
                        nome_estabelecimento=filtro_nome or None,
                        categoria_estabelecimento=filtro_tipo or None,
                        modo=modo,
                    ),
                    use_container_width=True,
                )
            except Exception as e:
                st.warning(f"Erro no gráfico 'frequencia_diaria_filtrada': {e}")

        with c6:
            try:
                st.plotly_chart(
                    frequencia_semanal_filtrada(
                        df_filtrado,
                        ano_escolhido,
                        nome_estabelecimento=filtro_nome or None,
                        categoria_estabelecimento=filtro_tipo or None,
                        modo=modo,
                    ),
                    use_container_width=True,
                )
            except Exception as e:
                st.warning(f"Erro no gráfico 'frequencia_semanal_filtrada': {e}")

        c7, c8 = st.columns(2)
        with c7:
            try:
                st.plotly_chart(
                    frequencia_mensal_filtrada(
                        df_filtrado,
                        ano_escolhido,
                        nome_estabelecimento=filtro_nome or None,
                        categoria_estabelecimento=filtro_tipo or None,
                        modo=modo,
                    ),
                    use_container_width=True,
                )
            except Exception as e:
                st.warning(f"Erro no gráfico 'frequencia_mensal_filtrada': {e}")

        with c8:
            try:
                st.plotly_chart(
                    frequencia_ano_filtrada(
                        df_filtrado,
                        nome_estabelecimento=filtro_nome or None,
                        categoria_estabelecimento=filtro_tipo or None,
                        modo=modo,
                    ),
                    use_container_width=True,
                )
            except Exception as e:
                st.warning(f"Erro no gráfico 'frequencia_ano_filtrada': {e}")

        c9, c10 = st.columns(2)
        with c9:
            try:
                st.plotly_chart(
                    frequencia_dia_semana_mes_filtrada(
                        df_filtrado,
                        ano_escolhido,
                        mes_escolhido,
                        nome_estabelecimento=filtro_nome or None,
                        categoria_estabelecimento=filtro_tipo or None,
                        modo=modo,
                    ),
                    use_container_width=True,
                )
            except Exception as e:
                st.warning(f"Erro no gráfico 'frequencia_dia_semana_mes_filtrada': {e}")

        with c10:
            try:
                st.plotly_chart(
                    frequencia_dia_semana_ano_filtrada(
                        df_filtrado,
                        ano_escolhido,
                        nome_estabelecimento=filtro_nome or None,
                        categoria_estabelecimento=filtro_tipo or None,
                        modo=modo,
                    ),
                    use_container_width=True,
                )
            except Exception as e:
                st.warning(f"Erro no gráfico 'frequencia_dia_semana_ano_filtrada': {e}")

    # ---------------------------
    # ABA 2 — Lojas / Categorias
    # ---------------------------
    with aba2:
        st.subheader("Lojas e Categorias (comparativos)")

        # Resumo de parceiros — cards
        try:
            total_lojas, total_categorias = resumo_parceiros(df_filtrado, mes_escolhido, ano_escolhido)
            st.write("### Resumo de Parceiros")
            r1, r2 = st.columns(2)
            r1.metric("Total de Lojas", f"{total_lojas}")
            r2.metric("Total de Categorias", f"{total_categorias}")
        except Exception as e:
            st.warning(f"Erro no 'resumo_parceiros': {e}")

        c11, c12 = st.columns(2)
        with c11:
            try:
                st.plotly_chart(
                    usuarios_loja(
                        df_filtrado,
                        mes_escolhido,
                        ano_escolhido,
                        modo=modo,
                    ),
                    use_container_width=True,
                )
            except Exception as e:
                st.warning(f"Erro no gráfico 'usuarios_loja': {e}")

        with c12:
            try:
                st.plotly_chart(
                    capturas_categoria(
                        df_filtrado,
                        mes_escolhido,
                        ano_escolhido,
                        modo=modo,
                    ),
                    use_container_width=True,
                )
            except Exception as e:
                st.warning(f"Erro no gráfico 'capturas_categoria': {e}")

    # ---------------------------
    # ABA 3 — Cupons
    # ---------------------------
    with aba3:
        st.subheader("Perfil de Cupons")

        try:
            st.plotly_chart(
                tipo_cupom(
                    df_filtrado,
                    ano_escolhido,
                    mes=mes_escolhido,
                    nome_estabelecimento=filtro_nome or None,
                    categoria_estabelecimento=filtro_tipo or None,
                    modo=modo,
                ),
                use_container_width=True,
            )
        except Exception as e:
            st.warning(f"Erro no gráfico 'tipo_cupom': {e}")

        try:
            st.plotly_chart(
                cupons_por_loja(
                    df_filtrado,
                    mes=mes_escolhido,
                    ano=ano_escolhido,
                    modo=modo
                ),
                use_container_width=True
            )
        except Exception as e:
            st.warning(f"Erro no gráfico 'cupons_por_loja': {e}")

        try:
            st.plotly_chart(
                cupons_por_categoria(
                    df_filtrado,
                    mes=mes_escolhido,
                    ano=ano_escolhido,
                    modo=modo
                ),
                use_container_width=True
            )
        except Exception as e:
            st.warning(f"Erro no gráfico 'cupons_por_categoria': {e}")  # <-- corrigido

        try:
            st.plotly_chart(
                heatmap_capturas_mapa(
                    df_filtrado,
                    mes=mes_escolhido,
                    ano=ano_escolhido,
                    usar_unicos_por_player=True,
                    filtros={
                        "categoria_estabelecimento": filtro_tipo,
                        "nome_estabelecimento": filtro_nome,
                        "tipo_cupom": filtro_tipo_cupom,   # <<-- usando o novo parâmetro
                    },
                    radius=30,
                    opacity=0.65
                ),
                use_container_width=True
            )
        except Exception as e:
            st.warning(f"Erro no gráfico 'heatmap_capturas_mapa': {e}")
