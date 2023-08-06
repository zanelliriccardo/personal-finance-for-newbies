from pathlib import Path
from datetime import datetime, timedelta
from typing import Tuple, Dict, List, Literal

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

from var import CACHE_EXPIRE_SECONDS


@st.cache_data(show_spinner=False)
def load_data(full_path: Path) -> Tuple[pd.DataFrame, pd.DataFrame]:
    df_storico = pd.read_excel(
        full_path,
        sheet_name="Transactions History",
        dtype={
            "Exchange": str,
            "Ticker": str,
            "Shares": int,
            "Price (€)": float,
            "Fees (€)": float,
        },
    ).rename(
        columns={
            "Exchange": "exchange",
            "Ticker": "ticker",
            "Transaction Date": "transaction_date",
            "Shares": "shares",
            "Price (€)": "price",
            "Fees (€)": "fees",
        }
    )
    df_storico["ap_amount"] = df_storico["shares"] * df_storico["price"]
    df_storico["ticker_yf"] = df_storico["ticker"] + "." + df_storico["exchange"]

    df_anagrafica = pd.read_excel(
        full_path, sheet_name="Securities Master Table", dtype=str
    ).rename(
        columns={
            "Exchange": "exchange",
            "Ticker": "ticker",
            "Security Name": "name",
            "Asset Class": "asset_class",
            "Macro Asset Class": "macro_asset_class",
        }
    )
    df_anagrafica["ticker_yf"] = (
        df_anagrafica["ticker"] + "." + df_anagrafica["exchange"]
    )

    write_load_message(df_data=df_storico, df_dimensions=df_anagrafica)
    return df_storico, df_anagrafica


def write_load_message(df_data: pd.DataFrame, df_dimensions: pd.DataFrame) -> None:
    n_transactions = df_data.shape[0]
    n_tickers = df_data["ticker"].nunique()
    min_date, max_date = (
        str(df_data["transaction_date"].min())[:10],
        str(df_data["transaction_date"].max())[:10],
    )
    set_data_tickers = sorted(df_data["ticker"].unique())
    set_dimensions_tickers = sorted(df_dimensions["ticker"].unique())
    n_data_na = df_data.isnull().sum().sum()
    n_dimensions_na = df_dimensions.isnull().sum().sum()

    if n_data_na > 0 or n_dimensions_na > 0:
        st.error(
            f"There are null values: {n_data_na} among transactions, {n_dimensions_na} among tickers' descriptions"
        )

    if set_data_tickers != set_dimensions_tickers:
        st.warning(
            "There is some inconsistency between the tickers traded and the tickers' descriptions"
        )

    st.success(
        f"Successfully loaded **{n_transactions} transactions** relating to **{n_tickers} tickers** and spanning from {min_date} to {max_date}"
    )


@st.cache_data(show_spinner=False)
def aggregate_by_ticker(df: pd.DataFrame, in_pf_only: bool = False) -> pd.DataFrame:
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
    for i, ticker_ in zip(range(len(ticker_list)), ticker_list):
        ticker_data = yf.Ticker(ticker_)
        try:
            closing_date_ = (
                ticker_data.history(
                    period="1d",
                    interval="1d",
                )["Close "]
                .reset_index()
                .values.tolist()
            )
            df_last_closing.iloc[i] = [ticker_] + closing_date_[0]
        except:
            try:
                closing_date_ = get_last_closing_price_from_api(ticker=ticker_)
                df_last_closing.iloc[i] = [ticker_] + closing_date_[0]
            except:
                st.error(
                    f"{ticker_}: latest data not available. Please check your internet connection or try again later",
                    icon="😔",
                )

    df_last_closing["last_closing_date"] = (
        df_last_closing["last_closing_date"].astype(str).str.slice(0, 10)
    )

    return df_last_closing


