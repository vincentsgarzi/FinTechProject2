import streamlit as st
import pandas as pd
from pathlib import Path
import os
import pandas as pd
import numpy as np
import alpaca_trade_api as tradeapi
from dotenv import load_dotenv
from datetime import date
from pathlib import Path
from pandas import DateOffset
from datetime import date, timedelta
import plotly.express as px




from Vinny.dmac import gatherData
from Vinny.dmac import concatDataframes
from Adam.functions import get_cleaned_tickers


# sets the page configuration for Streamlit utilization
st.set_page_config(page_title="Investment Application", page_icon=":earth_americas:")

# calling the load_dotenv() function to retrieve information from the .env file
load_dotenv()

# gathering the api keys for the Alpaca API
alpaca_api_key = os.getenv("ALPACA_API_KEY")
alpaca_secret_key = os.getenv("ALPACA_SECRET_KEY")

# creates a sidebar that is used to compose the portfolio
with st.sidebar:
    st.title('Portfolio Builder')
    
    # load NYSE tickers
    nyse_tickers = get_cleaned_tickers('./Resources/tickers.csv')

    # create a dropdown menu for selecting tickers
    st.subheader('Ticker Selection:')
    selected_tickers = st.multiselect(':blue[Select the stock tickers you wish to incorporate into your portfolio.]', nyse_tickers)

    # create a dictionary for storing ticker weights
    weights = {}

    st.subheader('Ticker Weights:')
    st.caption(':blue[Please allot the weights to your chosen stock tickers.]')
    st.caption('_Note: The combined total must be equal to 1.0._')

    # loop through selected tickers and prompt the user to input weights
    for ticker in selected_tickers:
        ticker_symbol, company_name = ticker.split(' - ')
        weight = st.slider(f'{ticker_symbol} Weight:', key=ticker_symbol, min_value=.0, max_value=1.0, value=0.0, step=.05)
        weights[ticker_symbol] = weight

    # create a list of the tickers to use in the Alpaca API call
    ticker_keys = list(weights.keys())

    # calculate the total weight
    total_weight = sum(weights.values())

    # if the total weight is not equal to 100, show an error message
    if total_weight != 1.0:
        st.error(f'Total combined weight of the stocks in your portfolio is currently {total_weight:.2f} must be equal to 1.0.')
    
# creates four tabs that will display on the webpage
tab1, tab2, tab3 = st.tabs(['About', 'Portfolio Dashboard', 'Robo Advisor'])

with tab1:
    st.title('About')

    # Description
    st.write("Our investment portfolio finanical application enables you to build and manage your investment portfolio. It is designed to help you make informed investment decisions and achieve your financial goals.")

    # Portfolio Overview Section
    st.header("Portfolio Overview")
    st.write("Our Portfolio Dashboard tab provides you with real-time information about your investment portfolio. You can view the current status of your investments and get access to the latest news and analysis about the stocks in your portfolio. This feature helps you stay up-to-date on the latest market trends and make informed decisions about your investment strategy.")
    st.write("This tab also offers a detailed breakdown of your portfolio, which provides you with a comprehensive overview of your investment allocations. You can easily see how much you've invested in each stock, sector, and asset class, allowing you to make any necessary adjustments to your portfolio based on your financial goals and risk tolerance.")

    # Future Projected Returns Section
    st.header('Future Projected Returns')
    st.write("Our app utilizes Facebook's Prophet time series forecasting model to provide you with projected returns for your portfolio.")

    # Robo Advisor Section
    st.header("Robo Advisor")
    st.write("Our machine learning algorithms and robo advisor feature provide you with a powerful tool to automatically trade the stocks in your portfolio. Our algorithms use the latest data analysis techniques to identify investment opportunities and help you make profitable trades. This feature allows you to take advantage of the latest market trends without spending countless hours analyzing market data.")

    # User-Friendly Interface Section
    st.header("User-Friendly Interface")
    st.write("Our platform is designed to be easy to use, even if you have no previous investment experience.")
    st.write("With that said, we are committed to helping you achieve your financial goals. Whether you're looking to build a long-term investment portfolio or trade stocks for short-term gains, our platform provides you with the tools and resources you need to succeed. Enjoy!")


with tab2:
    st.title('Portfolio Dashboard')
    st.subheader('The following is an overview of your selcted portfolio and their weights.')
    
    try:
        # calling the gatherData function to get the stock ticker data
        market_data = gatherData(tickers = ticker_keys, alpaca_api_key= alpaca_api_key, alpaca_secret_key= alpaca_secret_key)
        # concatanating the dataframe to visualize close history
        concat_market_data = concatDataframes(market_data, ticker_keys)

        # creating a dataframe to create a selectbox
        time_periods = {
        "5 years": 5 * 365,
        "1 year": 365,
        "6 months": 180,
        "3 months": 90,
        "7 days": 7}

        selected_period = st.selectbox("Select a time period to visualize the historic close data of your portfolio.", list(time_periods.keys()))

        # calculate the start date based on the selected time period
        today = date.today()
        start_date = today - timedelta(days=time_periods[selected_period])

        # filter the dataframe to the selected time period
        df_period = concat_market_data.loc[start_date:]

        # concatanating the dataframe to only show the 'close' columns
        close_df = pd.concat([df_period.loc[:, (ticker, 'close')] for ticker in ticker_keys], axis=1)
        close_df = close_df.droplevel(axis=1, level=1)

        # creating the plot to show the closing prices over a specific period of time
        close_plot = px.line(close_df, labels={'variable':'Ticker', 'value':'Closing Price (USD)', 'timestamp':'Date'})
        st.plotly_chart(close_plot)


    except:
        st.warning('Oops, no stock tickers were selected! Please go back to the sidebar to build your portfolio.')

with tab3:
      st.title('Robo Advisor')
  