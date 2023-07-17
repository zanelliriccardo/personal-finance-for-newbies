from typing import Dict, List

import yfinance as yf
import pandas as pd
import numpy as np


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


def get_last_closing_price(ticker_list: List[str]) -> pd.DataFrame:
    df_last_closing = pd.DataFrame(
        columns=["ticker_yf", "last_closing_date", "price"],
        index=range(len(ticker_list)),
    )

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

    return df_last_closing


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
