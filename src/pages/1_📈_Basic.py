import streamlit as st

from var import GLOBAL_STREAMLIT_STYLE  # , FAVICON
from utils import aggregate_by_ticker, get_last_closing_price
from plot import plot_sunburst

st.set_page_config(
    page_title="PFN | Basic",
    # page_icon=FAVICON,
    layout="wide",
    initial_sidebar_state="auto",
)

st.markdown(GLOBAL_STREAMLIT_STYLE, unsafe_allow_html=True)

if "data" in st.session_state:
    df_storico = st.session_state["data"]
    df_anagrafica = st.session_state["dimensions"]
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

col_l, col_r = st.columns([1, 1], gap="small")

consider_fees = st.checkbox("Take fees into account")

pf_actual_value = (df_j["shares"] * df_j["price"]).sum()
if consider_fees:
    pnl = pf_actual_value - expense - fees
    pnl_perc = 100 * (pf_actual_value - expense - fees) / expense
else:
    pnl = pf_actual_value - expense
    pnl_perc = 100 * (pf_actual_value - expense) / expense
sign = "+" if pnl >= 0 else "-"

col_l.metric(
    label="Actual Portfolio Value",
    value=f"{pf_actual_value: .1f} €",
    delta=f"{pnl: .1f} € ({sign}{pnl_perc: .1f}%)",
)

df_j["ticker"] = df_j["ticker_yf"].str.split(".").str[0]
df_j["position_value"] = df_j["shares"] * df_j["price"]
df_pivot = (
    df_j.merge(df_anagrafica, how="left", on="ticker")
    .groupby(
        [
            "macro_asset_class",
            "asset_class",
            "ticker",
            "name",
        ]
    )["position_value"]
    .sum()
    .reset_index()
)
df_pivot["weight_pf"] = (
    (100 * df_pivot["position_value"].div(pf_actual_value)).astype(float).round(1)
)

st.markdown("## Portfolio asset allocation")
fig = plot_sunburst(df=df_pivot)
st.plotly_chart(fig, use_container_width=True)
