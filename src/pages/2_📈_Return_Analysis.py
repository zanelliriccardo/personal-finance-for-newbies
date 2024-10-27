import streamlit as st

from input_output import write_disclaimer, get_max_common_history
from returns import get_period_returns
from plot import plot_correlation_map, plot_returns
from var import (
    GLOBAL_STREAMLIT_STYLE,
    PLT_CONFIG_NO_LOGO,
    FAVICON,
    DICT_GROUPBY_LEVELS,
    DICT_FREQ_RESAMPLE,
    PLT_CONFIG,
)

st.set_page_config(
    page_title="PFN | Return Analysis",
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

st.markdown(f"## Correlation of {freq.lower().replace('day','dai')}ly returns")

enhance_corr = st.radio(
    "Kind of correlation to enhance:",
    options=["Positive", "Null", "Negative"],
    horizontal=True,
)

df_rets = get_period_returns(
    df=df_common_history.loc[first_day:last_day, :],
    df_registry=df_registry,
    period=DICT_FREQ_RESAMPLE[freq],
    level=DICT_GROUPBY_LEVELS[level],
)

# import plotly.express as px
# from utils import get_rolling_returns

# df = df_common_history.loc[first_day:last_day, :].ffill()
# df_rr = get_rolling_returns(df, 60)

# # st.write(df_rr)
# st.plotly_chart(px.line(df_rr[["LCWD.MI", "SGLD.MI"]]))

fig = plot_correlation_map(
    df=df_rets.corr(),
    enhance_correlation=enhance_corr.lower(),
    lower_triangle_only=True,
)
st.plotly_chart(fig, use_container_width=True, config=PLT_CONFIG_NO_LOGO)

st.markdown("***")

st.markdown(f"## Distribution of {freq.lower().replace('day','dai')}ly returns")

default_objs = df_rets.columns.to_list()
cols = st.multiselect(
    f"Choose the {level.lower()} to display:",
    options=default_objs,
    default=default_objs[1],
    key="sel_lev_1",
)

annotation_list = [
    f"<b>{col_}</b> ⟶ excess kurtosis: {df_rets[col_].kurtosis().round(1)}, skewness: {df_rets[col_].skew().round(1)}"
    for col_ in cols
]

fig = plot_returns(df=df_rets[cols], annotation_text="<br>".join(annotation_list))
st.plotly_chart(fig, use_container_width=True, config=PLT_CONFIG)

write_disclaimer()
