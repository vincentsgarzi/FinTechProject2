import streamlit as st
import pandas as pd
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi
from pandas.tseries.offsets import DateOffset
import datetime as dt
import hvplot.pandas
import os
import plotly as px



# def portfolio_returns(inputdata,tickers,weights, init_investment,selected_period):
#     closing_prices_df = pd.DataFrame()
#     for ticker in tickers:
#         closing_prices_df[ticker] = inputdata[ticker]["close"]
#     closing_prices_df.index = closing_prices_df.index
#     daily_returns = closing_prices_df.pct_change().dropna()
#     weighted_returns = daily_returns * weights
    
#     # Calculate daily portfolio returns
#     inputdata["portfolio_daily_return"] = weighted_returns.sum(axis=1)
    
#     # Calculate cumulative portfolio returns
#     inputdata["cumulative_return"] = (1 + inputdata["portfolio_daily_return"]).cumprod()
    
#     # Calculate portfolio value
#     inputdata["portfolio_value"] = (inputdata["cumulative_return"] * init_investment)
    
#     inputdata = inputdata["portfolio_value"]
    
#     today = dt.date.today()
#     start_date = today - DateOffset(days=selected_period)
    
#     df_period = inputdata.loc[start_date:]

#     # plot the portfolio value over time
#     portfolio_plot = px.line(df_period, x=df_period.index, y='portfolio_value',
#                              labels={'variable': 'Ticker', 'value': 'Portfolio Value (USD)', 'timestamp': 'Date'})
            
#     return portfolio_plot

def portfolio_returns(inputdata,tickers,weights, init_investment,selected_period):
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
    
    today = dt.date.today()
    start_date = today - DateOffset(days=selected_period)
    
    df_period = inputdata.loc[start_date:]

    # plot the portfolio value over time
    portfolio_plot = px.line(df_period, x=df_period.index, y='portfolio_value',
                             labels={'variable': 'Ticker', 'value': 'Portfolio Value (USD)', 'timestamp': 'Date'})
    
    # get the last portfolio value
    last_value = df_period.iloc[-1]['portfolio_value']
            
    return portfolio_plot, last_value


   
   
