from ddtrace import patch_all, tracer
import logging
from ddtrace.contrib.logging import patch as log_patch
patch_all()
log_patch()

import os
log_file = os.path.join(os.getcwd(), 'robo_logs.log')

logging.basicConfig(
    level=logging.INFO,  # Set the log level
    format="%(asctime)s [%(levelname)s] [dd.service=%(dd.service)s] [dd.trace_id=%(dd.trace_id)s] [dd.span_id=%(dd.span_id)s] [source=python] - %(message)s",
    handlers=[
        logging.FileHandler(log_file),  # Write logs to the specified file
        logging.StreamHandler()  # Output logs to the console as well
    ]
)

# Set DEBUG level for Datadog logs
logging.getLogger("ddtrace").setLevel(logging.INFO)
logging.getLogger("datadog").setLevel(logging.INFO)

# Create logger instance for your script
logger = logging.getLogger(__name__)

# Example log messages
logger.debug("Debug log message for troubleshooting.")
logger.info("Application started successfully.")

tracer.set_tags({"service.name": "robo_advisor"})

with tracer.trace("example.trace", service="robo_advisor"):
    logger.info("This is a log message correlated with a Datadog trace.")

import streamlit as st
import pandas as pd
from pathlib import Path
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
from portfolio import portfolio_returns


logger.info("setting the page configuration for Streamlit utilization")
st.set_page_config(page_title="Investment Application", page_icon=":earth_americas:", layout='wide')

logger.info("calling the load_dotenv() function to retrieve information from the .env file")
load_dotenv()

logger.info("gathering the api keys for the Alpaca API")
alpaca_api_key = os.getenv("ALPACA_API_KEY")
alpaca_secret_key = os.getenv("ALPACA_SECRET_KEY")

logger.info("setting the path to the tickers.csv")
csv_path = './Resources/tickers.csv'

time_dictionary = {'5 Years': 2555, '1 Year': 265, '6 Months': 180, '3 Months': 90, '7 Days': 7}

logger.info("creating a list to create tabs")
time_periods = list(time_dictionary.keys())
num_days = list(time_dictionary.values())

logger.info("creates a sidebar that is used to compose the portfolio")
with st.sidebar:
    st.title('Portfolio Builder')

    logger.info("load NYSE tickers")
    nyse_tickers = get_cleaned_tickers(csv_path)

    logger.info("create a dropdown menu for selecting tickers")
    st.subheader('Ticker Selection:')
    selected_tickers = st.multiselect(':blue[Select the stock tickers you wish to incorporate into your portfolio.]', nyse_tickers)

    if selected_tickers == []:
        st.error('No tickers have been selected.')

    logger.info("create a dictionary for storing ticker weights")
    weights = {}

    st.subheader('Ticker Weights:')
    st.caption(':blue[Allot the weights to your chosen stock tickers.]')
    st.caption('_Note: The combined total must be equal to 1.0._')

    logger.info("loop through selected tickers and prompt the user to input weights")
    for ticker in selected_tickers:
        ticker_symbol, company_name = ticker.split(' - ')
        weight = st.slider(f'{ticker_symbol} Weight:', key=ticker_symbol, min_value=.0, max_value=1.0, value=0.0, step=.05)
        weights[ticker_symbol] = weight

    logger.info("create a list of the tickers to use in the Alpaca API call")
    ticker_keys = list(weights.keys())

    logger.info("create a list of the ticker weights to use in portfolio_returns function")
    ticker_weights = list(weights.values())

    logger.info("calculate the total weight")
    total_weight = sum(weights.values())

    logger.info("if the total weight is not equal to 100, show an error message")
    if total_weight != 1.0:
        st.error(f'Total combined weight of the stocks in your portfolio is currently {total_weight:.2f} must be equal to 1.0.')

    st.subheader('Investment Amount:')
    st.caption(':blue[Enter the amount you wish to invest in USD.]')

    logger.info("create an entry box to prompt the user for the investment amount")
    investment_amount = st.number_input("Investment Amount", min_value=0, step=500, value=1000)

