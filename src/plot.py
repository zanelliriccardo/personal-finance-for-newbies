import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np


def plot_sunburst(df: pd.DataFrame) -> go.Figure:
    fig = px.sunburst(
        data_frame=df.assign(hole=" "),
        path=["hole", "macro_asset_class", "asset_class", "ticker_yf"],
        values="weight_pf",
    )
    fig.update_traces(hovertemplate="<b>%{value:.1f}%")
    fig.update_layout(autosize=False, height=650, hoverlabel_font_size=14)
    return fig


def plot_wealth(df: pd.DataFrame) -> go.Figure:
    fig = px.area(
        data_frame=df,
        x=df.index,
        y="ap_daily_value",
    )
    fig.update_traces(hovertemplate="%{x}: <b>%{y:,.0f}€</b>")
    fig.update_layout(
        autosize=False,
        height=600,
        width=900,
        hoverlabel_font_size=14,
        xaxis=dict(title=""),
        yaxis=dict(title="Daily value", tickformat=",.0f"),
        showlegend=False,
    )
    return fig
