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
import sys
import os

load_dotenv()

os.chdir("../Kunal")
sys.path.append(os.getcwd())
from app import PriceSummary

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
tickers = ["AAPL", "TSLA", "MSFT","NVDA"] #this will be gathered from sidebar eventually
tickers_dfs = []

df_portfolio_year = alpaca.get_bars(
    tickers,
    timeframe,
    start = start_date
).df

df_portfolio_year.index=pd.to_datetime(df_portfolio_year.index).date

results_df = pd.DataFrame()

# Initializing facebook prophet library
def forecast_next_day(ticker,inputdata):
    results_df = pd.DataFrame()
    for ticker in tickers:
        stock_df = pd.DataFrame(inputdata.loc[inputdata["symbol"] == ticker]["close"])
        stock_df = stock_df.reset_index().rename(columns={"index": "ds", "close": "y"})
        model = Prophet()
        model.fit(stock_df)
        future = model.make_future_dataframe(periods=1, freq="D")
        forecast = model.predict(future)
        forecast_yhats= forecast[["yhat","yhat_lower","yhat_upper"]].tail(1).values[0]
        results_df = results_df.append({'ticker': ticker, 'yhat': forecast_yhats[0], 
                                        'yhat_lower': forecast_yhats[1], 'yhat_upper': forecast_yhats[2]}, 
                                        ignore_index=True)
    return results_df

results_df = forecast_next_day(tickers,df_portfolio_year)

df = PriceSummary(tickers,df_portfolio_year)

print(results_df)
print(df)

def compare_prices(results_df, df):
    comp_df = pd.DataFrame(columns=["Tickers","Actual Price","Best Price","Worst Price"])

    for i in range(len(df)):
        symbol = df.loc[i, 'Symbol']
        expected_price = df.loc[i, 'expectedprice']
        best_price = df.loc[i, 'expectedprice-high']
        worst_price = df.loc[i, 'expectedprice-low']
        #worst_price = df.loc[i, 'expectedprice']

        for j in range(len(results_df)):
            if results_df.loc[j, 'ticker'] == symbol:
                predicted_price = results_df.loc[j, 'yhat']
                yhat_best = results_df.loc[j, 'yhat_upper']
                yhat_worst = results_df.loc[j, 'yhat_lower']

                if predicted_price > expected_price:
                    comp_df = comp_df.append({"Tickers": symbol,
                                              "Actual Price": expected_price,
                                              "Best Price": best_price,
                                              "Worst Price": worst_price}, ignore_index=True)
                else:
                    comp_df = comp_df.append({"Tickers": symbol,
                                              "Actual Price": predicted_price,
                                              "Best Price": yhat_best,
                                              "Worst Price": yhat_worst}, ignore_index=True)
    return(comp_df)

compare_prices(results_df,df)

    