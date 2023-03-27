## This script includes functions that split the modeling dataframe into features & targets
## `Scaling` function standardizes the feature values
## each function returns a dataframe necessary for further processing in the main application   

import datetime as dt
from pandas.tseries.offsets import DateOffset
#import for scaling data
from sklearn.preprocessing import StandardScaler 

def targetdf(inputdata):
    return inputdata['Signal']

def featuresdf(inputdata):
    return inputdata[['symbol','close','actual_returns','ssma','ema','dema','tema','trima','sma_slow','sma_fast']].shift().dropna()

def train_test(featuredf,targetdf):
    # Select the start of the training period
    training_begin = featuredf.index.min()
    # Select the end of the training period
    training_end = featuredf.index.min() + DateOffset(months=6)
    # Generate the X_train and y_train DataFrames
    X_train=featuredf.loc[training_begin:training_end]
    y_train=targetdf.loc[training_begin:training_end]
    # Generate the X_test and y_test DataFrames
    X_test=featuredf.loc[training_end+DateOffset(days=1):]
    y_test=targetdf.loc[training_end+DateOffset(days=1):]
    return X_train, y_train, X_test, y_test
    
def scaling(feature_train, feature_test, forecast_df):
    # Create a StandardScaler instance
    scaler = StandardScaler()
    # Apply the scaler model to fit the X-train data
    X_scaler = scaler.fit(feature_train)
    # Transform the X_train and X_test DataFrames using the X_scaler
    X_train_scaled = X_scaler.transform(feature_train)
    X_test_scaled = X_scaler.transform(feature_test)
    X_frcst_scaled = X_scaler.transform(forecast_df)
    return X_train_scaled, X_test_scaled, X_frcst_scaled