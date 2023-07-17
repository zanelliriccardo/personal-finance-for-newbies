from pathlib import Path

import streamlit as st

from utils import load_data, write_disclaimer
from var import (
    GLOBAL_STREAMLIT_STYLE,
    DATA_PATH,
    FAVICON,
)

st.set_page_config(
    page_title="PFN",
    page_icon=FAVICON,
    layout="wide",
    initial_sidebar_state="auto",
)

st.markdown(GLOBAL_STREAMLIT_STYLE, unsafe_allow_html=True)

st.title("Welcome to Personal Finance for Newbies!")

st.markdown(
    "PFN is a web app that – from buy/sell financial asset transactions – provides easy-to-use, \
    near-real-time statistics (*i.e.*, updated to the last closing) on your investment portfolio."
)
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

write_disclaimer()
