# utils/auto_download.py
import base64
import streamlit as st

def trigger_download(file_bytes: bytes, filename: str, mime: str = "application/pdf"):
    """
    Dispara download automático no navegador usando um link data: e JavaScript.
    """
    b64 = base64.b64encode(file_bytes).decode("utf-8")
    href = f"data:{mime};base64,{b64}"
    html = f"""
        <a id="__auto_dl" href="{href}" download="{filename}"></a>
        <script>
        const a = document.getElementById('__auto_dl');
        if (a) {{ a.click(); }}
        </script>
    """
    st.components.v1.html(html, height=0)
