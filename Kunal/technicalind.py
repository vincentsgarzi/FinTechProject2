## The script fuction that selects data for the last 24 months and
## creates technical indicators for modeling on the base dataframe
## it returns a dataframe with key modeling features

import pandas as pd
import datetime as dt
from pandas.tseries.offsets import DateOffset
from finta import TA
import numpy as np

def techinds(data,ticker,short_window,long_window):
    #Subset dataframe for last 24 month history
    today= pd.to_datetime(dt.date.today())
    start= today - DateOffset(months=24)
    training_start_date=start.date()
    indicators_df=data.loc[(data.index>=training_start_date) 
                                        & (data['symbol']==ticker)].copy()
    
    # Create additional technical indicators
    indicators_df["ssma"] = TA.SSMA(indicators_df)
    indicators_df["ema"] = TA.EMA(indicators_df, 50)
    indicators_df["dema"] = TA.DEMA(indicators_df)
    indicators_df["tema"] = TA.TEMA(indicators_df)
    indicators_df["trima"] = TA.TRIMA(indicators_df)
    indicators_df["trima"] = TA.TRIMA(indicators_df)
    indicators_df['sma_fast'] = TA.SMA(indicators_df, short_window)
    indicators_df['sma_slow'] = TA.SMA(indicators_df, long_window)
    # Create signals based on returns and return dataframe with key modeling features
    signals_df=indicators_df.loc[:,['symbol',"close",'ssma','ema','dema','tema','trima'
                                    ,'sma_slow','sma_fast']]
    signals_df['actual_returns']=signals_df['close'].pct_change()
    signals_df=signals_df.dropna()
    signals_df['Signal']=np.where(signals_df['actual_returns']>=0 ,1 ,-1)
    return signals_df