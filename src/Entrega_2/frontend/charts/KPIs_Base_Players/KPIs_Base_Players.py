import pandas as pd
import numpy as np
import plotly.express as px

# -----------------------------
# Utilitários
# -----------------------------
_FAIXAS = ([0, 17, 24, 34, 44, 54, 64, 150],
           ["0-17", "18-24", "25-34", "35-44", "45-54", "55-64", "65+"])

def _ensure_numeric(series):
    s = pd.to_numeric(series, errors="coerce")
    return s

def _ensure_faixa(df):
    if "faixa_etaria" in df.columns:
        return df
    bins, labels = _FAIXAS
    dff = df.copy()
    dff["idade"] = _ensure_numeric(dff.get("idade"))
    dff["faixa_etaria"] = pd.cut(dff["idade"], bins=bins, labels=labels, right=True)
    return dff

# -----------------------------
# Faixa etária – gráfico
# -----------------------------
def fig_faixa_etaria(df):
    dff = df.copy()
    dff["idade"] = _ensure_numeric(dff.get("idade"))
    bins, labels = _FAIXAS
    dff["faixa_etaria"] = pd.cut(dff["idade"], bins=bins, labels=labels, right=True)

    faixa_counts = dff["faixa_etaria"].value_counts().reindex(labels, fill_value=0)
    faixa_df = pd.DataFrame({"Faixa Etária": faixa_counts.index, "Players": faixa_counts.values})

    fig = px.bar(
        faixa_df, x="Faixa Etária", y="Players", text="Players",
        title="Distribuição de Players por Faixa Etária",
        labels={"Faixa Etária": "Faixa Etária", "Players": "Quantidade de Players"},
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(xaxis_title="Faixa Etária", yaxis_title="Jogadores",
                      uniformtext_minsize=8, uniformtext_mode="hide")
    return fig

# -----------------------------
# Faixa x Sexo – gráfico
# -----------------------------
def fig_idade_x_sexo(df):
    dff = _ensure_faixa(df)
    dff["sexo"] = dff.get("sexo").fillna("Não informado")

    bins, labels = _FAIXAS
    # garante ordem das faixas
    dff["faixa_etaria"] = pd.Categorical(dff["faixa_etaria"], categories=labels, ordered=True)

    df_grouped = (
        dff.groupby(["faixa_etaria", "sexo"])
           .size()
           .reset_index(name="qtd_players")
           .sort_values(["faixa_etaria", "sexo"])
    )

    fig = px.bar(
        df_grouped, x="faixa_etaria", y="qtd_players", color="sexo",
        barmode="group", text="qtd_players",
        labels={"faixa_etaria": "Faixa Etária", "qtd_players": "Players", "sexo": "Sexo"},
        title="Distribuição de Players por Faixa Etária e Sexo",
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(xaxis_title="Faixa Etária", yaxis_title="Quantidade de Jogadores",
                      uniformtext_minsize=8, uniformtext_mode="hide")
    return fig

# -----------------------------
# Sexo – gráfico
# -----------------------------
def fig_sexo(df):
    dff = df.copy()
    dff["sexo"] = dff.get("sexo").fillna("Não informado")
    sexo_counts = dff["sexo"].value_counts(dropna=False).reset_index()
    sexo_counts.columns = ["Sexo", "Quantidade"]

    fig = px.pie(
        sexo_counts, names="Sexo", values="Quantidade",
        title="Distribuição de Jogadores por Sexo", hole=0.3
    )
    return fig

# -----------------------------
# Métricas etárias – retorna DataFrame (compatível com st.dataframe)
# -----------------------------
def metricas_etarias(df):
    dff = df.copy()
    dff["idade"] = _ensure_numeric(dff.get("idade"))
    moda_vals = dff["idade"].mode(dropna=True).dropna().astype(int).tolist()
    media = float(np.nanmean(dff["idade"])) if dff["idade"].notna().any() else np.nan
    mediana = float(np.nanmedian(dff["idade"])) if dff["idade"].notna().any() else np.nan

    out = pd.DataFrame({
        "Métrica": ["Moda (anos)", "Média (anos)", "Mediana (anos)"],
        "Valor": [", ".join(map(str, moda_vals)) if moda_vals else "—",
                  round(media, 1) if pd.notna(media) else "—",
                  round(mediana, 1) if pd.notna(mediana) else "—"]
    })
    return out

# -----------------------------
# Cidades – gráfico (com defaults para compatibilidade)
# -----------------------------
def grafico_cidades(df, tipo_cidade="Moradia", top_n=20):
    i = "residencial" if tipo_cidade == "Moradia" else ("escola" if tipo_cidade == "Escola" else "trabalho")
    col_city = f"cidade_{i}"
    if col_city not in df.columns:
        return px.bar(title=f"Coluna ausente: {col_city}")

    df_cidade = (
        df.groupby(col_city)["celular"]
          .nunique()
          .reset_index(name="Players")
          .sort_values("Players", ascending=True)
          .tail(top_n)
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
def grafico_bairros(df, tipo_cidade="Moradia", cidade=None, top_n=20):
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
           .tail(top_n)
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
