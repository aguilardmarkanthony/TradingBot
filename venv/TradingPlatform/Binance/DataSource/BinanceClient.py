from TradingPlatform.Binance.DataSource import BinanceSecretKey as apk
from binance.client import Client

client = Client(apk.api_key, apk.api_secret)