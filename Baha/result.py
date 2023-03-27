from Kunal.app import model_iteration
from Kunal.app import PriceSummary
from fbprophet import forecast_next_day

def forecast_vs_price_summary(ticker, inputdata):
    model_summary = model_iteration(inputdata)

    price_summary = PriceSummary(model_summary)
    print(price_summary)

    # Get forecasted next day price
    forecast_yhat = forecast_next_day(ticker,inputdata)
    print(forecast_yhat)


from dotenv import load_dotenv
import pandas as pd 
import alpaca_trade_api as tradeapi
from prophet import Prophet
import os
from pathlib import Path
from pandas.tseries.offsets import DateOffset
import datetime as dt
import hvplot.pandas


#working on ALPACA api's
load_dotenv()

alpaca_api_key = os.getenv("ALPACA_API_KEY")
alpaca_secret_key = os.getenv("ALPACA_SECRET_KEY")

alpaca = tradeapi.REST(
    alpaca_api_key,
    alpaca_secret_key,
    api_version = "v2"
)



# Creating a start date, and TimeFrame
today = dt.date.today()
start = today - DateOffset(years=5)

start_date = start.date()
end_date = today.isoformat()
timeframe = "1Day"



# initializing the alpaca
tickers = ["AAPL"] #this will be gathered from sidebar eventually
tickers_dfs = []

df_portfolio_year = alpaca.get_bars(
    tickers,
    timeframe,
    start = start_date
).df

df_portfolio_year.index=pd.to_datetime(df_portfolio_year.index).date

    # Compare expected price with forecasted next day price
    
 
forecast_vs_price_summary(tickers, df_portfolio_year)
    
