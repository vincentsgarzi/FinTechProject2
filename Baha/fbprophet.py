from dotenv import load_dotenv
import pandas as pd
import alpaca_trade_api as tradeapi
import os
from pandas.tseries.offsets import DateOffset
import datetime as dt
from cmdstanpy import install_cmdstan
install_cmdstan()
from prophet import Prophet
model = Prophet(stan_backend='CMDSTANPY')

# Initializing Facebook Prophet library
def forecast_next_day(tickers, inputdata):
    # Create an empty DataFrame to store the results
    results_df = pd.DataFrame()
    
    # Loop over each ticker symbol in the list of tickers
    for ticker in tickers:
        # Create a DataFrame with the closing prices for the current ticker
        stock_df = pd.DataFrame(inputdata.loc[inputdata["symbol"] == ticker]["close"])
        
        # Reset the index and rename the columns to work with Prophet
        stock_df = stock_df.reset_index().rename(columns={"index": "ds", "close": "y"})
        
        # Create a Prophet model and fit it to the data
        model = Prophet()
        model.fit(stock_df)
        
        # Create a DataFrame with the next day's date
        future = model.make_future_dataframe(periods=1, freq="D")
        
        # Use the model to predict the next day's closing price
        forecast = model.predict(future)
        
        # Extract the forecasted price and the upper/lower bounds of the forecast for the next day
        forecast_yhats = forecast[["yhat", "yhat_lower", "yhat_upper"]].tail(1).values[0]
        
        # Add the results for the current ticker to the results DataFrame
        new_row = pd.DataFrame([{
            'ticker': ticker,
            'yhat': forecast_yhats[0],
            'yhat_lower': forecast_yhats[1],
            'yhat_upper': forecast_yhats[2]
        }])
        
        results_df = pd.concat([results_df, new_row], ignore_index=True)
    
    # Return the results DataFrame
    return results_df


# Function to compare forecasted prices to actual prices
def compare_prices(results_df, df):
    # Create an empty DataFrame to store the comparison results
    comp_df = pd.DataFrame(columns=["Tickers", "Actual Price", "Best Price", "Worst Price"])
    
    # Loop over each row in the input DataFrame
    for i in range(len(df)):
        # Extract the symbol and expected price for the current row
        symbol = df.loc[i, 'Symbol']
        expected_price = df.loc[i, 'expectedprice']
        best_price = df.loc[i, 'expectedprice-high']
        worst_price = df.loc[i, 'expectedprice-low']
        
        # Loop over each row in the results DataFrame
        for j in range(len(results_df)):
            # If the ticker symbol in the results DataFrame matches the current symbol
            if results_df.loc[j, 'ticker'] == symbol:
                # Extract the forecasted price and the upper/lower bounds of the forecast
                predicted_price = results_df.loc[j, 'yhat']
                yhat_best = results_df.loc[j, 'yhat_upper']
                yhat_worst = results_df.loc[j, 'yhat_lower']
                
                # Compare the forecasted price to the actual price
                if predicted_price > expected_price:
                    # If forecasted price > actual price, add a new row with best/worst prices
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
                
                # Use pd.concat to append the new row to comp_df
                comp_df = pd.concat([comp_df, new_row], ignore_index=True)
    
    return comp_df