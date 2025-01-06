#########################
# Datadog Instrumentation
#########################
from ddtrace import patch_all, tracer
from ddtrace.contrib.logging import patch as log_patch

# Patch all supported integrations
patch_all()
# Patch logging to include Datadog trace details
log_patch()

import logging
import os

#########################
# Logging Configuration
#########################
log_file = os.path.join(os.getcwd(), 'kunal_data.log')

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [service=%(dd.service)s] [trace_id=%(dd.trace_id)s] [span_id=%(dd.span_id)s] [source=python] - %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

# Adjust log levels if desired
logging.getLogger("ddtrace").setLevel(logging.INFO)
logging.getLogger("datadog").setLevel(logging.INFO)

# Create a logger for this module
logger = logging.getLogger(__name__)

# Optionally, set a default service name for Datadog
tracer.set_tags({"service.name": "kunal_data_service"})

#########################
# Original Code
#########################
import sys
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

# tickers = ["AAPL", "TSLA", "MSFT"] #this will be gathered from sidebar eventually

def gatherData(tickers, alpaca_api_key, alpaca_secret_key):
    """
    Gathers historical data from Alpaca for the specified tickers.
    """
    # Wrap function with a Datadog trace
    with tracer.trace("gatherData", service="kunal_data_service"):
        logger.info("Gathering data from Alpaca API.")

        today = date.today()
        timeframe = "1Day"
        start = pd.Timestamp(today - DateOffset(years=5), tz="America/New_York").isoformat()
        end = pd.Timestamp(today, tz="America/New_York").isoformat()

        # Create the Alpaca API object
        alpaca = tradeapi.REST(
            alpaca_api_key,
            alpaca_secret_key,
            api_version="v2"
        )

        df_portfolio_year = alpaca.get_bars(
            tickers,
            timeframe,
            start
        ).df

        logger.info("Data gathering complete.")
        return df_portfolio_year

def concatDataframes(tickers_dfs, tickers):
    """
    Concatenates individual ticker DataFrames into a multi-level DataFrame.
    """
    # Wrap function with a Datadog trace
    with tracer.trace("concatDataframes", service="kunal_data_service"):
        logger.info("Concatenating DataFrames.")
        df_portfolio_year = pd.concat(tickers_dfs, axis=1, keys=tickers)
        df_portfolio_year = df_portfolio_year.fillna(0)
        logger.info("DataFrames concatenated successfully.")
        return df_portfolio_year

def createSignals(tickers_dfs, comp_df):
    """
    Creates buy/sell signals based on SMA crossovers and the provided comparison dataframe.
    """
    with tracer.trace("createSignals", service="kunal_data_service"):
        logger.info("Creating trading signals.")
        signals_dfs = []
        short_window = 50
        long_window = 100

        # index for retrieving projected close from price summary
        index = 0

        tomorrow = dt.date.today() + DateOffset(days=1)
        tomorrow = tomorrow.date()

        for ticker in tickers_dfs:
            # Grab index (date) and close from each df
            ticker = ticker.reset_index()
            ticker = ticker.loc[:, ["index", "close"]].copy()

            # Add projected close to dataframe
            ticker.loc[len(ticker)] = [tomorrow, comp_df.iloc[index]["Actual Price"]]
            ticker = ticker.set_index("index")

            # increment index
            index += 1

            # Make the short and long moving averages
            ticker["Short_SMA"] = ticker["close"].rolling(window=short_window).mean()
            ticker["Long_SMA"] = ticker["close"].rolling(window=long_window).mean()

            # Add signal column
            ticker["Signal"] = 0.0

            # Generate the trading signals
            ticker["Signal"][short_window:] = np.where(
                ticker["Short_SMA"][short_window:] > ticker["Long_SMA"][short_window:], 1.0, 0.0
            )

            # Use signals to determine when to trade
            ticker["Entry/Exit"] = ticker["Signal"].diff()

            # Add to signals list
            signals_dfs.append(ticker)

        logger.info("Returning signals DataFrames.")
        return signals_dfs