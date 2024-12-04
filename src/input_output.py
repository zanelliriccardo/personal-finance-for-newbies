from pathlib import Path
from datetime import datetime, timedelta
from typing import Tuple, Dict, List

import streamlit as st
import yfinance as yf
import pandas as pd

from var import CACHE_EXPIRE_SECONDS


def write_disclaimer() -> None:
    st.markdown("***")
    st.markdown(
        '<center> <span style="font-size:0.7em; font-style:italic">\
        This content is for educational purposes only and is under no circumstances intended\
        to be used or considered as financial or investment advice\
        </span> </center>',
        unsafe_allow_html=True,
    )


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
        st.stop()

    if set_data_tickers != set_dimensions_tickers:
        st.warning(
            "There is some inconsistency between the tickers traded and the tickers' descriptions"
        )

    st.success(
        f"Successfully loaded **{n_transactions} transactions** relating to **{n_tickers} tickers** and spanning from {min_date} to {max_date}"
    )



def load_data(full_path: Path) -> Tuple[pd.DataFrame, pd.DataFrame]:
    df_storico = pd.read_excel(
        full_path,
        sheet_name="Transactions History",
        dtype={
            "Exchange": str,
            "Ticker": str,
            "Shares": float,
            "Price (€)": float,
            "Fees (€)": float,
            "Amount (€)": float,
        },
    ).rename(
        columns={
            "Exchange": "exchange",
            "Ticker": "ticker",
            "Transaction Date": "transaction_date",
            "Shares": "shares",
            "Price (€)": "price",
            "Fees (€)": "fees",
            "Amount (€)": "ap_amount",
        }
    )
    # filter out tickers that start with ^
    df_storico = df_storico[~df_storico["ticker"].str.startswith("^")]

    df_storico['exchange'] = df_storico['exchange'].fillna('')
    df_storico["ticker_yf"] = df_storico.apply(
        lambda x: x["ticker"] + "." + x["exchange"] if x["exchange"] != '' else x["ticker"],
        axis=1,
    )

    df_anagrafica = pd.read_excel(
        full_path, sheet_name="Securities Master Table", dtype=str
    ).rename(
        columns={
            "Exchange": "exchange",
            "Ticker": "ticker",
            "Security Name": "name",
            "Asset Class": "asset_class",
            "Macro Asset Class": "macro_asset_class",
            "Sector_url": "sector_url",
        }
    )
    # filter out tickers that start with ^
    df_anagrafica = df_anagrafica[~df_anagrafica["ticker"].str.startswith("^")]
    # add the exchange to the ticker to match the yfinance format if exchange is not empty
    df_anagrafica = df_anagrafica.fillna("")
    df_anagrafica["ticker_yf"] = df_anagrafica.apply(
        lambda x: x["ticker"] + "." + x["exchange"] if x["exchange"] != '' else x["ticker"],
        axis=1,
    )

    # Drop columns not belonging to the excel tables
    df_storico = df_storico.drop(
        columns=[col_ for col_ in df_storico.columns if col_.startswith("Unnamed")]
    )
    df_storico.to_excel("df_storico.xlsx", index=False)
    df_anagrafica.to_excel("df_anagrafica.xlsx", index=False)
    write_load_message(df_data=df_storico, df_dimensions=df_anagrafica)
    return df_storico, df_anagrafica



def get_last_closing_price(ticker_list: List[str]) -> pd.DataFrame:
    df_last_closing = pd.DataFrame(
        columns=["ticker_yf", "last_closing_date", "price"],
        index=range(len(ticker_list)),
    )
    for i, ticker_ in zip(range(len(ticker_list)), ticker_list):
        print(f"Processing {ticker_}")
        ticker_data = (
            yf.Ticker(ticker_)
        )
        try:
            closing_date_ = (
                ticker_data.history(
                    period="1d",
                    interval="1d",
                )["Close"]
                .reset_index()
                .values.tolist()
            )
            df_last_closing.iloc[i] = [ticker_] + closing_date_[0]
        except:
            try:
                closing_date_ = (
                    ticker_data.history(
                        period="1mo",
                        interval="1d",
                    )["Close"]
                    .reset_index()
                    .values.tolist()
                )
                df_last_closing.iloc[i] = [ticker_] + closing_date_[-1]
            except:
                try:
                    closing_date_ = get_last_closing_price_from_api(ticker=ticker_)
                    df_last_closing.iloc[i] = [ticker_] + closing_date_[0]
                except:
                    print(f'Error in {ticker_}')
                    st.error(
                        f"{ticker_}: latest data not available. Please check your internet connection or try again later",
                        icon="😔",
                    )

    df_last_closing["last_closing_date"] = (
        df_last_closing["last_closing_date"].astype(str).str.slice(0, 10)
    )

    return df_last_closing



