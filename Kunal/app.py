#import for testing and training timeframes
import datetime as dt
from pandas.tseries.offsets import DateOffset

# Import the finta Python library and the TA module
import pandas as pd


# from Components.model_calls import supportvector
# from Components.model_calls import logistic
# from Components.model_calls import tree
# from Components.technicalind import techinds
# from Components.test_train import targetdf
# from Components.test_train import featuresdf
# from Components.test_train import train_test
# from Components.test_train import scaling
# from Components.model_select import model_selection
# from Components.expectedPerfCal import RecentPerfSummary

from model_calls import *
from technicalind import techinds
from test_train import *
from model_select import model_selection
from expectedPerfCal import RecentPerfSummary

def model_iteration(inputdata):
    #Creating an empty dataframe to save the performance summary 
    perforamance_summary=pd.DataFrame([])

    for index,ticker in enumerate(tickers):

        #Function call to subset the historical data with 24 months historty 
        #and creating dataframe with technical indicators
        tickerdf=techinds(inputdata,ticker,50,100)

        #Function call for creating dataframe with target variable
        target=targetdf(tickerdf)

        #Function call for creating dataframe with feature variables
        features=featuresdf(tickerdf)

        #Creating a df with feature to forecast 'tomorrow'
        forecastdf=pd.DataFrame(tickerdf.iloc[-1,:]).transpose()

        #Splitting the features and target datasets into training and testing subsets
        X_train, y_train, X_test, y_test=train_test(features,target)

        #scaling training testing & forecast features
        X_train_scaled, X_test_scaled, X_frcst_scaled = scaling(X_train.drop('symbol',axis=1) 
                                                                ,X_test.drop('symbol',axis=1)
                                                                , forecastdf.drop(['symbol','Signal']
                                                                                  ,axis=1))

        #Executing SVC model to obatin the classification report, and signal forecast for 'tomorrow'
        svc_classification_report, method, forecast = supportvector(X_train_scaled
                                                                    ,X_test_scaled
                                                                    ,X_frcst_scaled
                                                                    ,y_train
                                                                    ,y_test)
        result_list=list([ticker,index,method,svc_classification_report['accuracy']
                                             ,svc_classification_report['1']['precision']
                                             ,svc_classification_report['1']['recall']
                                             ,svc_classification_report['-1']['precision']
                                             ,svc_classification_report['-1']['recall']
                                             ,forecast[0]])
        perforamance_summary=perforamance_summary.append(pd.DataFrame([result_list]), ignore_index=True)
        #Executing logit model to obatin the classification report, and signal forecast for 'tomorrow'
        logit_classification_report, method ,forecast=logistic(X_train_scaled
                                                               ,X_test_scaled
                                                               ,X_frcst_scaled
                                                               ,y_train
                                                               ,y_test)
        result_list=list([ticker,index,method,logit_classification_report['accuracy']
                                             ,logit_classification_report['1']['precision']
                                             ,logit_classification_report['1']['recall']
                                             ,logit_classification_report['-1']['precision']
                                             ,logit_classification_report['-1']['recall']
                                             ,forecast[0]])
        perforamance_summary=perforamance_summary.append(pd.DataFrame([result_list]), ignore_index=True)
        #Executing Decision Tree model to obatin the classification report, and signal forecast for 'tomorrow'
        DecTree_classification_report, method ,forecast=tree(X_train_scaled
                                                             ,X_test_scaled
                                                             ,X_frcst_scaled
                                                             ,y_train
                                                             ,y_test)
        result_list=list([ticker,index,method,DecTree_classification_report['accuracy']
                                             ,DecTree_classification_report['1']['precision']
                                             ,DecTree_classification_report['1']['recall']
                                             ,DecTree_classification_report['-1']['precision']
                                             ,DecTree_classification_report['-1']['recall']
                                             ,forecast[0]])
        perforamance_summary=perforamance_summary.append(pd.DataFrame([result_list]), ignore_index=True)
    #Updating reporting columns in the performance summary 
    reportingcols={0:'Company',
                   1:'Position',
                   2:'ModelType',
                   3:'Accuracy',
                   4:'PrecisionForReturnIncrease',
                   5:'RecallForReturnIncrease',
                   6:'PrecisionForReturnDecrease',
                   7:'RecallForReturnDecrease',
                   8:'Forecast'}
    perforamance_summary=perforamance_summary.rename(columns=reportingcols)
    #Sorting the perforamnce summary for final model selection
    final_data_sorted=perforamance_summary.sort_values(by=['Position'
                                                           ,'Accuracy'
                                                           ,'PrecisionForReturnIncrease'
                                                           ,'PrecisionForReturnDecrease'
                                                           ,'RecallForReturnIncrease'
                                                           ,'RecallForReturnDecrease']
                                                ,ascending=  [True
                                                              ,False
                                                              ,False
                                                              ,False
                                                              ,False
                                                              ,False])

    return final_data_sorted

def PriceSummary(inputdata):
    perforamance_summary_sorted=model_iteration(inputdata)
    
    final_summary=pd.DataFrame()

    for ticker in tickers:
        method=model_selection(ticker,perforamance_summary_sorted)
        price, mean, stdev = RecentPerfSummary(ticker,inputdata)
        result_list=list([ticker
                          ,method
                          ,price
                          ,abs(mean)
                          ,stdev])

        final_summary=final_summary.append(pd.DataFrame([result_list]),ignore_index=True)

    columns={0:'Symbol',
             1:'PredictedSignal',
             2:'LatestPrice',
             3:'AvgReturns',
             4:'StdDev'}

    final_summary=final_summary.rename(columns=columns)

    final_summary['expectedprice']=final_summary['LatestPrice']*(1+final_summary['PredictedSignal']*final_summary['AvgReturns'])
    final_summary['expectedprice-high']=final_summary['LatestPrice']*(1+final_summary['PredictedSignal']*
                                                                      (final_summary['AvgReturns']+final_summary['StdDev']))
    final_summary['expectedprice-low']=final_summary['LatestPrice']*(1+final_summary['PredictedSignal']*
                                                                      (final_summary['AvgReturns']-final_summary['StdDev']))

    return final_summary


# Import the required libraries and dependencies
import os
import requests
import json
import pandas as pd
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi

# Load the environment variables from the .env file
#by calling the load_dotenv function
load_dotenv()

# Set the variables for the Alpaca API and secret keys
alpaca_api_key=os.getenv("ALPACA_API_KEY")
alpaca_secret_key=os.getenv("ALPACA_SECRET_KEY")

# Create the Alpaca tradeapi.REST object
alpaca=tradeapi.REST(alpaca_api_key,alpaca_secret_key,api_version="v2")

# Set start and end dates of 3 years back from your current date
# Alternatively, you can use an end date of 2020-08-07 and work 3 years back from that date 
import datetime as dt
from pandas.tseries.offsets import DateOffset

today= dt.date.today() #- DateOffset(days=1)
start= today - DateOffset(years=5)
start_date=start.date()
timeframe='1Day'

tickers = ["AAPL"] #this will be gathered from sidebar eventually

tickers_dfs = []

timeframe = "1Day"

df_portfolio_year = alpaca.get_bars(
    tickers,
    timeframe,
    start = start_date
).df

#Reformatting the index
df_portfolio_year.index=pd.to_datetime(df_portfolio_year.index).date

df=PriceSummary(df_portfolio_year)

print(df)