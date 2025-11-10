# theme_plotly.py
import plotly.express as px
import plotly.io as pio
import streamlit as st

# Paleta institucional
PALETA = ["#43BF30","#03318C", "#F2A649", "#7ABF36", "#B0BF3F"]

# Cores do tema do Streamlit (com fallback)
primary = st.get_option("theme.primaryColor") or PALETA[0]
bg = st.get_option("theme.backgroundColor") or "#FFFFFF"
bg2 = st.get_option("theme.secondaryBackgroundColor") or "#F5F5F5"
text = st.get_option("theme.textColor") or "#202124"

# Template personalizado
custom_layout = dict(
    paper_bgcolor=bg,
    plot_bgcolor=bg2,
    font=dict(color=text, family="sans-serif"),
    colorway=PALETA,
    xaxis=dict(showgrid=True, gridcolor="#E5E5E5"),
    yaxis=dict(showgrid=True, gridcolor="#E5E5E5"),
)

pio.templates["streamlit_custom"] = pio.templates["plotly_white"]
pio.templates["streamlit_custom"].layout.update(custom_layout)

# Aplicar como padrão
pio.templates.default = "streamlit_custom"
px.defaults.template = "streamlit_custom"
px.defaults.color_discrete_sequence = PALETA
px.defaults.width = None
px.defaults.height = 400
