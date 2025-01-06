#########################
# Datadog Instrumentation
#########################
from ddtrace import patch_all, tracer
from ddtrace.contrib.logging import patch as log_patch

# Apply patches to supported libraries
patch_all()
# Patch logging to include Datadog trace details
log_patch()

import logging
import os

# Configure logging for Datadog correlation
log_file = os.path.join(os.getcwd(), "news_service.log")
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
logger = logging.getLogger(__name__)
logger.level = logging.INFO

# Optionally set log levels for ddtrace/datadog
logging.getLogger("ddtrace").setLevel(logging.INFO)
logging.getLogger("datadog").setLevel(logging.INFO)

# Create a logger for this module
logger = logging.getLogger(__name__)

# Optionally set default service name for these traces
tracer.set_tags({"service.name": "news_service"})

#########################
# Original Imports
#########################
import alpaca_trade_api as tradeapi
import datetime as dt
from pandas import DateOffset
from dotenv import load_dotenv

# Load .env environment variables
load_dotenv('api.env')

# Set Alpaca API key and secret
alpaca_api_key = os.getenv("ALPACA_API_KEY")
alpaca_secret_key = os.getenv("ALPACA_SECRET_KEY")

alpaca = tradeapi.REST(
    alpaca_api_key,
    alpaca_secret_key,
    api_version="v2"
)

today = dt.date.today()
news_end_date = dt.date.today() - DateOffset(days=1)
news_start_date = today - DateOffset(days=14)

#########################
# Instrumented Functions
#########################
def getNews(ticker):
    with tracer.trace("getNews", service="news_service"):
        logger.info("Retrieving news for ticker: %s", ticker)
        return alpaca.get_news(
            ticker,
            start=news_start_date.date(),
            end=news_end_date.date()
        )

def getNewsHeadline(ticker):
    with tracer.trace("getNewsHeadline", service="news_service"):
        logger.info("Fetching latest news headline for ticker: %s", ticker)
        news = getNews(ticker)
        return news[0].headline

def getThumbnail(ticker):
    with tracer.trace("getThumbnail", service="news_service"):
        logger.info("Fetching thumbnail for ticker: %s", ticker)
        news = getNews(ticker)
        if len(news[0].images) != 0:
            return news[0].images[2]["url"]
        return "Resources/defaultImage.png"

def getNewsLink(ticker):
    with tracer.trace("getNewsLink", service="news_service"):
        logger.info("Fetching news link for ticker: %s", ticker)
        news = getNews(ticker)
        return news[0].url

# Example prints / test calls
print(getNewsHeadline("AAPL"))
print(getThumbnail("AAPL"))
print(getNewsLink("AAPL"))