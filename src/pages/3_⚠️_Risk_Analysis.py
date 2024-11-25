import streamlit as st

from input_output import write_disclaimer, get_max_common_history
from risk import get_drawdown, get_max_dd, get_portfolio_relative_risk_contribution, compute_metrics, compute_rolling_metrics
from returns import get_period_returns
from plot import plot_drawdown, plot_horizontal_bar, plot_risk_metrics_over_time
import pandas as pd
from var import (
    GLOBAL_STREAMLIT_STYLE,
    PLT_CONFIG_NO_LOGO,
    FAVICON,
    DICT_GROUPBY_LEVELS,
    DICT_FREQ_RESAMPLE,
    PLT_CONFIG,
)

st.set_page_config(
    page_title="PFN | Risk Analysis",
    page_icon=FAVICON,
    layout="wide",
    initial_sidebar_state="auto",
)

st.markdown(GLOBAL_STREAMLIT_STYLE, unsafe_allow_html=True)

if "data" in st.session_state:
    df_transactions = st.session_state["data"]
    df_registry = st.session_state["dimensions"]
else:
    st.error("Oops... there's nothing to display. Go through 🏠 first to load the data")
    st.stop()

df_n_shares = (
    df_transactions.groupby("ticker_yf")
    .agg(n_shares=("shares", "sum"))
    .sort_values("n_shares", ascending=False)
)
ticker_list = df_n_shares.loc[~(df_n_shares == 0).all(axis=1)].index.unique().to_list()

df_common_history = get_max_common_history(ticker_list=ticker_list)

st.markdown("## Global settings")

col_l_up, col_r_up = st.columns([1, 1], gap="small")

level = col_l_up.radio(
    label="Aggregate by:",
    options=["Macro Asset Classes", "Asset Classes", "Tickers"],
    horizontal=True,
    index=2,
    key="level",
    help="Choose how to aggregate data for analysis: Tickers provides the most granular view, while Macro Asset Classes aggregates at the highest level",
)
freq = col_r_up.radio(
    label="Frequency of returns:",
    options=["Month", "Week", "Day"],
    horizontal=True,
    index=2,
    key="freq",
)

st.markdown("<br>", unsafe_allow_html=True)
col_l_mid, col_c_mid, col_r_mid = st.columns([0.3, 1, 0.3], gap="small")
first_transaction = df_transactions["transaction_date"].sort_values().values[0]

first_day, last_day = col_c_mid.select_slider(
    "Select a time slice:",
    options=df_common_history.index,
    value=[
        max(df_common_history.index[0], first_transaction),
        df_common_history.index[-1],
    ],
    format_func=lambda value: str(value)[:10],
    label_visibility="collapsed",
)

st.markdown("***")

st.markdown(f"## Drawdown in {freq.lower().replace('day','dai')}ly returns")

df_rets = get_period_returns(
    df=df_common_history.loc[first_day:last_day, :],
    df_registry=df_registry,
    tickers_to_evaluate=ticker_list,
    period=DICT_FREQ_RESAMPLE[freq],
    level=DICT_GROUPBY_LEVELS[level],
)
default_objs = df_rets.columns.to_list()

cols = st.multiselect(
    f"Choose the {level.lower()} to display:",
    options=default_objs,
    default=default_objs[0],
    key="sel_lev_3",
)

if freq == "Day":
    window = st.radio(
        "Specify a rolling time window:",
        options=[
            "No window (whole time span)",
            "1 month (21 days)",
            "3 months (63 days)",
        ],
        horizontal=True,
    )
    if window == "No window (whole time span)":
        df_dd = get_drawdown(df_rets[cols])
    elif window == "3 months (63 days)":
        df_dd = df_rets[cols].rolling(window=63).apply(get_max_dd)
    elif window == "1 month (21 days)":
        df_dd = df_rets[cols].rolling(window=21).apply(get_max_dd)
else:
    df_dd = get_drawdown(df_rets[cols])

fig = plot_drawdown(df=df_dd)
st.plotly_chart(fig, use_container_width=True, config=PLT_CONFIG)

st.markdown("***")

st.markdown("## Relative risk contribution")

