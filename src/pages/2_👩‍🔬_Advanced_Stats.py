import streamlit as st

from var import (
    GLOBAL_STREAMLIT_STYLE,
    PLT_CONFIG_NO_LOGO,
    FAVICON,
    DICT_GROUPBY_LEVELS,
    PLT_CONFIG,
)

from utils import (
    get_max_common_history,
    write_disclaimer,
    get_daily_returns,
    get_drawdown,
)

from plot import plot_correlation_map, plot_daily_returns

st.set_page_config(
    page_title="PFN | Advanced Stats",
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

col_l_up, col_r_up = st.columns([0.5, 1], gap="small")

level = col_l_up.radio(
    label="Aggregate by:",
    options=["Macro Asset Classes", "Asset Classes", "Tickers"],
    horizontal=True,
    index=2,
)

col_r_up.markdown("")
first_transaction = df_transactions["transaction_date"].sort_values().values[0]
first_day, last_day = col_r_up.select_slider(
    "Select a time slice:",
    options=df_common_history.index,
    value=[first_transaction, df_common_history.index[-1]],
    format_func=lambda value: str(value)[:10],
    label_visibility="collapsed",
)

st.markdown("***")

st.markdown("## Correlation of daily returns")

enhance_corr = st.radio(
    "Kind of correlation to enhance:",
    options=["Positive", "Null", "Negative"],
    horizontal=True,
)

df_daily_rets = get_daily_returns(
    df=df_common_history.loc[first_day:last_day, :],
    df_registry=df_registry,
    level=DICT_GROUPBY_LEVELS[level],
)

fig = plot_correlation_map(
    df=df_daily_rets.corr(),
    enhance_correlation=enhance_corr.lower(),
    lower_triangle_only=True,
)
st.plotly_chart(fig, use_container_width=True, config=PLT_CONFIG_NO_LOGO)

st.markdown("***")

st.markdown("## Distribution of daily returns")

default_objs = df_daily_rets.columns.to_list()
cols = st.multiselect(
    f"Choose the {level.lower()} to display:",
    options=default_objs,
    default=default_objs[1],
)

annotation_list = [
    f"<b>{col_}</b> ⟶ excess kurtosis: {df_daily_rets[col_].kurtosis().round(1)}, skewness: {df_daily_rets[col_].skew().round(1)}"
    for col_ in cols
]

fig = plot_daily_returns(
    df=df_daily_rets[cols], annotation_text="<br>".join(annotation_list)
)
st.plotly_chart(fig, use_container_width=True, config=PLT_CONFIG)

df_dd = get_drawdown(df_daily_rets[cols])

import plotly.express as px
from utils import get_max_dd

fig = px.area(data_frame=df_dd)
st.plotly_chart(fig, use_container_width=True, config=PLT_CONFIG)

st.write(get_max_dd(df_daily_rets))

#################################

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

write_disclaimer()
