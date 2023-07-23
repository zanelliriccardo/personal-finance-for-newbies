import streamlit as st

from var import (
    GLOBAL_STREAMLIT_STYLE,
    # PLT_CONFIG,
    PLT_CONFIG_NO_LOGO,
    FAVICON,
)

from utils import (
    get_max_common_history,
    # sharpe_ratio,
    # get_risk_free_rate_last_value,
    # get_risk_free_rate_history,
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

fig = plot_correlation_map(df=df_common_history.corr(), lower_triangle_only=True)
st.plotly_chart(fig, use_container_width=True, config=PLT_CONFIG_NO_LOGO)

# weights = [
#     df_pivot[df_pivot["ticker_yf"].eq(x_)]["weight_pf"].values[0]
#     for x_ in df_common_history.columns
# ]
# weighted_average = pd.Series(np.average(df_common_history, weights=weights, axis=1))

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