st.markdown(
    """
The <b>relative risk contribution</b> $\widetilde{\mathcal{R}}_i$ from the $i$-th
asset (or asset class) is the ratio of its risk contribution $\mathcal{R}_i$ to the
total portfolio risk $\sigma$,
""",
    unsafe_allow_html=True,
)
st.latex(
    r"""
    \widetilde{\mathcal{R}}_i \overset{\underset{\mathrm{def}}{}}{=}
    \frac{\mathcal{R}_i}{\sigma} = \frac{1}{\sigma}
    \left(w_i \frac{\partial \sigma}{\partial w_i} \right) =
    \frac{w_i (\Sigma \mathrm{w})^i}{\mathrm{w^T \Sigma w}},
    \text{ so that } \sum_{i=1}^n \widetilde{\mathcal{R}}_i = 1.
    """
)
st.markdown(
    r"""
    In the above definition:
    - $\Sigma\in\mathbb{R}^{n \times n}$ is the portfolio return covariance matrix;
    - $\mathrm{w}\in\mathbb{R}^n$ are the portfolio weights;
    - $\mathcal{R}_i$ can be interpreted as the weighted marginal
    risk contribution of the $i$-th asset: it measures the sensitivity of portfolio
    risk to the $i$-th asset weight.
    
    Understanding relative risk contributions $\widetilde{\mathcal{R}}_i$ proves
    useful for portfolio <b>risk accounting and management</b>. This is a kind of
    dual representation, framed in the "risk space" (top chart) instead of the
    "weight space" (bottom chart).
    """,
    unsafe_allow_html=True,
)

order_by = st.radio(
    "Sort bars by:",
    options=[
        "Relative risk contribution",
        "Portfolio weight",
    ],
    horizontal=True,
)

order_by = (
    "pf_weight" if order_by == "Portfolio weight" else "relative_risk_contribution"
)

df_rrc = get_portfolio_relative_risk_contribution(
    df_prices=df_common_history.loc[first_day:last_day, :],
    df_shares=df_n_shares,
    df_registry=df_registry[df_registry["ticker_yf"].isin(ticker_list)],
    level=DICT_GROUPBY_LEVELS[level],
).sort_values(by=order_by, ascending=False)

fig = plot_horizontal_bar(
    df=df_rrc,
    field_to_plot="relative_risk_contribution",
    xaxis_title="Relative risk contribution",
)
st.plotly_chart(fig, use_container_width=True, config=PLT_CONFIG_NO_LOGO)

fig = plot_horizontal_bar(
    df=df_rrc, field_to_plot="pf_weight", xaxis_title="Portfolio weight"
)
st.plotly_chart(fig, use_container_width=True, config=PLT_CONFIG_NO_LOGO)


st.markdown("## Last year risk metrics")
df_rets = get_period_returns(
    df=df_common_history.loc[first_day:last_day, :],
    df_registry=df_registry,
    tickers_to_evaluate=ticker_list,
    period=DICT_FREQ_RESAMPLE["Day"],
    level=DICT_GROUPBY_LEVELS[level],
)
# take last year
df_rets = df_rets.iloc[-252:]
metrics_df = compute_metrics(df_returns=df_rets, trading_days=len(df_rets))

metrics_df.to_excel("metrics.xlsx")
st.dataframe(metrics_df.style.format("{:.4f}"))

st.markdown("***")

#st.markdown("## Risk metrics over time")

#window = st.slider(
#    "Choose a rolling window:",
#    min_value=1,
#    max_value=df_common_history.loc[first_day:last_day, :].shape[0] - 2,
#    value=30,
#)

#cols = st.multiselect(
#    f"Choose the assets to display:",
#    options=df_rets.columns.to_list(),
#    default=df_rets.columns.to_list()[0],
#    key="sel_lev_2",
#)

#rolling_metrics_df = compute_rolling_metrics(
#    df_returns=df_rets[cols],
#    trading_days=len(df_rets), 
#    window=window
#)

#fig = plot_risk_metrics_over_time(df=rolling_metrics_df)

#st.plotly_chart(fig, use_container_width=True, config=PLT_CONFIG_NO_LOGO)




write_disclaimer()