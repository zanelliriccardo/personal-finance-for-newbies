from pathlib import Path

import streamlit as st

from utils import load_data
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

st.title("Personal Finance for Newbies")

st.button(label="Load Mock Data", key="load_mock_df")

if st.session_state.get("load_mock_df"):
    df_storico, df_anagrafica = load_data(DATA_PATH / Path("pac.xlsx"))
    st.session_state["data"] = df_storico
    st.session_state["dimensions"] = df_anagrafica
