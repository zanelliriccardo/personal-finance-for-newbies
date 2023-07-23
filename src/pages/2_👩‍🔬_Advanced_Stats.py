import streamlit as st

from var import (
    GLOBAL_STREAMLIT_STYLE,
    # PLT_CONFIG,
    PLT_CONFIG_NO_LOGO,
    FAVICON,
)

from utils import (
    get_max_common_history,
    get_wealth_history,
    write_disclaimer,
)

from plot import plot_correlation_map

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

st.markdown("## Correlation Matrix")

col_l, col_c, col_r = st.columns([1, 0.15, 0.5], gap="small")

first_transaction = df_transactions["transaction_date"].sort_values().values[0]
first_day, last_day = col_l.select_slider(
    "Select a time slice:",
    options=df_common_history.index,
    value=[first_transaction, df_common_history.index[-1]],
    format_func=lambda value: str(value)[:10],
    label_visibility="collapsed",
)

enhance_corr = col_r.radio(
    "Kind of correlation to enhance:",
    options=["Positive", "Null", "Negative"],
    horizontal=True,
)

fig = plot_correlation_map(
    df=df_common_history.loc[first_day:last_day, :].corr(),
    enhance_correlation=enhance_corr.lower(),
    lower_triangle_only=True,
)
st.plotly_chart(fig, use_container_width=True, config=PLT_CONFIG_NO_LOGO)

st.markdown("## Distribution of Daily Returns")

# diff_prev_day = get_wealth_history(
#     df_transactions=df_transactions,
#     df_prices=get_max_common_history(ticker_list=ticker_list),
# )['diff_previous_day']

# import plotly.express as px
# st.plotly_chart(px.histogram(diff_prev_day), use_container_width=True, config=PLT_CONFIG_NO_LOGO)

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
