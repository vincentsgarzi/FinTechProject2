import streamlit as st
import pandas as pd
from pathlib import Path

# sets the page configuration for Streamlit utilization
st.set_page_config(page_title="Investment Application", page_icon=":earth_americas:")

# creates a sidebar that is used to compose the portfolio
with st.sidebar:
    st.title('Portfolio Builder')
    # load NYSE tickers
    nyse_tickers = pd.read_csv(Path('./Resources/tickers.csv'))
    nyse_tickers['Symbol_Name'] = nyse_tickers['Symbol'] + ' - ' + nyse_tickers['Name']
    nyse_tickers = nyse_tickers['Symbol_Name'].tolist()

    # create a dropdown menu for selecting tickers
    st.subheader('Ticker Selection:')
    selected_tickers = st.multiselect(':blue[Select the stock tickers you wish to incorporate into your portfolio.]', nyse_tickers)

    # create a dictionary for storing ticker weights
    weights = {}

    # loop through selected tickers and prompt the user to input weights
    st.subheader('Ticker Weights:')
    st.caption(':blue[Please allot the weights to your chosen stock tickers.]')
    st.caption('_Note: The combined total must be equal to 1.0._')
    for ticker in selected_tickers:
        ticker_symbol, company_name = ticker.split(' - ')
        weight = st.slider(f'{ticker_symbol} Weight:', key=ticker_symbol, min_value=.0, max_value=1.0, value=0.0, step=.01)
        weights[ticker_symbol] = weight

    # create a list of the tickers to use in the Alpaca API call
    ticker_keys = list(weights.keys())

    # calculate the total weight
    total_weight = sum(weights.values())

    # if the total weight is not equal to 100, show an error message
    if total_weight != 1.0:
        st.error(f'Total combined weight of the stocks in your portfolio is currently {total_weight:.2f} must be equal to 1.0.')
        st.write(total_weight)
    
# creates four tabs that will display on the webpage
tab1, tab2, tab3, tab4 = st.tabs(['About','Portfolio Dashboard','Future Projected Returns', 'Robo Advisor'])


with tab1:
    st.title('About')
    import streamlit as st

    # Description
    st.write("Our investment portfolio finanical application enables you to build and manage your investment portfolio, and is designed to help you make informed investment decisions and achieve your financial goals.")

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
    st.write("With that said, we are committed to helping you achieve your financial goals. Whether you're looking to build a long-term investment portfolio or trade stocks for short-term gains, our platform provides you with the tools and resources you need to succeed.")


with tab2:
    st.title('Portfolio Dashboard')
    st.subheader('The following is an overview of your selcted portfolio and their weights.')

with tab3:
    st.title('Future Projected Returns')

with tab4:
    st.title('Robo Advisor')