@st.cache_data(ttl=CACHE_EXPIRE_SECONDS, show_spinner=False)
def get_last_closing_price_from_api(ticker: str, days_of_delay: int = 5) -> List:
    today = datetime.utcnow()
    delayed = today - timedelta(days=days_of_delay)

    period1 = int(delayed.timestamp())
    period2 = int(datetime.utcnow().timestamp())

    link = f"https://query1.finance.yahoo.com/v7/finance/download/{ticker}?period1={period1}&period2={period2}&interval=1d&events=history&includeAdjustedClose=true"

    try:
        closing_date = pd.read_csv(link, usecols=["Date", "Adj Close"]).rename(
            {"Adj Close": "Close"}
        )
        closing_date["Date"] = pd.to_datetime(closing_date["Date"])
        closing_date = closing_date.head(1).values.tolist()
    except:
        closing_date = None

    return closing_date


@st.cache_data(ttl=CACHE_EXPIRE_SECONDS, show_spinner=False)
def get_full_price_history(ticker_list: List[str]) -> Dict:
    df_history = dict()

    for i, ticker_ in zip(range(len(ticker_list)), ticker_list):
        ticker_data = yf.Ticker(ticker_)
        df_history[ticker_] = ticker_data.history(period="max", interval="1d",)[
            "Close"
        ].rename(ticker_)

        df_history[ticker_].index = pd.to_datetime(df_history[ticker_].index.date)

    return df_history


@st.cache_data(ttl=CACHE_EXPIRE_SECONDS, show_spinner=False)
def get_max_common_history(ticker_list: List[str]) -> pd.DataFrame:
    full_history = get_full_price_history(ticker_list)
    df_full_history = pd.concat(
        [full_history[t_] for t_ in ticker_list],
        axis=1,
    )
    first_idx = df_full_history.apply(pd.Series.first_valid_index).max()
    return df_full_history.loc[first_idx:]


@st.cache_data(ttl=10 * CACHE_EXPIRE_SECONDS, show_spinner=False)
def get_risk_free_rate_last_value(decimal: bool = False) -> float:
    try:
        df_ecb = pd.read_html(
            io="http://www.ecb.europa.eu/stats/financial_markets_and_interest_rates/euro_short-term_rate/html/index.en.html"
        )[0]
        risk_free_rate = df_ecb.iloc[0, 1].astype(float)
    except:
        risk_free_rate = 3
    if decimal:
        risk_free_rate = risk_free_rate / 100
    return risk_free_rate


@st.cache_data(ttl=10 * CACHE_EXPIRE_SECONDS, show_spinner=False)
def get_risk_free_rate_history(decimal: bool = False) -> pd.DataFrame:
    euro_str_link = "https://sdw.ecb.europa.eu/quickviewexport.do?SERIES_KEY=438.EST.B.EU000A2X2A25.WT&type=csv"
    try:
        df_ecb = (
            pd.read_csv(
                euro_str_link,
                sep=",",
                skiprows=5,
                index_col=0,
            )
            .drop(columns="obs. status")
            .rename(columns={"Unnamed: 1": "euro_str"})
        ).sort_index()
    except:
        df_ecb = pd.DataFrame()
    if decimal:
        df_ecb["euro_str"] = df_ecb["euro_str"].div(100)
    return df_ecb


@st.cache_data(ttl=10 * CACHE_EXPIRE_SECONDS, show_spinner=False)
def sharpe_ratio(
    returns: pd.Series, trading_days: int, risk_free_rate: float = 3
) -> float:
    mean = returns.mean() * trading_days - risk_free_rate
    std = returns.std() * np.sqrt(trading_days)
    return mean / std


# def sortino_ratio(series, N, rf):
#     mean = series.mean() * N -rf
#     std_neg = series[series<0].std()*np.sqrt(N)
#     return mean/std_neg

# def max_drawdown(return_series):
#     comp_ret = (return_series+1).cumprod()
#     peak = comp_ret.expanding(min_periods=1).max()
#     dd = (comp_ret/peak)-1
#     return dd.min()


