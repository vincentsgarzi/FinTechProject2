import streamlit as st
import pandas as pd
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi
from pandas.tseries.offsets import DateOffset
import datetime as dt
import hvplot.pandas
import os
import plotly as px



def portfolio_returns(inputdata,tickers,weights, init_investment):
    closing_prices_df = pd.DataFrame()
    for ticker in tickers:
        closing_prices_df[ticker] = inputdata[ticker]["close"]
    closing_prices_df.index = closing_prices_df.index
    daily_returns = closing_prices_df.pct_change().dropna()
    weighted_returns = daily_returns * weights
    
    # Calculate daily portfolio returns
    inputdata["portfolio_daily_return"] = weighted_returns.sum(axis=1)
    
    # Calculate cumulative portfolio returns
    inputdata["cumulative_return"] = (1 + inputdata["portfolio_daily_return"]).cumprod()
    
    # Calculate portfolio value
    inputdata["portfolio_value"] = (inputdata["cumulative_return"] * init_investment)
    
    inputdata = inputdata["portfolio_value"]
            
    return inputdata

   
   
