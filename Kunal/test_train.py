## This script includes functions that split the modeling dataframe into features & targets
## `Scaling` function standardizes the feature values
## each function returns a dataframe necessary for further processing in the main application   

import datetime as dt
import pandas as pd
from pandas.tseries.offsets import DateOffset
#import for scaling data
from sklearn.preprocessing import StandardScaler 

def targetdf(inputdata):
    return inputdata['Signal']

def featuresdf(inputdata):
    return inputdata[['symbol','close','actual_returns','ssma','ema','dema','tema','trima','sma_slow','sma_fast']].shift().dropna()

def train_test(featuredf, targetdf):
    # Ensure the index is a DatetimeIndex
    featuredf.index = pd.to_datetime(featuredf.index)
    targetdf.index = pd.to_datetime(targetdf.index)

    # Select the start of the training period
    training_begin = featuredf.index.min()
    # Select the end of the training period
    training_end = featuredf.index.min() + DateOffset(months=6)

    # Generate the X_train and y_train DataFrames
    training_begin = pd.Timestamp(training_begin)
    training_end = pd.Timestamp(training_end)
    X_train = featuredf.loc[training_begin:training_end]
    y_train = targetdf.loc[training_begin:training_end]

    # Generate the X_test and y_test DataFrames
    X_test = featuredf.loc[training_end + DateOffset(days=1):]
    y_test = targetdf.loc[training_end + DateOffset(days=1):]

    return X_train, y_train, X_test, y_test
    
def scaling(feature_train, feature_test, forecast_df):
    from sklearn.preprocessing import StandardScaler
    
    # Ensure forecast_df has the same columns and order as feature_train
    forecast_df = forecast_df[feature_train.columns]
    
    # Create a StandardScaler instance
    scaler = StandardScaler()
    
    # Fit the scaler on the feature_train data
    X_scaler = scaler.fit(feature_train)
    
    # Transform the feature_train, feature_test, and forecast_df DataFrames
    X_train_scaled = X_scaler.transform(feature_train)
    X_test_scaled = X_scaler.transform(feature_test)
    X_frcst_scaled = X_scaler.transform(forecast_df)
    
    return X_train_scaled, X_test_scaled, X_frcst_scaled