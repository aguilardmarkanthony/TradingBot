from TradingPlatform.Binance.DataSource import BinanceAPI as binance
from TradingPlatform.Binance.DataSource import BinanceSecretKey as apk
import datetime as dt

#exchange_info = binance.exchange_info()
start = str(int(dt.datetime(2021,5,1).timestamp()*1000))
end = str(int(dt.datetime(2021,8,1).timestamp()*1000))
historical_klines = binance.historical_klines(symbol='BTCUSDT', interval='1hr',start_str=start, end_str=end)

print(historical_klines)


