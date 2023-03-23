import os
import pandas as pd
import numpy as np
import alpaca_trade_api as tradeapi
from dotenv import load_dotenv
from datetime import date
from pathlib import Path
from pandas import DateOffset

# Load .env environment variables
load_dotenv('api.env')

# Set Alpaca API key and secret
alpaca_api_key = os.getenv("ALPACA_API_KEY")
alpaca_secret_key = os.getenv("ALPACA_SECRET_KEY")

tickers = ["AAPL", "TSLA", "MSFT"] #this will be gathered from sidebar eventually

def gatherData(tickers):
  tickers_dfs = []

  today = date.today()
  timeframe = "1Day"
  start = pd.Timestamp(today - DateOffset(years=2), tz="America/New_York").isoformat()
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

def concatDataframes(tickers_dfs):
  df_portfolio_year = pd.concat(tickers_dfs,axis=1, keys=tickers)
  return df_portfolio_year

def createSignals(tickers_dfs):
  # new list for signals and such
  signals_dfs = []

  # Set the short window and long windows
  short_window = 50
  long_window = 100

  for ticker in tickers_dfs:
    # Grab index (date) and close from each df
    ticker = ticker.loc[:, ["close"]].copy()

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

print(createSignals(gatherData(tickers)))
