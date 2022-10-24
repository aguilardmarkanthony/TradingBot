import sys, os
sys.path.extend([f'{item[0]}' for item in os.walk(".") if os.path.isdir(item[0])])
import BinanceSecretKey as apk
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager

client = Client(apk.api_key, apk.api_secret)