from TradingPlatform.Binance.DataSource import BinanceAPI as binance
from TradingPlatform.Binance.DataSource import BinanceSecretKey as apk

exchaxnge_info = binance.exchange_info()
print(exchaxnge_info)


