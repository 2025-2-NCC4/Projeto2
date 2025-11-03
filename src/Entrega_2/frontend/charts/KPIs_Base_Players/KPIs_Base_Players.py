import pandas as pd
import numpy as np
import plotly.express as px

def fig_faixa_etaria(df):
    # mesmo cálculo das faixas
    bins = [0, 17, 24, 34, 44, 54, 64, 150]
    labels = ["0-17", "18-24", "25-34", "35-44", "45-54", "55-64", "65+"]
    df["faixa_etaria"] = pd.cut(df["idade"], bins=bins, labels=labels, right=True)

    # contagem ordenada
    faixa_counts = df["faixa_etaria"].value_counts().reindex(labels, fill_value=0)
    faixa_df = pd.DataFrame({
        "Faixa Etária": faixa_counts.index,
        "Players": faixa_counts.values
    })

    # cria o gráfico com plotly
    fig = px.bar(
        faixa_df,
        x="Faixa Etária",
        y="Players",
        text="Players",
        title="Distribuição de Players por Faixa Etária 🧍‍♀️🧍‍♂️",
        labels={"Faixa Etária": "Faixa Etária", "Players": "Quantidade de Players"},
    )

    # ajustes visuais
    fig.update_traces(textposition="outside")
    fig.update_layout(
        xaxis_title="Faixa Etária",
        yaxis_title="Jogadores",
        uniformtext_minsize=8,
        uniformtext_mode="hide"
    )
    return fig

def fig_idade_x_sexo(df):
 # agrupa os dados
    df_grouped = (
        df.groupby(["faixa_etaria", "sexo"])
        .size()
        .reset_index(name="qtd_players")
    )

    # cria o gráfico de barras agrupadas
    fig = px.bar(
        df_grouped,
        x="faixa_etaria",
        y="qtd_players",
        color="sexo",             
        barmode="group",         
        text="qtd_players",       
        labels={
            "faixa_etaria": "Faixa Etária",
            "qtd_players": "Players",
            "sexo": "Sexo"
        },
    title="Distribuição de players por Faixa Etária e Sexo"
        )

    # pequenas melhorias visuais
    fig.update_traces(textposition="outside")
    fig.update_layout(
        xaxis_title="Faixa Etária",
        yaxis_title="Quantidade de Jogadores",
        uniformtext_minsize=8,
        uniformtext_mode="hide"
    )

    return fig

def fig_sexo(df):
    # conta os jogadores por sexo
    sexo_counts = df["sexo"].value_counts().reset_index()
    sexo_counts.columns = ["Sexo", "Quantidade"]

    fig = px.pie(
        sexo_counts,
        names="Sexo",
        values="Quantidade",
        title="Distribuição de Jogadores por Sexo",
        hole=0.3,         
    )
    return fig

def metricas_etarias(df):
    moda = df["idade"].mode().to_list()
    media = round(df["idade"].mean(), 0)
    mediana = df["idade"].median()

    return moda, media, mediana

def df_principais_categorias(df):
    df = (
        df.groupby("categoria_frequentada")["celular"]
        .nunique()
        .reset_index()
        .rename(columns={
            "categoria_frequentada": "Categorias",
            "celular": "Players Únicos"
        })
        .sort_values(by="Players Únicos", ascending=False)
    )

    fig = px.bar(
        df,
        x="Players Únicos",
        y="Categorias",
        orientation="h",
        title="🏆 Ranking de Categorias por Players Únicos",
        text="Players Únicos",
    )

    fig.update_traces(textposition="outside")
    fig.update_layout(
        xaxis_title="Quantidade de Players",
        yaxis_title="Categorias",
        uniformtext_minsize=8,
        uniformtext_mode="hide"
    )
    return fig

def grafico_cidades(df, tipo_cidade):
    i = "residencial" if tipo_cidade == "Moradia" else ("escola" if tipo_cidade == "Escola" else "trabalho")
    col_city = f"cidade_{i}"

    df_cidade = (
        df.groupby(col_city)["celular"]
        .nunique()
        .reset_index(name="Players")
        .sort_values("Players", ascending=True)
    )

 

    fig = px.bar(
        df_cidade,
        x="Players",
        y=col_city,
        orientation="h",
        title=f"Cidades com mais Players ({tipo_cidade})",
        text="Players",
        color="Players",
        color_continuous_scale="Blues"
    )

    fig.update_traces(textposition="outside")
    fig.update_layout(xaxis_title="Players", yaxis_title="Cidade", xaxis=dict(autorange=True), yaxis=dict(autorange=True))

    return fig


def grafico_bairros(df, tipo_cidade, cidade):
    i = "residencial" if tipo_cidade == "Moradia" else ("escola" if tipo_cidade == "Escola" else "trabalho")
    col_city = f"cidade_{i}"
    col_bairro = f"bairro_{i}"

    dff = df[df[col_city] == cidade]
    df_bairro = (
        dff.groupby(col_bairro)["celular"]
        .nunique()
        .reset_index(name="Players")
        .sort_values("Players", ascending=True)
    )


    fig = px.bar(
        df_bairro,
        x="Players",
        y=col_bairro,
        orientation="h",
        title=f"Bairros com mais Players – {cidade} ({tipo_cidade})",
        text="Players",
        color="Players",
        color_continuous_scale="Blues"
    )

    fig.update_traces(textposition="outside")
    fig.update_layout(xaxis_title="Players", yaxis_title="Bairro", xaxis=dict(autorange=True), yaxis=dict(autorange=True))
    return fig