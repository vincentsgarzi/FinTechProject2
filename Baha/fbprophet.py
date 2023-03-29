from dotenv import load_dotenv
import pandas as pd
import alpaca_trade_api as tradeapi
from prophet import Prophet
import os
from pandas.tseries.offsets import DateOffset
import datetime as dt
import sys
import os

# Initializing facebook prophet library
# This function uses Facebook Prophet to forecast the next day's closing price for each stock in the list of tickers.
# It returns a DataFrame with the ticker symbol, forecasted price, and upper and lower bounds of the forecast.

def forecast_next_day(tickers,inputdata):
    # create an empty DataFrame to store the results
    results_df = pd.DataFrame()
    # loop over each ticker symbol in the list of tickers
    for ticker in tickers:
        # create a DataFrame with the closing prices for the current ticker
        stock_df = pd.DataFrame(inputdata.loc[inputdata["symbol"] == ticker]["close"])
        # reset the index and rename the columns to work with Prophet
        stock_df = stock_df.reset_index().rename(columns={"index": "ds", "close": "y"})
        # create a Prophet model and fit it to the data
        model = Prophet()
        model.fit(stock_df)
        # create a DataFrame with the next day's date
        future = model.make_future_dataframe(periods=1, freq="D")
        # use the model to predict the next day's closing price
        forecast = model.predict(future)
        # extract the forecasted price and the upper and lower bounds of the forecast for the next day
        forecast_yhats= forecast[["yhat","yhat_lower","yhat_upper"]].tail(1).values[0]
        # add the results for the current ticker to the results DataFrame
        results_df = results_df.append({'ticker': ticker, 'yhat': forecast_yhats[0],
                                        'yhat_lower': forecast_yhats[1], 'yhat_upper': forecast_yhats[2]},
                                        ignore_index=True)
    # return the results DataFrame
    return results_df


# This function compares the forecasted prices to the actual prices and returns a DataFrame with the ticker symbol,
# the actual price, the best-case price (the upper bound of the forecast), and the worst-case price (the lower bound
# of the forecast).

def compare_prices(results_df, df):
    # create an empty DataFrame to store the comparison results
    comp_df = pd.DataFrame(columns=["Tickers","Actual Price","Best Price","Worst Price"])
    # loop over each row in the input DataFrame
    for i in range(len(df)):
        # extract the symbol and expected price for the current row
        symbol = df.loc[i, 'Symbol']
        expected_price = df.loc[i, 'expectedprice']
        best_price = df.loc[i, 'expectedprice-high']
        worst_price = df.loc[i, 'expectedprice-low']
        # loop over each row in the results DataFrame
        for j in range(len(results_df)):
            # if the ticker symbol in the results DataFrame matches the current symbol
            if results_df.loc[j, 'ticker'] == symbol:
                # extract the forecasted price and the upper and lower bounds of the forecast for the current ticker
                predicted_price = results_df.loc[j, 'yhat']
                yhat_best = results_df.loc[j, 'yhat_upper']
                yhat_worst = results_df.loc[j, 'yhat_lower']
                # compare the forecasted price to the actual price
                if predicted_price > expected_price:
                    # if the forecasted price is higher than the actual price, add a row to the comparison DataFrame
                    # with the actual price, the best-case price, and the worst-case price
                    comp_df = comp_df.append({"Tickers": symbol,
                                              "Actual Price": expected_price,
                                              "Best Price": best_price,
                                              "Worst Price": worst_price}, ignore_index=True)

                    comp_df = comp_df.set_index('Tickers')
    return(comp_df)

