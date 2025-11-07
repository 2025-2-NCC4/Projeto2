import pandas as pd
import numpy as np
import plotly.express as px

# -----------------------------
# Cidades – gráfico (com defaults para compatibilidade)
# -----------------------------
def grafico_cidades(df, tipo_cidade="Moradia"):
    i = "residencial" if tipo_cidade == "Moradia" else ("escola" if tipo_cidade == "Escola" else "trabalho")
    col_city = f"cidade_{i}"
    if col_city not in df.columns:
        return px.bar(title=f"Coluna ausente: {col_city}")

    df_cidade = (
        df.groupby(col_city)["celular"]
          .nunique()
          .reset_index(name="Players")
          .sort_values("Players", ascending=True)
    )

    fig = px.bar(
        df_cidade, x="Players", y=col_city, orientation="h",
        title=f"Cidades com mais Players ({tipo_cidade})",
        text="Players", color="Players", color_continuous_scale="Blues"
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(xaxis_title="Players", yaxis_title="Cidade",
                      xaxis=dict(autorange=True), yaxis=dict(autorange=True))
    return fig

# -----------------------------
# Bairros – gráfico (escolhe cidade automaticamente se não informada)
# -----------------------------
def grafico_bairros(df, tipo_cidade="Moradia", cidade=None):
    i = "residencial" if tipo_cidade == "Moradia" else ("escola" if tipo_cidade == "Escola" else "trabalho")
    col_city = f"cidade_{i}"
    col_bairro = f"bairro_{i}"
    for col in (col_city, col_bairro):
        if col not in df.columns:
            return px.bar(title=f"Coluna ausente: {col}")

    dff = df.copy()
    if cidade is None:
        # escolhe cidade top por número de players
        cidade = (
            dff.groupby(col_city)["celular"]
               .nunique()
               .sort_values(ascending=False)
               .head(1)
               .index.tolist()
        )
        cidade = cidade[0] if cidade else None
        if not cidade:
            return px.bar(title=f"Sem dados para {tipo_cidade}")

    dff = dff[dff[col_city] == cidade]

    df_bairro = (
        dff.groupby(col_bairro)["celular"]
           .nunique()
           .reset_index(name="Players")
           .sort_values("Players", ascending=True)
    )

    fig = px.bar(
        df_bairro, x="Players", y=col_bairro, orientation="h",
        title=f"Bairros com mais Players – {cidade} ({tipo_cidade})",
        text="Players", color="Players", color_continuous_scale="Blues"
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(xaxis_title="Players", yaxis_title="Bairro",
                      xaxis=dict(autorange=True), yaxis=dict(autorange=True))
    return fig
