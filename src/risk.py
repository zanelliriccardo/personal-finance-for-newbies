from typing import Literal

import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf

from var import CACHE_EXPIRE_SECONDS, TRADING_DAYS_YEAR

import pandas as pd
import numpy as np

# 1. Sharpe Ratio
@st.cache_data(ttl=CACHE_EXPIRE_SECONDS, show_spinner=False)
def sharpe_ratio(returns: pd.Series, risk_free_rate: float = 3, trading_days: int = 252) -> float:
    mean_return = returns.mean() * trading_days
    std_dev = returns.std() * np.sqrt(trading_days)
    return (mean_return - risk_free_rate) / std_dev if std_dev != 0 else np.nan

# 2. Sortino Ratio
@st.cache_data(ttl=CACHE_EXPIRE_SECONDS, show_spinner=False)
def sortino_ratio(returns: pd.Series, risk_free_rate: float = 3, trading_days: int = 252) -> float:
    downside = returns[returns < 0].std() * np.sqrt(trading_days)
    mean_return = returns.mean() * trading_days
    return (mean_return - risk_free_rate) / downside if downside != 0 else np.nan

# 3. Calmar Ratio
@st.cache_data(ttl=CACHE_EXPIRE_SECONDS, show_spinner=False)
def calmar_ratio(returns: pd.Series, trading_days: int = 252) -> float:
    annualized_return = returns.mean() * trading_days
    max_dd = get_max_dd(returns)
    return annualized_return / abs(max_dd) if max_dd != 0 else np.nan

# 4. Max Drawdown
@st.cache_data(ttl=CACHE_EXPIRE_SECONDS, show_spinner=False)
def get_max_dd(returns: pd.Series) -> float:
    cumulative = (1 + returns).cumprod()
    drawdown = cumulative / cumulative.cummax() - 1
    return drawdown.min()

# 5. Volatility
@st.cache_data(ttl=CACHE_EXPIRE_SECONDS, show_spinner=False)
def volatility(returns: pd.Series, trading_days: int = 252) -> float:
    return returns.std() * np.sqrt(trading_days)

# 6. Annualized Return
@st.cache_data(ttl=CACHE_EXPIRE_SECONDS, show_spinner=False)
def annualized_return(returns: pd.Series, trading_days: int = 252) -> float:
    return returns.mean() * trading_days

# 7. Downside Deviation
@st.cache_data(ttl=CACHE_EXPIRE_SECONDS, show_spinner=False)
def downside_deviation(returns: pd.Series, trading_days: int = 252) -> float:
    downside = returns[returns < 0]
    return downside.std() * np.sqrt(trading_days)

# 8. Pain Index
@st.cache_data(ttl=CACHE_EXPIRE_SECONDS, show_spinner=False)
def pain_index(returns: pd.Series, trading_days: int = 252) -> float:
    downside = returns[returns < 0]
    return downside.sum() / trading_days

# 9. Value at Risk (VaR)
@st.cache_data(ttl=CACHE_EXPIRE_SECONDS, show_spinner=False)
def value_at_risk(returns: pd.Series, confidence_level: float = 0.05) -> float:
    return np.percentile(returns, 100 * confidence_level)

# 10. Conditional Value at Risk (CVaR)
@st.cache_data(ttl=CACHE_EXPIRE_SECONDS, show_spinner=False)
def conditional_value_at_risk(returns: pd.Series, confidence_level: float = 0.05) -> float:
    var = value_at_risk(returns, confidence_level)
    return returns[returns <= var].mean()

@st.cache_data(ttl=CACHE_EXPIRE_SECONDS, show_spinner=False)
def compute_metrics(
    df_returns: pd.DataFrame, 
    risk_free_rate: float = yf.Ticker("^IRX").history(period="1y").Close.mean(),
    trading_days: int = 252
) -> pd.DataFrame:
    metrics = {}

    daily_risk_free_rate = risk_free_rate / 100 / trading_days

    df_returns.to_excel('df_returns.xlsx')
    for col in df_returns.columns:
        returns = df_returns[col]
        metrics[col] = {
            "Sharpe Ratio": sharpe_ratio(returns, daily_risk_free_rate, trading_days),
            "Sortino Ratio": sortino_ratio(returns, daily_risk_free_rate, trading_days),
            "Volatility": volatility(returns, trading_days),
            "Max Drawdown %": get_max_dd(returns) * 100,
            "Calmar Ratio": calmar_ratio(returns, trading_days),
            "Annualized Return %": annualized_return(returns, trading_days) * 100,
            "Downside Deviation": downside_deviation(returns, trading_days),
            "Pain Index": pain_index(returns, trading_days),
            "Value at Risk (VaR)": value_at_risk(returns, confidence_level=0.05) * 100,
            "Conditional VaR (CVaR)": conditional_value_at_risk(returns, confidence_level=0.05) * 100,
        }

    return pd.DataFrame(metrics).T