@st.cache_data(ttl=10 * CACHE_EXPIRE_SECONDS, show_spinner=False)
def get_wealth_history(
    df_transactions: pd.DataFrame, df_prices: pd.DataFrame
) -> pd.Series:
    ticker_list = df_prices.columns.to_list()
    df_transactions = df_transactions[df_transactions["ticker_yf"].isin(ticker_list)]

    begin_date = df_transactions["transaction_date"].min()
    today = datetime.now().date()
    date_range = pd.date_range(start=begin_date, end=today, freq="D")

    df_asset_allocation = pd.DataFrame(
        index=date_range,
        columns=ticker_list,
        data=0,
    )

    for (data, ticker), group in df_transactions.groupby(
        ["transaction_date", "ticker_yf"]
    ):
        total_shares = group["shares"].sum()
        df_asset_allocation.loc[data, ticker] += total_shares
    df_asset_allocation = df_asset_allocation.cumsum()

    df_wealth = pd.DataFrame(
        df_asset_allocation.multiply(df_prices.loc[begin_date:])
        .fillna(method="ffill")
        .sum(axis=1)
        .rename("ap_daily_value")
    )
    df_wealth["diff_previous_day"] = df_wealth.diff()

    return df_wealth


@st.cache_data(ttl=10 * CACHE_EXPIRE_SECONDS, show_spinner=False)
def get_portfolio_pivot(
    df: pd.DataFrame,
    df_dimensions: pd.DataFrame,
    pf_actual_value: float,
    aggregation_level: Literal["ticker", "asset_class", "macro_asset_class"],
) -> pd.DataFrame:
    if aggregation_level == "ticker":
        groupby_keys = [
            "macro_asset_class",
            "asset_class",
            "ticker_yf",
            "name",
        ]
    elif aggregation_level == "asset_class":
        groupby_keys = [
            "macro_asset_class",
            "asset_class",
        ]
    elif aggregation_level == "macro_asset_class":
        groupby_keys = "macro_asset_class"
    df_pivot = (
        df.copy()
        .merge(df_dimensions, how="left", on="ticker_yf")
        .groupby(groupby_keys)["position_value"]
        .sum()
        .reset_index()
    )
    df_pivot["weight_pf"] = (
        (100 * df_pivot["position_value"].div(pf_actual_value)).astype(float).round(1)
    )
    df_pivot["position_value"] = df_pivot["position_value"].astype(float).round(1)
    return df_pivot


@st.cache_data(ttl=10 * CACHE_EXPIRE_SECONDS, show_spinner=False)
def get_pnl_by_asset_class(
    df: pd.DataFrame,
    df_dimensions: pd.DataFrame,
    group_by: Literal["asset_class", "macro_asset_class"],
) -> pd.DataFrame:
    df_pnl = df.merge(df_dimensions, how="left", on="ticker_yf")
    df_pnl["pnl"] = np.round(
        ((df_pnl["price"] - df_pnl["dca"]) * df_pnl["shares"]).astype(float), 1
    )
    df_pnl = df_pnl.groupby(group_by)["pnl"].sum().reset_index().sort_values([group_by])
    return df_pnl


def write_disclaimer() -> None:
    st.markdown("***")
    st.markdown(
        '<center> <span style="font-size:0.7em; font-style:italic">\
        This content is for educational purposes only and is under no circumstances intended\
        to be used or considered as financial or investment advice\
        </span> </center>',
        unsafe_allow_html=True,
    )


@st.cache_data(ttl=CACHE_EXPIRE_SECONDS, show_spinner=False)
def get_daily_returns(
    df: pd.DataFrame,
    df_registry: pd.DataFrame,
    level: Literal["ticker", "asset_class", "macro_asset_class"],
):
    df_daily_rets = df.pct_change()[1:]

    if level == "ticker":
        return df_daily_rets
    else:
        classes = df_registry[level].unique()
        df_daily_rets_classes = pd.DataFrame(columns=classes)
        for class_ in classes:
            cols_to_sum = df_registry[df_registry[level].eq(class_)][
                "ticker_yf"
            ].to_list()

            df_daily_rets_classes[class_] = df_daily_rets[cols_to_sum].sum(axis=1)
        return df_daily_rets_classes


@st.cache_data(ttl=CACHE_EXPIRE_SECONDS, show_spinner=False)
def get_drawdown(df: pd.DataFrame) -> pd.DataFrame:
    df = df.fillna(0.0)
    cumulative_rets = (df + 1).cumprod()
    running_max = np.maximum.accumulate(cumulative_rets)
    return (cumulative_rets - running_max).div(running_max)


def get_max_dd(df: pd.DataFrame):
    return get_drawdown(df).min()
