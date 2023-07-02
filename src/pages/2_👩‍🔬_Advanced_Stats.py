import streamlit as st

from var import (
    GLOBAL_STREAMLIT_STYLE,
    # PLT_CONFIG,
    # PLT_CONFIG_NO_LOGO,
    FAVICON,
)

# from utils import (
#     sharpe_ratio,
#     get_risk_free_rate_last_value,
#     get_risk_free_rate_history,
# )

st.set_page_config(
    page_title="PFN | Advanced Stats",
    page_icon=FAVICON,
    layout="wide",
    initial_sidebar_state="auto",
)

st.markdown(GLOBAL_STREAMLIT_STYLE, unsafe_allow_html=True)
st.warning("Work in progress! Please, come back later", icon="🚧")

# df_common_history = get_max_common_history(ticker_list=ticker_list)

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
