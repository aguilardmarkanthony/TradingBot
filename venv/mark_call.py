import sys, os
sys.path.extend([f'{item[0]}' for item in os.walk(".") if os.path.isdir(item[0])])
import TradingPlatform.Binance.DataSource.BinanceAPI as binance
import TradingPlatform.Binance.DataSource.BinanceSecretKey as apk
import TradingTool.APIAttr as attr
import TradingTool.APIFunc as func
import TradingSetup.VWAP_Bollinger_Bands_RSI as TS1
import plotly.graph_objects as go
import datetime  as dt
import pandas    as pd
import pandas_ta as ta
import requests
import time


exchange_info = binance.exchange_info()

while True:
  for s in exchange_info['symbols']:
    symbol = func.get_symbol(s)
    base = func.get_base(s)
    if func.check_base(base): continue
    if func.exclude_fiat(symbol): continue

    df = func.get_base_df(symbol=symbol,interval=attr.three_hr)

    if not isinstance(df, type(None)):
      try:
        TS1.VWAP_BB_RSI(df=df,symbol=symbol)
      except:
        continue
    else:
      continue



















