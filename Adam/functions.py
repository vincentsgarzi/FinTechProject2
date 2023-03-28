import pandas as pd
from pathlib import Path
import pandas as pd
import plotly.express as px
from datetime import date, timedelta
import alpaca_trade_api as tradeapi
import streamlit as st
import streamlit_scrollable_textbox as stx


# function that returns the list of tickers and their names for use in the 'ticker selection' drop down
def get_cleaned_tickers(csv_path):

    # reading in the csv file
    nyse_tickers = pd.read_csv(Path(csv_path)) 
    nyse_tickers['Symbol'] = nyse_tickers['Symbol'].astype(str)

    # removing the tickers that contain a '^' sign, for data cleansing and alpaca api compatability
    nyse_tickers = nyse_tickers[~nyse_tickers['Symbol'].str.contains('\^')]

    # creating a new column consisting of the ticker-name
    nyse_tickers['Symbol_Name'] = nyse_tickers['Symbol'] + ' - ' + nyse_tickers['Name']

    # appends the 'symbol_name' column to a list
    nyse_tickers = nyse_tickers['Symbol_Name'].tolist()
    return nyse_tickers


# function that returns three pi charts based off the portfolio tickers, sector, and industry
def portfolio_breakdown(csv_path, weights):

    # reading in the tickers.csv file
    tickers_csv = pd.read_csv(Path(csv_path))
    tickers_csv['Symbol'] = tickers_csv['Symbol'].astype(str)

    # removing the tickers that contain a '^' sign, for data cleansing and alpaca api compatability
    tickers_csv = tickers_csv[~tickers_csv['Symbol'].str.contains('\^')]

    # creating a new dataframe and merging them on the 'Symbol' column
    portfolio_df = pd.DataFrame(weights.items(), columns=['Symbol', 'Weight'])
    merged_df = pd.merge(portfolio_df, tickers_csv, on='Symbol')

    # create a pie chart of sector weights using Plotly
    fig1 = px.pie(merged_df, values='Weight', names='Sector', title='by Sector')
    fig2 = px.pie(merged_df, values='Weight', names='Industry', title='by Industry')
    fig3 = px.pie(merged_df, values='Weight', names='Symbol', title='by Stock')
    return fig1, fig2, fig3


# function that returns the line plot for the the historical close prices
def plot_close_prices(ticker_keys, concat_market_data, selected_period):

    # calculate the start date based on the selected time period
    today = date.today()
    start_date = today - timedelta(days=selected_period)

    # filter the dataframe to the selected time period
    df_period = concat_market_data.loc[start_date:]

    # concatanating the dataframe to only show the 'close' columns
    close_df = pd.concat([df_period.loc[:, (ticker, 'close')] for ticker in ticker_keys], axis=1)
    close_df = close_df.droplevel(axis=1, level=1)

    # creating the plot to show the closing prices over a specific period of time
    close_plot = px.line(close_df, labels={'variable':'Ticker', 'value':'Closing Price (USD)', 'timestamp':'Date'})

    return close_plot


def get_closing_prices(tickers, api_key, secret_key):
    # set up Alpaca API credentials
    api = tradeapi.REST(api_key, secret_key)

    # get the most recent closing prices for the specified tickers
    barsets = api.get_bars(tickers, '1D').df
    barsets = barsets.set_index('symbol').rename_axis('Ticker')

    # adjusting the datafram to only show the most recent close and the ticker
    barsets = barsets.drop(columns=['open', 'high', 'low','volume', 'trade_count', 'vwap'])
    barsets = barsets.rename(columns={'close':'Closing Price (USD)'})
    return barsets


def get_news_headlines(tickers, api_key, secret_key):

    # Set up Alpaca API credentials
    api = tradeapi.REST(api_key, secret_key)

    # Retrieve one news article for each ticker
    news_items = []
    for ticker in tickers:
        news = api.get_news(ticker, limit=1)
        if news:
            item = news[0]
            news_items.append({
                'Ticker': st.write(ticker),
                'Headline': st.caption(item.headline),
                'Link': st.markdown(item.url, unsafe_allow_html=True)
            })

        












