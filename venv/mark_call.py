from TradingPlatform.Binance.DataSource import BinanceAPI as binance
from TradingPlatform.Binance.DataSource import BinanceSecretKey as apk
import datetime as dt

exchange_info = binance.exchange_info()
#historical_klines = binance.historical_klines(symbol='BTCUSDT')

print(exchange_info)


