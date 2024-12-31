#########################
# Datadog Instrumentation
#########################
from ddtrace import patch_all, tracer
from ddtrace.contrib.logging import patch as log_patch

# Patch supported modules (requests, etc.) and logging
patch_all()
log_patch()

import logging
import os

# Configure logging for Datadog correlation
log_file = os.path.join(os.getcwd(), "functions_service.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] "
           "[dd.service=%(dd.service)s] "
           "[dd.trace_id=%(dd.trace_id)s] "
           "[dd.span_id=%(dd.span_id)s] "
           "[source=python] - %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

# Optionally set log levels for ddtrace/datadog
logging.getLogger("ddtrace").setLevel(logging.INFO)
logging.getLogger("datadog").setLevel(logging.INFO)

# Create a logger for this module
logger = logging.getLogger(__name__)

# Optionally set a default service name for these traces
tracer.set_tags({"service.name": "functions_service"})

#########################
# Original Imports
#########################
import pandas as pd
from pathlib import Path
import plotly.express as px
from datetime import date, timedelta
import alpaca_trade_api as tradeapi
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

#########################
# Instrumented Functions
#########################

def get_cleaned_tickers(csv_path):
    """Returns a list of 'Ticker - Name' entries for a dropdown menu."""
    with tracer.trace("get_cleaned_tickers", service="functions_service"):
        logger.info("Reading tickers from CSV and cleaning data.")
        nyse_tickers = pd.read_csv(Path(csv_path))
        nyse_tickers['Symbol'] = nyse_tickers['Symbol'].astype(str)

        # Remove tickers containing '^' for data cleansing and Alpaca API compatibility
        nyse_tickers = nyse_tickers[~nyse_tickers['Symbol'].str.contains('\^')]

        # Create a new column with "Symbol - Name"
        nyse_tickers['Symbol_Name'] = nyse_tickers['Symbol'] + ' - ' + nyse_tickers['Name']

        # Convert the 'Symbol_Name' column to a list and return
        cleaned_tickers = nyse_tickers['Symbol_Name'].tolist()
        logger.info("Returning cleaned list of tickers.")
        return cleaned_tickers

def portfolio_breakdown(csv_path, weights):
    """Returns three pie charts (by Sector, by Industry, by Stock) based on portfolio tickers and their weights."""
    with tracer.trace("portfolio_breakdown", service="functions_service"):
        logger.info("Generating portfolio breakdown pie charts.")
        tickers_csv = pd.read_csv(Path(csv_path))
        tickers_csv['Symbol'] = tickers_csv['Symbol'].astype(str)

        # Remove tickers containing '^'
        tickers_csv = tickers_csv[~tickers_csv['Symbol'].str.contains('\^')]

        # Create a DataFrame from the weights dict and merge with CSV
        portfolio_df = pd.DataFrame(weights.items(), columns=['Symbol', 'Weight'])
        merged_df = pd.merge(portfolio_df, tickers_csv, on='Symbol')

        # Create pie charts with Plotly
        fig1 = px.pie(merged_df, values='Weight', names='Sector', title='by Sector', height=350, width=500)
        fig2 = px.pie(merged_df, values='Weight', names='Industry', title='by Industry', height=350, width=500)
        fig3 = px.pie(merged_df, values='Weight', names='Symbol', title='by Stock', height=350, width=500)

        logger.info("Returning sector, industry, and stock composition charts.")
        return fig1, fig2, fig3

def plot_close_prices(ticker_keys, concat_market_data, selected_period):
    """
    Returns a Plotly line chart showing the historical close prices for the specified
    period of time for all tickers in ticker_keys.
    """
    with tracer.trace("plot_close_prices", service="functions_service"):
        logger.info("Plotting close prices for selected period.")
        # Convert index to tz-naive
        concat_market_data.index = concat_market_data.index.tz_localize(None)

        today = date.today()
        start_date = today - timedelta(days=selected_period)

        # Filter the DataFrame for the selected time period
        df_period = concat_market_data.loc[start_date:]

        # Concatenate only the 'close' columns
        close_df = pd.concat([df_period.loc[:, (ticker, 'close')] for ticker in ticker_keys], axis=1)
        close_df = close_df.droplevel(axis=1, level=1)

        close_plot = px.line(
            close_df,
            labels={'variable': 'Ticker', 'value': 'Closing Price (USD)', 'timestamp': 'Date'}
        )
        logger.info("Returning close prices line chart.")
        return close_plot

def get_closing_prices(tickers, api_key, secret_key):
    """Returns a DataFrame of the most recent closing prices for the specified tickers."""
    with tracer.trace("get_closing_prices", service="functions_service"):
        logger.info("Fetching latest closing prices via Alpaca API.")
        api = tradeapi.REST(api_key, secret_key)
        barsets = api.get_bars(tickers, '1D').df
        barsets = barsets.set_index('symbol').rename_axis('Ticker')

        barsets = barsets.drop(columns=['open', 'high', 'low','volume', 'trade_count', 'vwap'])
        barsets = barsets.rename(columns={'close':'Closing Price (USD)'})

        logger.info("Returning DataFrame of current closing prices.")
        return barsets

def get_news_headlines(tickers, api_key, secret_key):
    """Retrieves one news article for each ticker and displays it using Streamlit."""
    with tracer.trace("get_news_headlines", service="functions_service"):
        logger.info("Fetching news headlines for selected tickers.")
        api = tradeapi.REST(api_key, secret_key)

        for ticker in tickers:
            news = api.get_news(ticker, limit=1)
            if news:
                item = news[0]
                # Streamlit calls for display
                st.write(ticker)
                st.caption(item.headline)
                st.markdown(item.url, unsafe_allow_html=True)

        logger.info("Completed fetching and displaying news headlines.")

def robo_graphs(signals_dfs, tickers):
    """
    Returns a dictionary of Plotly figures showing buy/sell signals,
    short/long SMAs, and stock price lines for each ticker.
    """
    with tracer.trace("robo_graphs", service="functions_service"):
        logger.info("Constructing robo advisor charts with buy/sell signals.")
        charts = {}
        index = 0

        for ticker in signals_dfs:
            # Buy timing
            buy_points = ticker[ticker["Entry/Exit"] == 1.0]["close"]
            entry = go.Scatter(
                x=buy_points.index,
                y=buy_points,
                name="Buy",
                mode="markers",
                marker=dict(color="green", symbol="triangle-up", size=10)
            )

            # Sell timing
            sell_points = ticker[ticker["Entry/Exit"] == -1.0]["close"]
            exit = go.Scatter(
                x=sell_points.index,
                y=sell_points,
                name="Sell",
                mode="markers",
                marker=dict(color="red", symbol="triangle-down", size=10)
            )

            # Stock price
            security_close = go.Scatter(
                x=ticker.index,
                y=ticker["close"],
                name="Close",
                mode="lines",
                line=dict(color="lightgray")
            )

            # Moving averages
            moving_avgs = go.Scatter(
                x=ticker.index,
                y=ticker["Short_SMA"],
                name="Short SMA",
                mode="lines",
                line=dict(color="blue")
            )
            moving_avgs2 = go.Scatter(
                x=ticker.index,
                y=ticker["Long_SMA"],
                name="Long SMA",
                mode="lines",
                line=dict(color="orange")
            )

            # Create subplot with 2 rows, 1 column
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05)

            # Add traces
            fig.add_trace(security_close, row=1, col=1)
            fig.add_trace(moving_avgs, row=1, col=1)
            fig.add_trace(moving_avgs2, row=1, col=1)
            fig.add_trace(entry, row=1, col=1)
            fig.add_trace(exit, row=1, col=1)

            # Update layout
            fig.update_layout(title=tickers[index], height=800, width=1000, showlegend=False)
            fig.update_yaxes(title_text="Price (usd)", row=1, col=1)
            fig.update_xaxes(title_text="Date")

            charts[tickers[index]] = fig
            index += 1

        logger.info("Returning dictionary of robo advisor charts.")
        return charts