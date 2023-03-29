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
import sys
import os

# Change directory to the directory that contains the subdirectories
os.chdir("../FinTechProject2")

# Add subdirectories to sys.path
sys.path.append("./Adam")
sys.path.append("./Vinny")
sys.path.append("./Kunal")
sys.path.append("./Baha")

# Import modules
from functions import get_cleaned_tickers
from functions import portfolio_breakdown
from functions import plot_close_prices
from functions import get_closing_prices
from functions import get_news_headlines
from functions import robo_graphs
from dmac import gatherData
from dmac import concatDataframes
from app import PriceSummary
from dmac import createSignals
from fbprophet import compare_prices
from fbprophet import forecast_next_day


# sets the page configuration for Streamlit utilization
st.set_page_config(page_title="Investment Application", page_icon=":earth_americas:", layout='wide')

# calling the load_dotenv() function to retrieve information from the .env file
load_dotenv()

# gathering the api keys for the Alpaca API
alpaca_api_key = os.getenv("ALPACA_API_KEY")
alpaca_secret_key = os.getenv("ALPACA_SECRET_KEY")

# setting the path to the tickers.csv
csv_path = './Resources/tickers.csv'

# creates a sidebar that is used to compose the portfolio
with st.sidebar:
    st.title('Portfolio Builder')

    # load NYSE tickers
    nyse_tickers = get_cleaned_tickers(csv_path)

    # create a dropdown menu for selecting tickers
    st.subheader('Ticker Selection:')
    selected_tickers = st.multiselect(':blue[Select the stock tickers you wish to incorporate into your portfolio.]', nyse_tickers)

    if selected_tickers == []:
        st.error('No tickers have been selected.')

    # create a dictionary for storing ticker weights
    weights = {}

    st.subheader('Ticker Weights:')
    st.caption(':blue[Allot the weights to your chosen stock tickers.]')
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

    st.subheader('Investment Amount:')
    st.caption(':blue[Enter the amount you wish to invest in USD.]')

    # create an entry box to prompt the user for the investment amount
    investment_amount = st.number_input("Investment Amount", min_value=0, step=500, value=1000)

# creates four tabs that will display on the webpage
tab1, tab2, tab3, tab4 = st.tabs(['About', 'Portfolio Dashboard', 'What-If', 'Robo Advisor'])

with tab1:
    st.title('About Us')

    # Description
    st.write("Our investment portfolio finanical application enables you to build and manage your investment portfolio. It is designed to help you make informed investment decisions and achieve your financial goals.")

    st.title('')

    # Portfolio Overview Section
    with st.expander("Portfolio Overview"):
        st.write("Our Portfolio Dashboard tab provides you with real-time information about your investment portfolio. You can view the current status of your investments and get access to the latest news and analysis about the stocks in your portfolio. This feature helps you stay up-to-date on the latest market trends and make informed decisions about your investment strategy.")
        st.write("This tab also offers a detailed breakdown of your portfolio, which provides you with a comprehensive overview of your investment allocations. You can easily see how much you've invested in each stock, sector, and asset class, allowing you to make any necessary adjustments to your portfolio based on your financial goals and risk tolerance.")

    # What If Section
    with st.expander("What-If"):
        st.write("The 'What If' tab is a web tool that helps you see how your portfolio would have performed if you had invested it over different time periods in the past.")
        st.write('It uses sophisticated algorithms and data analysis techniques to give you a clear picture of the potential value of your portfolio. By theorizing how your investments would have performed over time, you can gain valuable insights into their historical performance and make more informed decisions about future investment strategies.')

    # Robo Advisor Section
    with st.expander("Robo Advisor"):
        st.write("Our machine learning algorithms and robo advisor feature provide you with a powerful tool to automatically trade the stocks in your portfolio. Our algorithms use the latest data analysis techniques to identify investment opportunities and help you make profitable trades. This feature allows you to take advantage of the latest market trends without spending countless hours analyzing market data.")

    # User-Friendly Interface Section
    with st.expander("User-Friendly Interface"):
        st.write("Our platform is designed to be easy to use, even if you have no previous investment experience.")
        st.write("With that said, we are committed to helping you achieve your financial goals. Whether you're looking to build a long-term investment portfolio or trade stocks for short-term gains, our platform provides you with the tools and resources you need to succeed. Enjoy!")

