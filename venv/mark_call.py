import sys, os
sys.path.extend([f'{item[0]}' for item in os.walk(".") if os.path.isdir(item[0])])
import TradingPlatform.Binance.DataSource.BinanceAPI as binance
import TradingPlatform.Binance.DataSource.BinanceSecretKey as apk
import datetime as dt

exchange_info = binance.exchange_info()
#historical_klines = binance.historical_klines(symbol='BTCUSDT')

print(exchange_info)


