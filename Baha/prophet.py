from dotenv import load_dotenv
import pandas as pd 
import alpaca_trade_api as tradeapi
from prophet import Prophet
import os
from pathlib import Path
from pandas.tseries.offsets import DateOffset
import datetime as dt
from prophet import Prophet
import hvplot.pandas


#working on ALPACA api's
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
tickers = ["AAPL", "TSLA", "MSFT"] #this will be gathered from sidebar eventually
tickers_dfs = []

df_portfolio_year = alpaca.get_bars(
    tickers,
    timeframe,
    start = start_date
).df

df_portfolio_year.index=pd.to_datetime(df_portfolio_year.index).date

# Initializing facebook prophet library
def forecast_next_day(ticker):
        stock_df = pd.DataFrame(df_portfolio_year.loc[df_portfolio_year["symbol"] == ticker]["close"])
        stock_df = stock_df.reset_index().rename(columns={"index": "ds", "close": "y"})
        model = Prophet()
        model.fit(stock_df)
        future = model.make_future_dataframe(periods=1, freq="D")
        forecast = model.predict(future)
        forecast_yhats= forecast[["yhat","yhat_lower","yhat_upper"]].tail(1).values[0]
        return forecast_yhats


#Calling the def fubction
forecast_next_day("AAPL")