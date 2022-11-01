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
from binance.client import Client
from binance.helpers import round_step_size

futures_exchange_info = binance.futures_exchange_info()

while True:
  for s in futures_exchange_info['symbols']:
    symbol = func.get_symbol(s['symbol'])
    contract_type = func.get_contract_type(s['symbol'])
    if func.check_contract_type(contract_type): continue
    base = func.get_base(symbol)
    if func.check_base(base): continue
    symbol = func.modify_symbol(symbol)
    df = func.get_base_df(symbol=symbol,start=attr.three_hr) 

    if not isinstance(df, type(None)):
      try:
        TS1.VWAP_BB_RSI(df=df,symbol=symbol)
      except:
        continue
    else:
      continue



















