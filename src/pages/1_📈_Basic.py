import streamlit as st
import pandas as pd

from var import GLOBAL_STREAMLIT_STYLE, FAVICON

st.set_page_config(
    page_title="PFN | Basic",
    page_icon=FAVICON,
    layout="wide",
    initial_sidebar_state="auto",
)

st.markdown(GLOBAL_STREAMLIT_STYLE, unsafe_allow_html=True)


if "data" in st.session_state:
    df_storico = st.session_state["data"]
    st.write(df_storico)