# 1. Sharpe Ratio (Rolling)
@st.cache_data(ttl=CACHE_EXPIRE_SECONDS, show_spinner=False)
def rolling_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 3, trading_days: int = 252, window: int = 21) -> pd.Series:
    """Calculate rolling Sharpe ratio."""
    excess_returns = returns - (risk_free_rate / 100 / trading_days)
    rolling_mean = excess_returns.rolling(window).mean() * trading_days
    rolling_std = returns.rolling(window).std() * np.sqrt(trading_days)
    return rolling_mean / rolling_std


# 2. Sortino Ratio (Rolling)
@st.cache_data(ttl=CACHE_EXPIRE_SECONDS, show_spinner=False)
def rolling_sortino_ratio(returns: pd.Series, risk_free_rate: float = 3, trading_days: int = 252, window: int = 21) -> pd.Series:
    """Calculate rolling Sortino ratio."""
    downside = returns[returns < 0]
    downside_rolling_std = downside.rolling(window).std() * np.sqrt(trading_days)
    rolling_mean = returns.rolling(window).mean() * trading_days
    return (rolling_mean - risk_free_rate / 100) / downside_rolling_std


# 3. Calmar Ratio (Rolling)
@st.cache_data(ttl=CACHE_EXPIRE_SECONDS, show_spinner=False)
def rolling_calmar_ratio(returns: pd.Series, trading_days: int = 252, window: int = 21) -> pd.Series:
    """Calculate rolling Calmar ratio."""
    rolling_return = returns.rolling(window).mean() * trading_days
    rolling_max_dd = returns.rolling(window).apply(get_max_dd)
    return rolling_return / abs(rolling_max_dd)


# 4. Max Drawdown (Rolling)
@st.cache_data(ttl=CACHE_EXPIRE_SECONDS, show_spinner=False)
def rolling_get_max_dd(returns: pd.Series) -> float:
    cumulative = (1 + returns).cumprod()
    drawdown = cumulative / cumulative.cummax() - 1
    return drawdown.min()

@st.cache_data(ttl=CACHE_EXPIRE_SECONDS, show_spinner=False)
def rolling_max_drawdown_rolling(returns: pd.Series, window: int = 21) -> pd.Series:
    """Calculate rolling Max Drawdown."""
    return returns.rolling(window).apply(get_max_dd)


# 5. Volatility (Rolling)
@st.cache_data(ttl=CACHE_EXPIRE_SECONDS, show_spinner=False)
def rolling_volatility(returns: pd.Series, trading_days: int = 252, window: int = 21) -> pd.Series:
    """Calculate rolling volatility."""
    return returns.rolling(window).std() * np.sqrt(trading_days)


# 6. Annualized Return (Rolling)
@st.cache_data(ttl=CACHE_EXPIRE_SECONDS, show_spinner=False)
def rolling_annualized_return(returns: pd.Series, trading_days: int = 252, window: int = 21) -> pd.Series:
    """Calculate rolling annualized return."""
    return returns.rolling(window).mean() * trading_days


# 7. Downside Deviation (Rolling)
@st.cache_data(ttl=CACHE_EXPIRE_SECONDS, show_spinner=False)
def rolling_downside_deviation(returns: pd.Series, trading_days: int = 252, window: int = 21) -> pd.Series:
    """Calculate rolling downside deviation."""
    downside = returns[returns < 0]
    return downside.rolling(window).std() * np.sqrt(trading_days)

# 8. Pain Index (Rolling)
@st.cache_data(ttl=CACHE_EXPIRE_SECONDS, show_spinner=False)
def rolling_pain_index(returns: pd.Series, trading_days: int = 252, window: int = 21) -> pd.Series:
    """Calculate rolling pain index."""
    downside = returns[returns < 0]
    return downside.rolling(window).sum() / trading_days

