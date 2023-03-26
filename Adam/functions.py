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