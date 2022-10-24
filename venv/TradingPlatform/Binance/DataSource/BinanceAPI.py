import pandas as pd
from TradingPlatform.Binance.DataSource import BinanceSecretKey as apk
from TradingPlatform.Binance.DataSource import BinanceAPI as binance
from TradingPlatform.Binance.DataSource import BinanceClient as client

def exchange_info():
  exchange_info = client.get_exchange_info()
  return exchange_info

def historical_klines(symbol):
  historical_klines = client.get_historical_klines(symbol, '5MIN', '1 days ago UTC')
  return historical_klines