import pandas as pd
from pathlib import Path
import pandas as pd
import plotly.express as px
from datetime import date, timedelta

def get_cleaned_tickers(csv_path):
    nyse_tickers = pd.read_csv(Path(csv_path))
    nyse_tickers['Symbol'] = nyse_tickers['Symbol'].astype(str)
    nyse_tickers = nyse_tickers[~nyse_tickers['Symbol'].str.contains('\^')]
    nyse_tickers['Symbol_Name'] = nyse_tickers['Symbol'] + ' - ' + nyse_tickers['Name']
    nyse_tickers = nyse_tickers['Symbol_Name'].tolist()
    return nyse_tickers

def portfolio_breakdown(csv_path, weights):
    tickers_csv = pd.read_csv(Path(csv_path))
    tickers_csv['Symbol'] = tickers_csv['Symbol'].astype(str)
    tickers_csv = tickers_csv[~tickers_csv['Symbol'].str.contains('\^')]
    portfolio_df = pd.DataFrame(weights.items(), columns=['Symbol', 'Weight'])
    merged_df = pd.merge(portfolio_df, tickers_csv, on='Symbol')
    # create a pie chart of sector weights using Plotly
    fig1 = px.pie(merged_df, values='Weight', names='Sector', title='Portfolio Breakdown by Sector')
    # create a pie chart of industry weights using Plotly
    fig2 = px.pie(merged_df, values='Weight', names='Industry', title='Portfolio Breakdown by Industry')
    # create a pie chart of stock weights using Plotly
    fig3 = px.pie(merged_df, values='Weight', names='Symbol', title='Portfolio Breakdown by Stock')
    return fig1, fig2, fig3


def plot_close_prices(ticker_keys, concat_market_data, time_periods, selected_period):

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

    return close_plot