def get_last_closing_price_from_api(ticker: str, days_of_delay: int = 5) -> List:
    today = datetime.utcnow()
    delayed = today - timedelta(days=days_of_delay)

    period1 = int(delayed.timestamp())
    period2 = int(datetime.utcnow().timestamp())

    
    try:
        link = f"https://query1.finance.yahoo.com/v7/finance/download/{ticker}?period1={period1}&period2={period2}&interval=1d&events=history&includeAdjustedClose=true"
        closing_date = pd.read_csv(link, usecols=["Date", "Adj Close"]).rename(
            {"Adj Close": "Close"}
        )
        closing_date["Date"] = pd.to_datetime(closing_date["Date"])
        closing_date = closing_date.head(1).values.tolist()
    except:
        try:
            link = f"https://query1.finance.yahoo.com/v7/finance/download/{ticker}?period1={period1}&period2={period2}&interval=1mo&events=history&includeAdjustedClose=true"
            closing_date = pd.read_csv(link, usecols=["Date", "Close"])
            closing_date["Date"] = pd.to_datetime(closing_date["Date"])
            closing_date = closing_date.head(1).values.tolist()
        except:
            closing_date = None

    return closing_date



def get_full_price_history(ticker_list: List[str]) -> Dict:
    df_history = dict()

    for ticker_ in ticker_list:
        ticker_data = yf.Ticker(ticker_)
        df_history[ticker_] = ticker_data.history(
            period="max",
            interval="1d",
        )[
            "Close"
        ].rename(ticker_)

        df_history[ticker_].index = pd.to_datetime(df_history[ticker_].index.date)

    return df_history



def get_max_common_history(ticker_list: List[str]) -> pd.DataFrame:
    full_history = get_full_price_history(ticker_list)
    df_full_history = pd.concat(
        [full_history[t_] for t_ in ticker_list],
        axis=1,
    )
    first_idx = df_full_history.apply(pd.Series.first_valid_index).max()
    last_idx = df_full_history.apply(pd.Series.last_valid_index).min()
    return df_full_history.loc[first_idx:last_idx]


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


def get_summary(df_storico, df_anagrafica):
    # df_storico contains the historical transactions
    # df_anagrafica contains the asset information

    # compute # of shares for each asset
    number_of_shares = df_storico.groupby("ticker_yf")["shares"].sum()
    df_anagrafica = df_anagrafica.merge(number_of_shares, left_on="ticker_yf", right_index=True, how="left")

    # compute avg shares cost for each asset weighted by the number of shares
    avg_weighted_cost = (
        df_storico.groupby("ticker_yf")["ap_amount"].sum() / df_storico.groupby("ticker_yf")["shares"].sum()
    ).to_frame("avg_shares_cost")
    df_anagrafica = df_anagrafica.merge(avg_weighted_cost, left_on="ticker_yf", right_index=True, how="left")

    # compute current price for each asset
    last_closing_price = get_last_closing_price(df_anagrafica["ticker_yf"].to_list())
    last_closing_price.rename(columns={"price": "last_closing_price"}, inplace=True)
    df_anagrafica = df_anagrafica.merge(last_closing_price, left_on="ticker_yf", right_on="ticker_yf", how="left")

    # compute total cost for each asset
    total_cost = df_storico.groupby("ticker_yf")["ap_amount"].sum().to_frame("total_cost")
    df_anagrafica = df_anagrafica.merge(total_cost, left_on="ticker_yf", right_index=True, how="left")

    # compute current value for each asset
    print(df_anagrafica)
    df_anagrafica["current_value"] = df_anagrafica["shares"] * df_anagrafica["last_closing_price"]

    # compute total gain/loss for each asset
    df_anagrafica["gain_loss"] = df_anagrafica["current_value"] - df_anagrafica["total_cost"]

    # compute total gain/loss percentage for each asset
    df_anagrafica["gain_loss_perc"] = df_anagrafica["gain_loss"] / df_anagrafica["total_cost"]

    print(df_anagrafica)
    df_anagrafica = df_anagrafica[[
        "ticker_yf",
        "name",
        "shares",
        "avg_shares_cost",
        "total_cost",
        "last_closing_price",
        "current_value",
        "gain_loss",
        "gain_loss_perc",
    ]]

    # Compute a total row for each column
    total_series = [
        "",
        "Total",
        df_anagrafica["shares"].sum(),
        df_anagrafica["avg_shares_cost"].mean(),
        df_anagrafica["total_cost"].sum(),
        df_anagrafica["last_closing_price"].mean(),
        df_anagrafica["current_value"].sum(),
        df_anagrafica["gain_loss"].sum(),
        df_anagrafica["gain_loss"].sum() / df_anagrafica["total_cost"].sum(),
    ]
    df_anagrafica.loc["Total"] = total_series

    return df_anagrafica
    

# Future projections setup with Plotly
def simulate_future_growth(initial_wealth, annualised_return, inflation, monthly_investment, years, increase_investment):
    # Calculate the number of months
    months = years * 12
    future_wealth = []
    wealth_without_investment = []
    annualised_return_adjusted = annualised_return - inflation

    for month in range(months):
        # Calculate the future wealth with investment each month with annualised return adjusted for inflation
        current_wealth = initial_wealth if month == 0 else future_wealth[-1]
        future_wealth.append(
            current_wealth * (1 + annualised_return_adjusted / 12) + monthly_investment
        )

        # Calculate the future wealth without investment each month with inflation
        current_wealth_without_investment = initial_wealth if month == 0 else wealth_without_investment[-1]
        wealth_without_investment.append(
            current_wealth_without_investment * (1 - inflation / 12) + monthly_investment
        )
        
        # Increase the monthly investment every 5 years (60 months)
        increase_interval_years = 5
        if (month + 1) % (increase_interval_years * 12) == 0 and month > 0:
            monthly_investment *= (1 + increase_investment)

    return future_wealth, wealth_without_investment