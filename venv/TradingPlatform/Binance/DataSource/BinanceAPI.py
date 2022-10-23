from TradingPlatform.Binance.DataSource import BinanceSecretKey as apk
from TradingPlatform.Binance.DataSource import BinanceAPI as binance
from TradingPlatform.Binance.DataSource import BinanceClient as client

def exchange_info():
  exchange_info = client.get_exchange_info()
  return exchange_info

def historical_klines(symbol, interval, start_str=None, end_str=None):
  historical_klines = client.get_historical_klines(symbol=symbol, interval=interval, start_str=start_str, end_str=end_str)
  return historical_klines