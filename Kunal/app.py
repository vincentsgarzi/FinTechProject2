#import for testing and training timeframes
import datetime as dt
from pandas.tseries.offsets import DateOffset

# Import the finta Python library and the TA module
import pandas as pd

from model_calls import *
from technicalind import techinds
from test_train import *
from model_select import model_selection
from expectedPerfCal import RecentPerfSummary

def model_iteration(tickers, inputdata):
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

def PriceSummary(tickers,inputdata):
    perforamance_summary_sorted=model_iteration(tickers,inputdata)
    
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