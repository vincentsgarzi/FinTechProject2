import pandas as pd
from pathlib import Path
import pandas as pd
import plotly.express as px
from datetime import date, timedelta
import alpaca_trade_api as tradeapi
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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
    fig1 = px.pie(merged_df, values='Weight', names='Sector', title='by Sector', height=350, width=500)
    fig2 = px.pie(merged_df, values='Weight', names='Industry', title='by Industry', height=350, width=500 )
    fig3 = px.pie(merged_df, values='Weight', names='Symbol', title='by Stock', height=350, width=500)
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



def robo_graphs(signals_dfs, tickers):
    charts = {}

    index = 0

    for ticker in signals_dfs:
        # buy timing
        buy_points = ticker[ticker["Entry/Exit"] == 1.0]["close"]
        entry = go.Scatter(x=buy_points.index, y=buy_points, name="Buy", mode="markers",
                           marker=dict(color="green", symbol="triangle-up", size=10))

        # sell timing
        sell_points = ticker[ticker["Entry/Exit"] == -1.0]["close"]
        exit = go.Scatter(x=sell_points.index, y=sell_points, name="Sell", mode="markers",
                           marker=dict(color="red", symbol="triangle-down", size=10))

        # stock price
        security_close = go.Scatter(x=ticker.index, y=ticker["close"], name="Close", mode="lines",
                                     line=dict(color="lightgray"))

        # moving averages
        moving_avgs = go.Scatter(x=ticker.index, y=ticker["Short_SMA"], name="Short SMA", mode="lines",
                                  line=dict(color="blue"))
        moving_avgs2 = go.Scatter(x=ticker.index, y=ticker["Long_SMA"], name="Long SMA", mode="lines",
                                   line=dict(color="orange"))

        # create subplot with 2 rows and 1 column
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05)

        # add traces to subplot
        fig.add_trace(security_close, row=1, col=1)
        fig.add_trace(moving_avgs, row=1, col=1)
        fig.add_trace(moving_avgs2, row=1, col=1)
        fig.add_trace(entry, row=1, col=1)
        fig.add_trace(exit, row=1, col=1)

        # set subplot layout and axis titles
        fig.update_layout(title=tickers[index], height=800, width=1000, showlegend=False)
        fig.update_yaxes(title_text="Price (usd)", row=1, col=1)
        fig.update_xaxes(title_text='Date')

        index = index + 1

        # add the chart to the dictionary
        charts[tickers[index-1]] = fig

    # return the dictionary of charts
    return charts


















