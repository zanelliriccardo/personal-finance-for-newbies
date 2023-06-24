from pathlib import Path
from typing import Tuple, Dict, List

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

from var import CACHE_EXPIRE_SECONDS


@st.cache_data(show_spinner=False)
def load_data(full_path: Path) -> Tuple[pd.DataFrame, pd.DataFrame]:
    df_storico = pd.read_excel(
        full_path,
        sheet_name="Storico",
        dtype={
            "Borsa": str,
            "Ticker": str,
            "Quote": int,
            "Prezzo (€)": float,
            "Commissioni": float,
        },
    ).rename(
        columns={
            "Borsa": "exchange",
            "Ticker": "ticker",
            "Data Operazione": "transaction_date",
            "Quote": "shares",
            "Prezzo (€)": "price",
            "Commissioni (€)": "fees",
        }
    )

    df_anagrafica = pd.read_excel(
        full_path, sheet_name="Anagrafica Titoli", dtype=str
    ).rename(
        columns={
            "Ticker": "ticker",
            "Nome ETF": "name",
            "Tipologia": "asset_class",
            "Macro Tipologia": "macro_asset_class",
        }
    )

    return df_storico, df_anagrafica


@st.cache_data(show_spinner=False)
def aggregate_by_ticker(df: pd.DataFrame, in_pf_only: bool = False) -> pd.DataFrame:
    df["ap_amount"] = df["shares"] * df["price"]
    df["ticker_yf"] = df["ticker"] + "." + df["exchange"]

    df_portfolio = (
        df.groupby("ticker_yf")
        .agg(
            shares=("shares", "sum"),
            ap_amount=("ap_amount", "sum"),
            fees=("fees", "sum"),
        )
        .reset_index()
        .sort_values(
            "shares",
            ascending=False,
        )
    )

    df_portfolio["is_in_pf"] = df_portfolio["shares"].ne(0)

    df_portfolio["dca"] = np.where(
        df_portfolio["is_in_pf"].eq(True),
        df_portfolio["ap_amount"].div(df_portfolio["shares"]),
        0,
    )

    if in_pf_only:
        df_portfolio = df_portfolio[df_portfolio["is_in_pf"].eq(True)]

    return df_portfolio.drop(columns="is_in_pf").reset_index(drop=True)


@st.cache_data(ttl=CACHE_EXPIRE_SECONDS, show_spinner=False)
def get_last_closing_price(ticker_list: List[str]) -> pd.DataFrame:
    df_last_closing = pd.DataFrame(
        columns=["ticker_yf", "last_closing_date", "price"],
        index=range(len(ticker_list)),
    )
    try:
        for i, ticker_ in zip(range(len(ticker_list)), ticker_list):
            ticker_data = yf.Ticker(ticker_)
            closing_date_ = (
                ticker_data.history(
                    period="1d",
                    interval="1d",
                )["Close"]
                .reset_index()
                .values.tolist()
            )

            df_last_closing.iloc[i] = [ticker_] + closing_date_[0]

        df_last_closing["last_closing_date"] = (
            df_last_closing["last_closing_date"].astype(str).str.slice(0, 10)
        )
    except:
        st.error('Data not available. Please check your internet connection or try again later', icon='😔')
        st.stop()

    return df_last_closing


@st.cache_data(ttl=CACHE_EXPIRE_SECONDS, show_spinner=False)
def get_full_price_history(ticker_list: List[str]) -> Dict:
    df_history = dict()

    for i, ticker_ in zip(range(len(ticker_list)), ticker_list):
        ticker_data = yf.Ticker(ticker_)
        df_history[ticker_] = ticker_data.history(
            period="max",
            interval="1d",
        )[
            "Close"
        ].rename(ticker_)

        df_history[ticker_].index = pd.to_datetime(df_history[ticker_].index.date)

    return df_history

@st.cache_data(ttl=10*CACHE_EXPIRE_SECONDS, show_spinner=False)
def get_risk_free_rate() -> float:
    try:
        df_ecb = pd.read_html(io='http://www.ecb.europa.eu/stats/financial_markets_and_interest_rates/euro_short-term_rate/html/index.en.html')[0]
        risk_free_rate = df_ecb.iloc[0,1].astype(float)
    except:
        risk_free_rate = 3
    return risk_free_rate