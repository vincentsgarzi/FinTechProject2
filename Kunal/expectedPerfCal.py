## This script uses the last 30 days of returns to calculate a naive estimate for 'tomorrow's' returns

#import for testing and training timeframes
import datetime as dt
from pandas.tseries.offsets import DateOffset

import pandas as pd

def RecentPerfSummary(forCompany,inputdata):
    today= pd.to_datetime(dt.date.today())
    start= today - DateOffset(days=30)
    summary_start_date=start.date()
    summary_df=inputdata.loc[(inputdata['symbol'] == forCompany) & (inputdata.index>=summary_start_date)].copy()
    summary_df['actual_returns']=summary_df['close'].pct_change()
    summary_df=summary_df.dropna()
    return summary_df.iloc[-1]['close'],summary_df['actual_returns'].mean(), summary_df['actual_returns'].std()
