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
