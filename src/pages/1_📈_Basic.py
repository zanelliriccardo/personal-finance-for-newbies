import streamlit as st
import pandas as pd
import numpy as np

from var import GLOBAL_STREAMLIT_STYLE, FAVICON
from utils import aggregate_by_ticker, get_last_closing_price

st.set_page_config(
    page_title="PFN | Basic",
    page_icon=FAVICON,
    layout="wide",
    initial_sidebar_state="auto",
)

st.markdown(GLOBAL_STREAMLIT_STYLE, unsafe_allow_html=True)


if "data" in st.session_state:
    df_storico = st.session_state["data"]
else:
    st.error(
        "Ops... non c'è niente da visualizzare. Passa prima per la 🏠 per caricare i dati"
    )
    st.stop()

df_pf = aggregate_by_ticker(df_storico, in_pf_only=True)

ticker_list = df_pf["ticker_yf"].to_list()
df_last_closing = get_last_closing_price(ticker_list=ticker_list)

df_j = df_pf[["ticker_yf", "dca", "shares"]].merge(
    df_last_closing[["ticker_yf", "price"]], how="left", on="ticker_yf"
)

expense = (df_j["shares"] * df_j["dca"]).sum()
fees = df_storico["fees"].sum().round(2)

st.markdown("## Profit and Loss")

pf_actual_value = (df_j["shares"] * df_j["price"]).sum()
pnl = (pf_actual_value - expense).round(2)
# pnl_perc =
# pnl_fees =
# pnl_fees_perc =

st.metric(
    label="Actual PF Value", value=f"{np.round(pf_actual_value, 2)} €", delta=f"{pnl} €"
)

# np.round(100 * (pf_actual_value - expense) / expense, 1)

# (pf_actual_value - expense - fees).round(2)

# np.round(100 * (pf_actual_value - expense - fees) / expense, 1)
