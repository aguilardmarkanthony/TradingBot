import sys, os
sys.path.extend([f'{item[0]}' for item in os.walk(".") if os.path.isdir(item[0])])
import BinanceSecretKey as apk
import pandas as pd
import BinanceAPI as binance
from binance.client import Client

def exchange_info():
  try:
    client = Client(apk.api_key, apk.api_secret)
    exchange_info = client.get_exchange_info()
    return exchange_info
  except:
    print("Cannot get exchange info")
  

def historical_klines(symbol, interval):
  try:
    client = Client(apk.api_key, apk.api_secret)
    historical_klines = client.get_historical_klines(symbol, Client.KLINE_INTERVAL_5MINUTE, interval) #need to change, temporarily hard coded params
    return historical_klines
  except:
    print("Cannot get historical klines")

def orderbook_tickers():
  try:
    client = Client(apk.api_key, apk.api_secret)
    orderbook_tickers = client.get_orderbook_tickers()
    return orderbook_tickers
  except:
    print("Cannot get orderbook tickers")

def all_tickers():
  try:
      client = Client(apk.api_key, apk.api_secret)
      all_tickers = client.get_all_tickers()
      return all_tickers
  except:
      print("Cannot get all tickers")

