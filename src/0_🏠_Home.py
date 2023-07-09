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
    "You can **download** a template, **fill** it in with your accumulation plan's buy/sell transactions, and **upload** it:",
    unsafe_allow_html=True,
)
col_ll, col_l, col_c, col_r, col_rr = st.columns([0.6, 1, 0.6, 1, 0.6], gap="small")
with open(DATA_PATH / Path("demo.xlsx"), "rb") as f:
    col_l.download_button(
        "Download Template",
        data=f,
        file_name="template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
if col_r.button("Upload your Data"):
    uploaded_file = st.file_uploader(label="", label_visibility="collapsed")
    if uploaded_file is not None:
        col_r.write("You selected the file:", uploaded_file.name)

st.markdown("##")
st.markdown(
    "If you wish to **explore** the app first, upload some **demo data** instead:",
    unsafe_allow_html=True,
)
col_ll_mid, col_l_mid, col_c_mid, col_r_mid, col_rr_mid = st.columns(
    [0.6, 1, 0.6, 1, 0.6], gap="small"
)
col_l_mid.button(label="Load Mock Data", key="load_mock_df")

if st.session_state.get("load_mock_df"):
    df_storico, df_anagrafica = load_data(DATA_PATH / Path("demo.xlsx"))
    st.session_state["data"] = df_storico
    st.session_state["dimensions"] = df_anagrafica

write_disclaimer()
