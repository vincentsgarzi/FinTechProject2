#########################
# Datadog Instrumentation
#########################
from ddtrace import patch_all, tracer
from ddtrace.contrib.logging import patch as log_patch

# Patch all supported modules (requests, sqlite3, etc. if used)
patch_all()
# Patch logging to include Datadog trace details in logs
log_patch()

import logging
import os

# Configure logging to capture Datadog trace/spans
log_file = os.path.join(os.getcwd(), 'model_iteration.log')
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s [%(levelname)s] "
#            "[service=%(dd.service)s] "
#            "[trace_id=%(dd.trace_id)s] "
#            "[span_id=%(dd.span_id)s] "
#            "[source=python] - %(message)s",
#     handlers=[
#         logging.FileHandler(log_file),
#         logging.StreamHandler()
#     ]
# )

FORMAT = ('%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] '
          '[dd.service=%(dd.service)s dd.env=%(dd.env)s dd.version=%(dd.version)s dd.trace_id=%(dd.trace_id)s dd.span_id=%(dd.span_id)s] '
          '- %(message)s')
logging.basicConfig(format=FORMAT)
log = logging.getLogger(__name__)
log.level = logging.INFO

# Optionally set log levels
logging.getLogger("ddtrace").setLevel(logging.INFO)
logging.getLogger("datadog").setLevel(logging.INFO)

# Create a logger for this module
logger = logging.getLogger(__name__)

# You can tag all traces with a default service name if you like
tracer.set_tags({"service.name": "model_service"})

#########################
# Original Imports
#########################
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

#########################
# Instrumented Functions
#########################

def model_iteration(tickers, inputdata):
    """
    Iterates over multiple ML models (SVC, Logistic Regression, Decision Tree),
    evaluates performance, and returns a sorted DataFrame with model performance results.
    """
    with tracer.trace("model_iteration", service="model_service"):
        logger.info("Starting model iteration on provided tickers.")
        # Creating an empty dataframe to save the performance summary
        performance_summary = pd.DataFrame([])

        for index, ticker in enumerate(tickers):
            # Function call to subset the historical data and create technical indicators
            tickerdf = techinds(inputdata, ticker, 50, 100)
            # Create target variable
            target = targetdf(tickerdf)
            # Create features
            features = featuresdf(tickerdf)
            # Create forecast DataFrame with just the last row
            forecastdf = pd.DataFrame(tickerdf.iloc[-1, :]).transpose()

            # Split the features and target datasets into training and testing subsets
            X_train, y_train, X_test, y_test = train_test(features, target)

            # Scale training, testing, and forecast features
            X_train_scaled, X_test_scaled, X_frcst_scaled = scaling(
                X_train.drop('symbol', axis=1),
                X_test.drop('symbol', axis=1),
                forecastdf.drop(['symbol', 'Signal'], axis=1)
            )

            # SVC Model
            svc_classification_report, method, forecast = supportvector(
                X_train_scaled, X_test_scaled, X_frcst_scaled, y_train, y_test
            )
            svc_result_list = [
                ticker,
                index,
                method,
                svc_classification_report['accuracy'],
                svc_classification_report['1']['precision'],
                svc_classification_report['1']['recall'],
                svc_classification_report['-1']['precision'],
                svc_classification_report['-1']['recall'],
                forecast[0]
            ]
            performance_summary = pd.concat(
                [performance_summary, pd.DataFrame([svc_result_list])],
                ignore_index=True
            )

            # Logistic Regression Model
            logit_classification_report, method, forecast = logistic(
                X_train_scaled, X_test_scaled, X_frcst_scaled, y_train, y_test
            )
            logit_result_list = [
                ticker,
                index,
                method,
                logit_classification_report['accuracy'],
                logit_classification_report['1']['precision'],
                logit_classification_report['1']['recall'],
                logit_classification_report['-1']['precision'],
                logit_classification_report['-1']['recall'],
                forecast[0]
            ]
            performance_summary = pd.concat(
                [performance_summary, pd.DataFrame([logit_result_list])],
                ignore_index=True
            )

            # Decision Tree Model
            DecTree_classification_report, method, forecast = tree(
                X_train_scaled, X_test_scaled, X_frcst_scaled, y_train, y_test
            )
            dt_result_list = [
                ticker,
                index,
                method,
                DecTree_classification_report['accuracy'],
                DecTree_classification_report['1']['precision'],
                DecTree_classification_report['1']['recall'],
                DecTree_classification_report['-1']['precision'],
                DecTree_classification_report['-1']['recall'],
                forecast[0]
            ]
            performance_summary = pd.concat(
                [performance_summary, pd.DataFrame([dt_result_list])],
                ignore_index=True
            )

        # Updating reporting columns
        reportingcols = {
            0: 'Company',
            1: 'Position',
            2: 'ModelType',
            3: 'Accuracy',
            4: 'PrecisionForReturnIncrease',
            5: 'RecallForReturnIncrease',
            6: 'PrecisionForReturnDecrease',
            7: 'RecallForReturnDecrease',
            8: 'Forecast'
        }
        performance_summary = performance_summary.rename(columns=reportingcols)

        # Sorting the performance summary for final model selection
        final_data_sorted = performance_summary.sort_values(
            by=[
                'Position',
                'Accuracy',
                'PrecisionForReturnIncrease',
                'PrecisionForReturnDecrease',
                'RecallForReturnIncrease',
                'RecallForReturnDecrease'
            ],
            ascending=[True, False, False, False, False, False]
        )

        logger.info("Completed model iteration. Returning final_data_sorted.")
        return final_data_sorted


def PriceSummary(tickers, inputdata):
    """
    Based on `model_iteration`, determines final summary of expected prices,
    leveraging the top-performing model selection results.
    """
    with tracer.trace("PriceSummary", service="model_service"):
        logger.info("Starting PriceSummary to determine final forecasted prices.")

        performance_summary_sorted = model_iteration(tickers, inputdata)
        final_summary = pd.DataFrame()

        for ticker in tickers:
            method = model_selection(ticker, performance_summary_sorted)
            price, mean, stdev = RecentPerfSummary(ticker, inputdata)
            result_list = [ticker, method, price, abs(mean), stdev]

            final_summary = pd.concat(
                [final_summary, pd.DataFrame([result_list])],
                ignore_index=True
            )

        columns = {
            0: 'Symbol',
            1: 'PredictedSignal',
            2: 'LatestPrice',
            3: 'AvgReturns',
            4: 'StdDev'
        }
        final_summary = final_summary.rename(columns=columns)

        final_summary['expectedprice'] = (
            final_summary['LatestPrice'] *
            (1 + final_summary['PredictedSignal'] * final_summary['AvgReturns'])
        )
        final_summary['expectedprice-high'] = (
            final_summary['LatestPrice'] *
            (1 + final_summary['PredictedSignal'] * (final_summary['AvgReturns'] + 2 * final_summary['StdDev']))
        )
        final_summary['expectedprice-low'] = (
            final_summary['LatestPrice'] *
            (1 + final_summary['PredictedSignal'] * (final_summary['AvgReturns'] - 2 * final_summary['StdDev']))
        )

        logger.info("PriceSummary calculation complete. Returning final_summary.")
        return final_summary