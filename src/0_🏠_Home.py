from pathlib import Path

import streamlit as st

from input_output import load_data, write_disclaimer
from var import GLOBAL_STREAMLIT_STYLE, DATA_PATH, FAVICON, APP_VERSION, COVER

st.set_page_config(
    page_title="PFN",
    page_icon=FAVICON,
    layout="wide",
    initial_sidebar_state="auto",
)

st.markdown(GLOBAL_STREAMLIT_STYLE, unsafe_allow_html=True)

st.title(f"Welcome to Personal Finance for Newbies!")
st.text(f"v{APP_VERSION}")

col_l, col_r = st.columns([0.8, 1], gap="large")

col_r.markdown(
    """
    Personal Finance for Newbies (or PFN) is a web app that – from buy/sell
    financial asset transactions – provides easy-to-use, near-real-time statistics
    (*i.e.*, updated to the last closing) on your investment portfolio.
    <br><br>
    PFN allows you to analyse your portfolio from multiple perspectives:
    from higher-level metrics (profit & loss, asset class weights) to those
    allowing you to study risk and returns in depth, especially over time.
    To use the app, you don't need to create an account! You just need to set up a file
    (see the template below) containing your buy/sell transactions. PFN takes care of
    downloading historical prices from [Yahoo Finance](https://finance.yahoo.com/)
    and analysing them for you.
    <br><br>
    We do not collect or store any data. Nor do we provide any guarantee of the accuracy
    of the results displayed, which are intended for educational and informational
    purposes only. The project is open source and we always look for pull requests,
    if you know better!
    <br><br>
    <i>Someone's sitting in the shade today because someone planted a tree
    a long time ago</i> (W. Buffet)
    """,
    unsafe_allow_html=True,
)
col_l.image(COVER)

st.markdown("***")

st.markdown("## Let's get started")
st.markdown(
    "To load your data, fill in the template with your accumulation plan's buy/sell transactions and upload it here:",
    unsafe_allow_html=True,
)
col_l, col_r = st.columns([1, 0.8], gap="small")

uploaded_file = col_l.file_uploader(
    label="Upload your Data",
    label_visibility="collapsed",
)
if uploaded_file is not None:
    try:
        df_storico, df_anagrafica = load_data(uploaded_file)
        st.session_state["data"] = df_storico
        st.session_state["dimensions"] = df_anagrafica
    except:
        st.error("Please check your file format and make sure it matches the template")
        st.stop()

with open(DATA_PATH / Path("template.xlsx"), "rb") as f:
    col_l.download_button(
        "Download Template",
        data=f,
        file_name="template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

st.markdown("##")
st.markdown(
    "If you wish to **explore** the app first, load some **demo data** instead:",
    unsafe_allow_html=True,
)

if st.button(label="Load Mock Data", key="load_mock_df"):
    df_storico, df_anagrafica = load_data(DATA_PATH / Path("demo.xlsx"))
    st.session_state["data"] = df_storico
    st.session_state["dimensions"] = df_anagrafica
    st.switch_page("pages/1_🎯_Asset_Allocation_&_PnL.py")

# st.page_link(
#     "pages/1_🎯_Asset_Allocation_&_PnL.py", label="Asset Allocation & PnL", icon="🎯"
# )

# TODO add links with short descriptions

write_disclaimer()
