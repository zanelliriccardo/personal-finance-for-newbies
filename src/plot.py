import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from var import PLT_FONT_SIZE


def plot_sunburst(df: pd.DataFrame) -> go.Figure:
    fig = px.sunburst(
        data_frame=df.assign(hole=" "),
        path=["hole", "macro_asset_class", "asset_class", "ticker_yf"],
        values="weight_pf",
    )
    fig.update_traces(hovertemplate="<b>%{value:.1f}%")
    fig.update_layout(
        autosize=False,
        height=600,
        margin=dict(l=0, r=0, t=20, b=20),
        hoverlabel_font_size=PLT_FONT_SIZE,
    )
    return fig


def plot_pnl_by_asset_class(df_pnl: pd.DataFrame) -> go.Figure:
    df_pnl["color"] = np.where(df_pnl["pnl"].ge(0), "green", "red")
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=df_pnl["asset_class"],
            y=df_pnl["pnl"],
            marker_color=df_pnl["color"],
            text=df_pnl["pnl"],
            hoverinfo="skip",
        )
    )
    fig.update_traces(texttemplate="%{y:.1f}")
    fig.update_layout(
        autosize=False,
        height=500,
        margin=dict(l=0, r=0, t=20, b=20),
        barmode="stack",
        yaxis=dict(title="PnL", showgrid=False, tickformat=",.0f", ticksuffix=" €"),
    )
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
        height=550,
        hoverlabel_font_size=PLT_FONT_SIZE,
        margin=dict(l=0, r=0, t=20, b=20),
        xaxis=dict(title=""),
        yaxis=dict(
            title="Daily value", showgrid=False, tickformat=",.0f", ticksuffix=" €"
        ),
        showlegend=False,
    )
    return fig