@st.cache_data(ttl=CACHE_EXPIRE_SECONDS, show_spinner=False)
def compute_rolling_metrics(
    df_returns: pd.DataFrame, 
    risk_free_rate: float = 3, 
    trading_days: int = 252,
    window: int = 21  # Rolling window in terms of days
) -> pd.DataFrame:
    """Compute rolling metrics for each asset in the DataFrame."""
    metrics = {}

    for col in df_returns.columns:
        returns = df_returns[col]
        metrics[col] = {
            "Sharpe Ratio": rolling_sharpe_ratio(returns, risk_free_rate, trading_days, window),
            "Sortino Ratio": rolling_sortino_ratio(returns, risk_free_rate, trading_days, window),
            "Volatility": rolling_volatility(returns, trading_days, window),
            "Max Drawdown": rolling_max_drawdown_rolling(returns, window),
            "Calmar Ratio": rolling_calmar_ratio(returns, trading_days, window),
            "Annualized Return": rolling_annualized_return(returns, trading_days, window),
            "Downside Deviation": rolling_downside_deviation(returns, trading_days, window),
            "Pain Index": rolling_pain_index(returns, trading_days, window),
        }

    reshaped_metrics = []
    # Iterate over the dictionary to reshape data
    for asset, metric_values in metrics.items():
        for metric, values in metric_values.items():
            for date_index, value in enumerate(values):
                reshaped_metrics.append({
                    'Asset': asset,
                    'Date': date_index,  # Assuming date as index (0, 1, ...)
                    'Metric': metric,
                    'Value': value
                })

    df = pd.DataFrame(reshaped_metrics)
    # Pivot to required format: index as (Asset, Date), columns as Metric, values as Value
    df_pivoted = df.pivot(index=['Asset', 'Date'], columns='Metric', values='Value').reset_index()
    df_pivoted.to_excel('df_metrics_pivoted.xlsx')

    return df_pivoted

@st.cache_data(ttl=CACHE_EXPIRE_SECONDS, show_spinner=False)
def get_drawdown(df: pd.DataFrame) -> pd.DataFrame:
    df = df.fillna(0.0)
    cumulative_rets = (df + 1).cumprod()
    running_max = cumulative_rets.cummax()
    return (cumulative_rets - running_max).div(running_max)


def get_max_dd(df: pd.DataFrame) -> float:
    return get_drawdown(df).min()


def get_portfolio_variance(
    weights: pd.Series, returns: pd.DataFrame, trading_days=TRADING_DAYS_YEAR
) -> float:
    return trading_days * np.dot(weights.T, np.dot(returns.cov(), weights))


def get_relative_risk_contributions(
    weights: pd.Series, returns: pd.DataFrame
) -> pd.Series:
    volatility = np.sqrt(get_portfolio_variance(weights, returns))
    covariance = returns.cov()
    marginal_vols = np.dot(covariance, weights) / volatility
    risk_contrib = marginal_vols * weights
    relative_risk_contrib = risk_contrib / risk_contrib.sum()
    return relative_risk_contrib


def get_portfolio_relative_risk_contribution(
    df_prices: pd.DataFrame,
    df_shares: pd.DataFrame,
    df_registry: pd.DataFrame,
    level: Literal["ticker", "asset_class", "macro_asset_class"],
) -> pd.DataFrame:
    df_log_rets = np.log(df_prices.div(df_prices.shift())).fillna(0)
    if level == "ticker":
        # Log-returns
        df_rets = df_log_rets
        # Weights
        df_weights = df_prices.tail(1).T.merge(
            df_shares, left_index=True, right_index=True
        )
        df_weights.columns = ["last_price", "shares"]
        df_weights["total_invested"] = df_weights["last_price"] * df_weights["shares"]
        df_weights["pf_weight"] = df_weights["total_invested"].div(
            df_weights["total_invested"].sum()
        )
    else:
        classes = df_registry[level].unique()
        df_rets = pd.DataFrame(columns=classes)
        df_weights = pd.DataFrame(columns=["total_invested"])
        # Log-returns & weights per class
        for class_ in classes:
            # Tickers belonging to class_
            cols_to_sum = df_registry[df_registry[level].eq(class_)][
                "ticker_yf"
            ].to_list()
            # Log-return of class_
            df_rets[class_] = df_log_rets[cols_to_sum].sum(axis=1)
            # Weight of class_
            df_ = (
                df_prices[cols_to_sum]
                .tail(1)
                .T.merge(df_shares.loc[cols_to_sum], left_index=True, right_index=True)
            )
            df_.columns = ["last_price", "shares"]
            df_["total_invested"] = df_["last_price"] * df_["shares"]
            df_weights.loc[class_] = df_["total_invested"].sum()
        df_weights["pf_weight"] = df_weights["total_invested"].div(
            df_weights["total_invested"].sum()
        )

    df = pd.DataFrame(
        get_relative_risk_contributions(df_weights["pf_weight"], df_rets).rename(
            "relative_risk_contribution"
        )
    ).merge(df_weights["pf_weight"], right_index=True, left_index=True)

    return df