with tab2:
    st.title('Portfolio Dashboard')
    st.write("Below, you'll find an overview of your selected investment portfolio, including weightings and historical close data. You'll also see pertinent news related to the portfolio you've constructed.")
    st.title('')

    try:
        # calling the gatherData function to get the stock ticker data
        market_data = gatherData(tickers = ticker_keys, alpaca_api_key= alpaca_api_key, alpaca_secret_key= alpaca_secret_key)

        tickers_dfs = []
        for ticker in ticker_keys:
            ticker = market_data[market_data['symbol']==ticker].drop('symbol', axis=1)
            tickers_dfs.append(ticker)

        # concatanating the dataframe to visualize close history
        concat_market_data = concatDataframes(tickers_dfs, ticker_keys)

    except:
        st.error('Must build your portfolio to proceed.')

    # error handling to ensure the user correctly input their data
    if total_weight != 1:
        st.error('The sum of the weights in your portfolio must be equal to 1.0.')
    else:
        # calling the portfolio_breakdown function to get the portfolio breakdown pi charts
        sector_pie, industry_pie, stock_pie = portfolio_breakdown(csv_path=csv_path, weights=weights)

        st.subheader('Portfolio Composition')

        # putting the pi charts into respective columns
        pi1, pi2, pi3 = st.columns(3, gap='medium')

        with pi1:
            st.plotly_chart(stock_pie, use_container_width=True)
        with pi2:
            st.plotly_chart(sector_pie, use_container_width=True)
        with pi3:
            st.plotly_chart(industry_pie, use_container_width=True)

        col1, col2 = st.columns([2.5,1], gap='large')

        with col1:

            st.subheader('Historic Close Prices')

            # creating a list to create tabs
            time_periods = ["5 Years", "1 Year", "6 Months", "3 Months", "7 Days"]
            num_days = [2555, 265, 180, 90, 7]

            # setting up the tabs to display appropriate charts
            chart1, chart2, chart3, chart4, chart5 = st.tabs(time_periods)

            # displaying the appropriate chart for its time frame using the 'plot_close_prices' function
            with chart1:
                close_plot = plot_close_prices(ticker_keys=ticker_keys, concat_market_data=concat_market_data, selected_period=num_days[0])
                st.plotly_chart(close_plot, use_container_width=True)
            with chart2:
                close_plot = plot_close_prices(ticker_keys=ticker_keys, concat_market_data=concat_market_data, selected_period=num_days[1])
                st.plotly_chart(close_plot, use_container_width=True)
            with chart3:
                close_plot = plot_close_prices(ticker_keys=ticker_keys, concat_market_data=concat_market_data, selected_period=num_days[2])
                st.plotly_chart(close_plot, use_container_width=True)
            with chart4:
                close_plot = plot_close_prices(ticker_keys=ticker_keys, concat_market_data=concat_market_data, selected_period=num_days[3])
                st.plotly_chart(close_plot, use_container_width=True)
            with chart5:
                close_plot = plot_close_prices(ticker_keys=ticker_keys, concat_market_data=concat_market_data, selected_period=num_days[4])
                st.plotly_chart(close_plot, use_container_width=True)

        with col2:

            st.subheader('Current Close Prices')
            current_close_df = get_closing_prices(tickers=ticker_keys,api_key=alpaca_api_key, secret_key=alpaca_secret_key)

            st.dataframe(current_close_df, use_container_width=True)

            st.title('')

            st.subheader('Market News')

            news = get_news_headlines(tickers=ticker_keys, api_key=alpaca_api_key, secret_key=alpaca_secret_key)

with tab3:
    st.title('What-If')
    st.write('Discover the potential value of your investment portfolio with our advanced analysis tool. It takes the portfolio you built and visualizes how your investments **:blue[could have]** grown over various time periods. It provides valuable insights into the performance of your investments and helps you make informed decisions about your financial future.')

with tab4:
    st.title('Robo Advisor')

    ticker_keys = ["AAPL"]

    if len(ticker_keys) != 0:
        market_data = gatherData(ticker_keys, alpaca_api_key, alpaca_secret_key)

        priceSummary = PriceSummary(ticker_keys, market_data)
        nextDay = forecast_next_day(ticker_keys, market_data)
        comp_df = compare_prices(nextDay, priceSummary)

        tickers_dfs = []
        for ticker in ticker_keys:
            ticker = market_data[market_data['symbol']==ticker].drop('symbol', axis=1)
            tickers_dfs.append(ticker)

        signals_df = createSignals(tickers_dfs, comp_df)

        print(signals_df)

        st.plotly_chart(robo_graphs(signals_df, ticker_keys))
