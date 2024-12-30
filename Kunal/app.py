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
    # Creating an empty dataframe to save the performance summary
    performance_summary = pd.DataFrame([])

    for index, ticker in enumerate(tickers):
        # Function call to subset the historical data and create technical indicators
        tickerdf = techinds(inputdata, ticker, 50, 100)

        # Function call for creating dataframe with target variable
        target = targetdf(tickerdf)

        # Function call for creating dataframe with feature variables
        features = featuresdf(tickerdf)

        # Creating a df with features to forecast 'tomorrow'
        forecastdf = pd.DataFrame(tickerdf.iloc[-1, :]).transpose()

        # Splitting the features and target datasets into training and testing subsets
        X_train, y_train, X_test, y_test = train_test(features, target)

        # Scaling training, testing, and forecast features
        X_train_scaled, X_test_scaled, X_frcst_scaled = scaling(
            X_train.drop('symbol', axis=1),
            X_test.drop('symbol', axis=1),
            forecastdf.drop(['symbol', 'Signal'], axis=1)
        )

        # Executing SVC model
        svc_classification_report, method, forecast = supportvector(
            X_train_scaled, X_test_scaled, X_frcst_scaled, y_train, y_test
        )
        result_list = [ticker, index, method,
                       svc_classification_report['accuracy'],
                       svc_classification_report['1']['precision'],
                       svc_classification_report['1']['recall'],
                       svc_classification_report['-1']['precision'],
                       svc_classification_report['-1']['recall'],
                       forecast[0]]

        # Use pd.concat instead of append
        performance_summary = pd.concat([performance_summary, pd.DataFrame([result_list])], ignore_index=True)

        # Executing Logistic Regression model
        logit_classification_report, method, forecast = logistic(
            X_train_scaled, X_test_scaled, X_frcst_scaled, y_train, y_test
        )
        result_list = [ticker, index, method,
                       logit_classification_report['accuracy'],
                       logit_classification_report['1']['precision'],
                       logit_classification_report['1']['recall'],
                       logit_classification_report['-1']['precision'],
                       logit_classification_report['-1']['recall'],
                       forecast[0]]

        performance_summary = pd.concat([performance_summary, pd.DataFrame([result_list])], ignore_index=True)

        # Executing Decision Tree model
        DecTree_classification_report, method, forecast = tree(
            X_train_scaled, X_test_scaled, X_frcst_scaled, y_train, y_test
        )
        result_list = [ticker, index, method,
                       DecTree_classification_report['accuracy'],
                       DecTree_classification_report['1']['precision'],
                       DecTree_classification_report['1']['recall'],
                       DecTree_classification_report['-1']['precision'],
                       DecTree_classification_report['-1']['recall'],
                       forecast[0]]

        performance_summary = pd.concat([performance_summary, pd.DataFrame([result_list])], ignore_index=True)

    # Updating reporting columns
    reportingcols = {0: 'Company',
                     1: 'Position',
                     2: 'ModelType',
                     3: 'Accuracy',
                     4: 'PrecisionForReturnIncrease',
                     5: 'RecallForReturnIncrease',
                     6: 'PrecisionForReturnDecrease',
                     7: 'RecallForReturnDecrease',
                     8: 'Forecast'}
    performance_summary = performance_summary.rename(columns=reportingcols)

    # Sorting the performance summary for final model selection
    final_data_sorted = performance_summary.sort_values(by=['Position',
                                                            'Accuracy',
                                                            'PrecisionForReturnIncrease',
                                                            'PrecisionForReturnDecrease',
                                                            'RecallForReturnIncrease',
                                                            'RecallForReturnDecrease'],
                                                        ascending=[True, False, False, False, False, False])

    return final_data_sorted


def PriceSummary(tickers, inputdata):
    performance_summary_sorted = model_iteration(tickers, inputdata)

    final_summary = pd.DataFrame()

    for ticker in tickers:
        method = model_selection(ticker, performance_summary_sorted)
        price, mean, stdev = RecentPerfSummary(ticker, inputdata)
        result_list = [ticker, method, price, abs(mean), stdev]

        # Use pd.concat instead of append
        final_summary = pd.concat([final_summary, pd.DataFrame([result_list])], ignore_index=True)

    columns = {0: 'Symbol',
               1: 'PredictedSignal',
               2: 'LatestPrice',
               3: 'AvgReturns',
               4: 'StdDev'}

    final_summary = final_summary.rename(columns=columns)

    final_summary['expectedprice'] = final_summary['LatestPrice'] * (
            1 + final_summary['PredictedSignal'] * final_summary['AvgReturns'])
    final_summary['expectedprice-high'] = final_summary['LatestPrice'] * (
            1 + final_summary['PredictedSignal'] * (final_summary['AvgReturns'] + 2 * final_summary['StdDev']))
    final_summary['expectedprice-low'] = final_summary['LatestPrice'] * (
            1 + final_summary['PredictedSignal'] * (final_summary['AvgReturns'] - 2 * final_summary['StdDev']))

    return final_summary