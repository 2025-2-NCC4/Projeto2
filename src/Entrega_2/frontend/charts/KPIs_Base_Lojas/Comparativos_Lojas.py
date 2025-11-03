import pandas as pd
import numpy as np
import plotly.express as px

def usuarios_loja(df):
    s = (
        df.groupby("nome_loja")["numero_celular"]
          .nunique()
          .sort_values(ascending=False)
          .reset_index(name="usuarios_unicos")
    )

    fig = px.bar(
        data_frame=s,
        y="nome_loja",
        x="usuarios_unicos",
        orientation="h",
        title="Lojas por Número de Capturas",
        text_auto=True,
        color="usuarios_unicos",
        color_continuous_scale="Blues",
        labels={"nome_loja": "Lojas", "usuarios_unicos": "Capturas"}
    )

    fig.update_layout(xaxis_tickangle=-45, height=500)
    return fig