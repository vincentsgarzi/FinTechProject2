import streamlit as st
import pandas as pd
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi
from pandas.tseries.offsets import DateOffset
import datetime as dt
import os
import plotly.express as px

# Define the function with input arguments: inputdata, ticker, weights, init_investment, selected_period
def portfolio_returns(inputdata, ticker, weights, init_investment, selected_period):
    
    # Get today's date
    today = dt.date.today()
    
    # Calculate the start date for the given period based on the selected_period parameter
    start_date = today - DateOffset(days=selected_period)
    
    # Slice the inputdata to get the data for the selected period
    df_period = inputdata.loc[start_date:]
    
    # Create an empty dataframe to store the closing prices of the given tickers for the selected period
    closing_prices_df = pd.DataFrame()
    
    # Loop through the given tickers and populate the closing_prices_df dataframe with the closing prices for each ticker
    for ticker in tickers:
        closing_prices_df[ticker] = df_period[ticker]["close"]
        
    # Set the index of the closing_prices_df dataframe to match the index of the inputdata
    closing_prices_df.index = closing_prices_df.index
    
    # Calculate the daily returns for the selected period
    daily_returns = closing_prices_df.pct_change().dropna()
    
    # Calculate the weighted returns for each ticker based on the given weights
    weighted_returns = daily_returns * weights
    
    # Calculate the daily portfolio returns by summing the weighted returns across all tickers for each day
    df_period["portfolio_daily_return"] = weighted_returns.sum(axis=1)
    
    # Calculate the cumulative portfolio returns by calculating the product of (1 + daily portfolio return) for each day
    df_period["cumulative_return"] = (1 + df_period["portfolio_daily_return"]).cumprod()
    
    # Calculate the portfolio value for each day by multiplying the cumulative portfolio returns with the initial investment
    df_period["portfolio_value"] = (df_period["cumulative_return"] * init_investment)
    
    # Extract the portfolio_value column from the df_period dataframe and assign it to inputdata
    inputdata = df_period["portfolio_value"]
    
    # Create a line plot of the portfolio value over time using plotly express
    portfolio_plot = px.line(inputdata, x=df_period.index, y='portfolio_value',
                             labels={'variable': 'Ticker', 'value': 'Portfolio Value (USD)', 'timestamp': 'Date'})
   
    # Get the last portfolio value from the inputdata dataframe
    last_value = inputdata.iloc[-1]
    
    # Return the last portfolio value and the portfolio plot
    return last_value, portfolio_plot




   
   
