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
    resumo_parceiros,
    tipo_cupom,
    usuarios_loja,
)

def render_aba_lojas(
    df_filtrado,
    ano_escolhido: int,
    mes_escolhido: int,
    modo: str,
    filtro_nome=None,   # lista/None
    filtro_tipo=None,   # lista/None
    filtro_categ=None,  # lista/None (aplicado antes da chamada, se existir)
):
    """Renderiza a aba 'Perfil das Lojas' com base nos filtros e período."""
    st.subheader("Capturas / Lojas – Período Selecionado")

    # KPIs (médias/sumários) no topo
    try:
        kpi = medias_frequencia_filtrada(
            df_filtrado,
            mes_escolhido,
            ano_escolhido,
            nome_estabelecimento=filtro_nome or None,
            categoria_estabelecimento=filtro_tipo or None,
        )
        st.write("Resumo de Frequência (médias):")
        media_diaria = kpi.get("media_diaria_mes_ano", 0)
        media_semanal = kpi.get("media_semanal_ano", 0)
        media_mensal = kpi.get("media_mensal_ano", 0)
        media_anual = kpi.get("media_anual", 0)

        st.write("### Resumo de Frequência (médias)")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Média Diária (mês/ano)", f"{media_diaria:.1f}")
        col2.metric("Média Semanal (ano)", f"{media_semanal:.1f}")
        col3.metric("Média Mensal (ano)", f"{media_mensal:.1f}")
        col4.metric("Média Anual (base)", f"{media_anual:.1f}")
    except Exception as e:
        st.warning(f"Não foi possível calcular 'medias_frequencia_filtrada': {e}")

    c1, c2 = st.columns(2)
    with c1:
        # Frequência diária
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

        
    
    with c2:
        # Frequência semanal (ANUAL)
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
    c3, c4 = st.columns(2)
    with c3:
        # Frequência mensal (ANUAL)
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
    with c4:
        # Frequência anual (toda base)
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


    c5, c6 = st.columns(2)
    with c5:
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

    with c6:
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


    st.markdown("---")
    st.subheader("Lojas e Categorias (comparativos)")

    c7, c8 = st.columns(2)
    with c7:
        # Usuários por loja
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

        # Resumo de parceiros
        try:
            resumo = resumo_parceiros(df_filtrado, mes_escolhido, ano_escolhido)
            st.dataframe(resumo, use_container_width=True)
        except Exception as e:
            st.warning(f"Erro no 'resumo_parceiros': {e}")

    with c8:
        # Capturas por categoria
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

    st.markdown("---")
    st.subheader("Perfil de Cupons")

    # Tipo de cupom (pizza/treemap/etc.) — agora filtrado por período + filtros
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
