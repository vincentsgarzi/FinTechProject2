import sys
import os

print(os.getcwd())

os.chdir("../Kunal")
sys.path.append(os.getcwd())
from app import PriceSummary

import pandas as pd
import numpy as np
import alpaca_trade_api as tradeapi
import datetime as dt
from dotenv import load_dotenv
from datetime import date, timedelta
from pathlib import Path
from pandas import DateOffset


# Load .env environment variables
load_dotenv('api.env')

# Set Alpaca API key and secret
alpaca_api_key = os.getenv("ALPACA_API_KEY")
alpaca_secret_key = os.getenv("ALPACA_SECRET_KEY")

#tickers = ["AAPL", "TSLA", "MSFT"] #this will be gathered from sidebar eventually

def gatherData(tickers, alpaca_api_key, alpaca_secret_key):
  tickers_dfs = []

  today = date.today()
  timeframe = "1Day"
  start = pd.Timestamp(today - DateOffset(years=5), tz="America/New_York").isoformat()
  end = pd.Timestamp(today, tz="America/New_York").isoformat()

  # Create the Alpaca API object
  alpaca = tradeapi.REST(
  alpaca_api_key,
  alpaca_secret_key,
  api_version="v2")

  df_portfolio_year = alpaca.get_bars(
      tickers,
      timeframe,
      start = start
  ).df

  for ticker in tickers:
      ticker = df_portfolio_year[df_portfolio_year['symbol']==ticker].drop('symbol', axis=1)
      tickers_dfs.append(ticker)
  return tickers_dfs

def concatDataframes(tickers_dfs, tickers):
  df_portfolio_year = pd.concat(tickers_dfs,axis=1, keys=tickers)
  df_portfolio_year = df_portfolio_year.fillna(0)
  return df_portfolio_year

def createSignals(tickers_dfs, priceSummary):
  # new list for signals and such
  signals_dfs = []

  # Set the short window and long windows
  short_window = 50
  long_window = 100

  # index for gathering projected close from proce summary
  index = 0

  tomorrow = dt.date.today() + DateOffset(days=1)
  tomorrow = tomorrow.date()

  print(tomorrow)

  for ticker in tickers_dfs:
    # Grab index (date) and close from each df

    ticker = ticker.reset_index()
    print(ticker)

    ticker = ticker.loc[:,["timestamp", "close"]].copy()
    ticker.loc[len(ticker)] = [tomorrow, priceSummary.iloc[index]["expectedprice"]]

    # ticker.index=pd.to_datetime(ticker.index).date

    print(ticker)
    # add projected close to dataframe

    # increment index
    index = index + 1

    # Make the short and long moving averages
    ticker["Short_SMA"] = ticker["close"].rolling(window=short_window).mean()
    ticker["Long_SMA"] = ticker["close"].rolling(window=long_window).mean()

    # add signal column
    ticker["Signal"] = 0.0

    # generate the trading signals
    ticker["Signal"][short_window:] = np.where(
        ticker["Short_SMA"][short_window:] > ticker["Long_SMA"][short_window:], 1.0, 0.0)

    # use signals to determine when to trade
    ticker["Entry/Exit"] = ticker["Signal"].diff()

    # add to signals list
    signals_dfs.append(ticker)

  return signals_dfs

alpaca=tradeapi.REST(alpaca_api_key,alpaca_secret_key,api_version="v2")

# Set start and end dates of 3 years back from your current date
# Alternatively, you can use an end date of 2020-08-07 and work 3 years back from that date
import datetime as dt
from pandas.tseries.offsets import DateOffset

today= dt.date.today() #- DateOffset(days=1)
start= today - DateOffset(years=5)
start_date=start.date()
timeframe='1Day'

tickers = ["AAPL", "TSLA"] #this will be gathered from sidebar eventually

tickers_dfs = []

timeframe = "1Day"

df_portfolio_year = alpaca.get_bars(
    tickers,
    timeframe,
    start = start_date
).df

#Reformatting the index
df_portfolio_year.index=pd.to_datetime(df_portfolio_year.index).date

print(createSignals(gatherData(tickers, alpaca_api_key, alpaca_secret_key), PriceSummary(df_portfolio_year)))
