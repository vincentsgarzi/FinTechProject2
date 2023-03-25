import os
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
  api_version="v2")

today = dt.date.today()

news_end_date = dt.date.today() - DateOffset(days=1)
news_start_date = today - DateOffset(days=14)

def getNews(ticker):
  return alpaca.get_news(ticker,start=news_start_date.date(),end=news_end_date.date())

def getNewsHeadline(ticker):
  news = getNews(ticker)
  return news[0].headline

def getThumbnail(ticker):
  news = getNews(ticker)
  if len(news[0].images) != 0:
    return news[0].images[2]["url"]
  return "Resources/defaultImage.png"


def getNewsLink(ticker):
  news = getNews(ticker)
  return news[0].url

print(getNewsHeadline("AAPL"))
print(getThumbnail("AAPL"))
print(getNewsLink("AAPL"))
