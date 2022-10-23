from TradingPlatform.Binance.DataSource import BinanceSecretKey as apk
from TradingPlatform.Binance.DataSource import BinanceAPI as binance
from binance.client import Client

client = Client(apk.api_key, apk.api_secret)

def binance_exchange_info():
  exchange_info = client.get_exchange_info()
  return exchange_info