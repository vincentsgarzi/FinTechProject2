import sys
import os

# os.chdir("../Kunal")
# sys.path.append(os.getcwd())
# from app import PriceSummary

import pandas as pd
import numpy as np
import alpaca_trade_api as tradeapi
import datetime as dt
from dotenv import load_dotenv
from datetime import date, timedelta
from pathlib import Path
from pandas import DateOffset

import warnings
warnings.filterwarnings("ignore")

# Load .env environment variables
load_dotenv('api.env')

# Set Alpaca API key and secret
alpaca_api_key = os.getenv("ALPACA_API_KEY")
alpaca_secret_key = os.getenv("ALPACA_SECRET_KEY")

#tickers = ["AAPL", "TSLA", "MSFT"] #this will be gathered from sidebar eventually

def gatherData(tickers, alpaca_api_key, alpaca_secret_key):

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
      start
  ).df

  return df_portfolio_year

def concatDataframes(tickers_dfs, tickers):
  df_portfolio_year = pd.concat(tickers_dfs,axis=1, keys=tickers)
  df_portfolio_year = df_portfolio_year.fillna(0)
  return df_portfolio_year

def createSignals(tickers_dfs, comp_df):
  # new list for signals and such
  signals_dfs = []

  # Set the short window and long windows
  short_window = 50
  long_window = 100

  # index for gathering projected close from proce summary
  index = 0

  tomorrow = dt.date.today() + DateOffset(days=1)
  tomorrow = tomorrow.date()

  for ticker in tickers_dfs:
    # Grab index (date) and close from each df
    ticker = ticker.reset_index()
    ticker = ticker.loc[:,["index", "close"]].copy()

    # add projected close to dataframe
    ticker.loc[len(ticker)] = [tomorrow, comp_df.iloc[index]["Actual Price"]]
    ticker = ticker.set_index('index')

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

  print("returning signals dfs")
  return signals_dfs

