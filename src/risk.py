import streamlit as st
import pandas as pd
import numpy as np

from var import CACHE_EXPIRE_SECONDS


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


@st.cache_data(ttl=CACHE_EXPIRE_SECONDS, show_spinner=False)
def get_drawdown(df: pd.DataFrame) -> pd.DataFrame:
    df = df.fillna(0.0)
    cumulative_rets = (df + 1).cumprod()
    running_max = cumulative_rets.cummax()
    return (cumulative_rets - running_max).div(running_max)


def get_max_dd(df: pd.DataFrame):
    return get_drawdown(df).min()