logger.info("creates four tabs that will display on the webpage")
tab1, tab2, tab3, tab4 = st.tabs(['About', 'Portfolio Dashboard', 'What-If', 'Robo Advisor'])

with tab1:

    st.image('Images/finance_banner.png', use_container_width=True, )
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
        logger.info("calling the gatherData function to get the stock ticker data")
        market_data = gatherData(tickers = ticker_keys, alpaca_api_key= alpaca_api_key, alpaca_secret_key= alpaca_secret_key)

        tickers_dfs = []
        for ticker in ticker_keys:
            ticker = market_data[market_data['symbol']==ticker].drop('symbol', axis=1)
            tickers_dfs.append(ticker)

        logger.info("concatanating the dataframe to visualize close history")
        concat_market_data = concatDataframes(tickers_dfs, ticker_keys)

    except:
        st.error('Must build your portfolio to proceed.')
        logger.error("Must build your portfolio to proceed.")

    logger.info("error handling to ensure the user correctly input their data")
    if total_weight != 1:
        st.error('The sum of the weights in your portfolio must be equal to 1.0.')
        logger.error("The sum of the weights in your portfolio must be equal to 1.0.")
    else:
        logger.info("calling the portfolio_breakdown function to get the portfolio breakdown pi charts")
        sector_pie, industry_pie, stock_pie = portfolio_breakdown(csv_path=csv_path, weights=weights)

        st.subheader('Portfolio Composition')

        logger.info("putting the pi charts into respective columns")
        pi1, pi2, pi3 = st.columns(3, gap='medium')

        with pi1:
            st.plotly_chart(stock_pie, use_container_width=True, key="chart_1")
        with pi2:
            st.plotly_chart(sector_pie, use_container_width=True, key="chart_2")
        with pi3:
            st.plotly_chart(industry_pie, use_container_width=True, key="chart_3")

        col1, col2 = st.columns([2.5,1], gap='large')

        with col1:

            st.subheader('Historic Close Prices')

            logger.info("setting up the tabs to display appropriate charts")
            chart1, chart2, chart3, chart4, chart5 = st.tabs(time_periods)

            logger.info("displaying the appropriate chart for its time frame using the 'plot_close_prices' function")
            with chart1:
                close_plot = plot_close_prices(ticker_keys=ticker_keys, concat_market_data=concat_market_data, selected_period=num_days[0])
                st.plotly_chart(close_plot, use_container_width=True, key="chart_4")
            with chart2:
                close_plot = plot_close_prices(ticker_keys=ticker_keys, concat_market_data=concat_market_data, selected_period=num_days[1])
                st.plotly_chart(close_plot, use_container_width=True, key="chart_5")
            with chart3:
                close_plot = plot_close_prices(ticker_keys=ticker_keys, concat_market_data=concat_market_data, selected_period=num_days[2])
                st.plotly_chart(close_plot, use_container_width=True, key="chart_6")
            with chart4:
                close_plot = plot_close_prices(ticker_keys=ticker_keys, concat_market_data=concat_market_data, selected_period=num_days[3])
                st.plotly_chart(close_plot, use_container_width=True, key="chart_7")
            with chart5:
                close_plot = plot_close_prices(ticker_keys=ticker_keys, concat_market_data=concat_market_data, selected_period=num_days[4])
                st.plotly_chart(close_plot, use_container_width=True, key="chart_8")

        with col2:

            st.subheader('Current Close Prices')

            logger.info("calling the 'get_closing_prices' function to retrieve a dataframe of the closing prices for each ticker the user selected")
            current_close_df = get_closing_prices(tickers=ticker_keys,api_key=alpaca_api_key, secret_key=alpaca_secret_key)

            st.dataframe(current_close_df, use_container_width=True)

            st.title('')

            st.subheader('Market News')

            logger.info("calling the 'get_news_headlines' function to")
            news = get_news_headlines(tickers=ticker_keys, api_key=alpaca_api_key, secret_key=alpaca_secret_key)

