import sys, os
sys.path.extend([f'{item[0]}' for item in os.walk(".") if os.path.isdir(item[0])])
import pandas as pd
import BinanceAPI as binance
import BinanceClient as Client

def exchange_info():
  exchange_info = Client.get_exchange_info()
  return exchange_info

def historical_klines(symbol):
  historical_klines = Client.get_historical_klines(symbol, '5MIN', '1 days ago UTC')
  return historical_klines