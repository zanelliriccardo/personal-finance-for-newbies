import streamlit as st

from input_output import write_disclaimer, get_max_common_history
from risk import get_drawdown, get_max_dd
from returns import get_period_returns
from plot import plot_drawdown
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

ticker_list = df_transactions["ticker_yf"].unique().tolist()
df_common_history = get_max_common_history(ticker_list=ticker_list)

st.markdown("## Global settings")

col_l_up, col_r_up = st.columns([1, 1], gap="small")

level = col_l_up.radio(
    label="Aggregate by:",
    options=["Macro Asset Classes", "Asset Classes", "Tickers"],
    horizontal=True,
    index=2,
    key="level",
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
    period=DICT_FREQ_RESAMPLE[freq],
    level=DICT_GROUPBY_LEVELS[level],
)
default_objs = df_rets.columns.to_list()

cols = st.multiselect(
    f"Choose the {level.lower()} to display:",
    options=default_objs,
    default=default_objs[1],
    key="sel_lev_2",
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

write_disclaimer()

# returns = np.log(weighted_average.div(weighted_average.shift(1))).fillna(0)

# first_ap_day = str(df_storico["transaction_date"].min())[:10]

# sr = sharpe_ratio(
#     returns=returns,
#     trading_days=df_common_history.shape[0],
#     risk_free_rate=get_risk_free_rate_history(decimal=True)
#     .sort_index()
#     .loc[first_ap_day:]
#     .median()
#     .values[0],
# )

# st.write(sr)