with tab3:
    st.title('What-If')
    st.write('Discover the potential value of your investment portfolio with our advanced analysis tool. It takes the portfolio you built and visualizes how your investments **:blue[could have]** grown over various time periods. It provides valuable insights into the performance of your investments and helps you make informed decisions about your financial future.')

    if total_weight != 1.0:
        st.error('The sum of the weights in your portfolio must be equal to 1.0.')
        logger.error("The sum of the weights in your portfolio must be equal to 1.0.")


    else:
        selected_period = st.selectbox('Select the time period you want to visualize.', time_periods)

        logger.info("retrieving an integer from a string")
        periods = {"Year": 365, "Years": 365, "Months": 30, "Days": 1}
        time_number, time_word = selected_period.split(' ')
        number_days = int(time_number) * periods[time_word]

        logger.info("calling the portfolio_returns function to get probable returns and the plot")
        return_num, return_plot = portfolio_returns(concat_market_data, ticker_keys, ticker_weights, investment_amount, selected_period=number_days)
        co1, co2 = st.columns([2.5, .9], gap='large')

        with co1:

            logger.info("showing potential returns")
            st.subheader(f"If you would have invested :blue[**${investment_amount}**]  {selected_period.lower()} ago, your portfolio would have an estimated value of :blue[**${return_num:.2f}**] today.")

            logger.info("setting up the tabs to display appropriate charts")
            st.plotly_chart(return_plot, use_container_width=True, key="chart_9")

        with co2:
            st.title('')
            st.image('Images/whatif.png', use_container_width= True)
         

with tab4:
    st.title('Robo Advisor')

    if len(ticker_keys) != 0:

        priceSummary = PriceSummary(ticker_keys, market_data)
        nextDay = forecast_next_day(ticker_keys, market_data)
        comp_df = compare_prices(nextDay, priceSummary)

        tickers_dfs = []
        for ticker in ticker_keys:
            ticker = market_data[market_data['symbol']==ticker].drop('symbol', axis=1)
            tickers_dfs.append(ticker)

        logger.info("calling the 'createSignals' function to return a dataframe with the buy and sell datax")
        signals_df = createSignals(tickers_dfs, comp_df)

        logger.info("calling the robo_graphs function to visualize when the user should buy/sell")
        charts_dict = robo_graphs(signals_df, ticker_keys)

        side1, side2 = st.columns([2,.75], gap='large')

        with side1:
            st.write('Our robo-advisor tab uses machine learning and simple moving averages to provide you with real-time recommendations on when to buy or sell specific stocks in your portfolio. The red and green arrows indicate whether you should sell or buy a stock, respectively, based on our analysis of market trends and performance data.')
            st.write('You can visualize each stock in your portfolio by selecting it from the dropdown menu. Our data-driven recommendations take the guesswork out of investing and help you make informed decisions to optimize your portfolio for maximum returns.')


            ticker_symbol = st.selectbox("Select Ticker Symbol", ticker_keys)

            st.title('')

            st.plotly_chart(charts_dict[ticker_symbol], use_container_width=True, key="chart_10")

        with side2:

            st.image("Images/robot.png", width=200)

            st.title('')

            st.subheader('Recommended Action')

            logger.info("for loop to indicate whether the user should buy, sell, or hold for each stock in portfolio")
            index = 0
            for signal in signals_df:
                position = ''
                sig = signal.iloc[len(signal)-1]['Entry/Exit']
                if sig == 0.0:
                    position = "maintain position for"
                elif sig == 1.0:
                    position = "buy"
                else:
                    position = "sell"
                st.write(f"You should **:blue[{position}]** {ticker_keys[index]}.")
                index = index + 1

            st.title('')

            st.subheader('Expected Prices')
            st.write('Below are the expected future prices with a 95% confidence of the stocks in your portfolio.')

            st.dataframe(comp_df, use_container_width=True)
