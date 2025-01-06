#########################
# Datadog Instrumentation
#########################
from ddtrace import tracer, patch_all
import logging
from ddtrace.contrib.logging import patch as log_patch

# Enable Datadog tracing and logging
patch_all()
log_patch()

# Configure logging (console + correlation)
# logging.basicConfig(
#     level=logging.DEBUG,
#     format=(
#         "%(asctime)s [%(levelname)s] [service=%(dd.service)s] "
#         "[trace_id=%(dd.trace_id)s] [span_id=%(dd.span_id)s] "
#         "[source=python] - %(message)s"
#     )
# )
# logger = logging.getLogger(__name__)

FORMAT = ('%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] '
          '[dd.service=%(dd.service)s dd.env=%(dd.env)s dd.version=%(dd.version)s dd.trace_id=%(dd.trace_id)s dd.span_id=%(dd.span_id)s] '
          '- %(message)s')
logging.basicConfig(format=FORMAT)
logger = logging.getLogger(__name__)
logger.level = logging.INFO

# Set Datadog global tags (optionally rename the service if you like)
tracer.set_tags({"service.name": "robo_advisor"})

#########################
# Standard Imports
#########################
import os
from dotenv import load_dotenv
import pandas as pd
import alpaca_trade_api as tradeapi
from pandas.tseries.offsets import DateOffset
import datetime as dt
from prophet import Prophet  # PyStan backend is used by default

# Load environment variables
load_dotenv()

#########################
# Core Code
#########################

@tracer.wrap("forecast_next_day")
def forecast_next_day(tickers, inputdata):
    """
    Given a list of tickers and historical data, this function uses
    the Prophet model to predict the next day's closing price.
    """
    logger.info("Starting forecast_next_day for tickers: %s", tickers)
    
    results_df = pd.DataFrame()

    for ticker in tickers:
        with tracer.trace("forecasting.ticker", resource=ticker) as span:
            logger.info("Processing ticker: %s", ticker)
            
            try:
                # Prepare data for Prophet
                stock_df = pd.DataFrame(
                    inputdata.loc[inputdata["symbol"] == ticker]["close"]
                )
                stock_df = stock_df.reset_index().rename(
                    columns={"index": "ds", "close": "y"}
                )
                
                logger.debug("Training Prophet model for ticker: %s", ticker)
                model = Prophet()
                model.fit(stock_df)
                
                # Forecast next day's price
                future = model.make_future_dataframe(periods=1, freq="D")
                forecast = model.predict(future)
                logger.debug("Forecast completed for ticker: %s", ticker)
                
                # Extract results
                forecast_yhats = forecast[["yhat", "yhat_lower", "yhat_upper"]].tail(1).values[0]
                new_row = pd.DataFrame([{
                    "ticker": ticker,
                    "yhat": forecast_yhats[0],
                    "yhat_lower": forecast_yhats[1],
                    "yhat_upper": forecast_yhats[2]
                }])
                results_df = pd.concat([results_df, new_row], ignore_index=True)
            
            except Exception as e:
                logger.error("Error processing ticker %s: %s", ticker, str(e))
                span.set_tag("error", True)
                span.set_tag("error.msg", str(e))
    
    logger.info("Completed forecast_next_day for tickers: %s", tickers)
    return results_df


@tracer.wrap("compare_prices")
def compare_prices(results_df, df):
    """
    Compares the Prophet-forecasted prices (from results_df) to the expected
    prices (from df), returning a DataFrame that shows the actual, best,
    and worst prices for each ticker.
    """
    logger.info("Starting compare_prices")
    
    comp_df = pd.DataFrame(columns=["Tickers", "Actual Price", "Best Price", "Worst Price"])
    
    # Loop through each row in df (user's expected price data)
    for i in range(len(df)):
        symbol = df.loc[i, "Symbol"]
        expected_price = df.loc[i, "expectedprice"]
        best_price = df.loc[i, "expectedprice-high"]
        worst_price = df.loc[i, "expectedprice-low"]
        
        # Find the matching ticker forecast in results_df
        for j in range(len(results_df)):
            if results_df.loc[j, "ticker"] == symbol:
                predicted_price = results_df.loc[j, "yhat"]
                yhat_best = results_df.loc[j, "yhat_upper"]
                yhat_worst = results_df.loc[j, "yhat_lower"]
                
                # Decide if we should use user's expected price or Prophet's predicted price
                if predicted_price > expected_price:
                    new_row = pd.DataFrame([{
                        "Tickers": symbol,
                        "Actual Price": expected_price,
                        "Best Price": best_price,
                        "Worst Price": worst_price
                    }])
                else:
                    new_row = pd.DataFrame([{
                        "Tickers": symbol,
                        "Actual Price": predicted_price,
                        "Best Price": yhat_best,
                        "Worst Price": yhat_worst
                    }])
                
                comp_df = pd.concat([comp_df, new_row], ignore_index=True)

    logger.info("Completed compare_prices")
    return comp_df