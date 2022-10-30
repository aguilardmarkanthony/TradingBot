import sys, os
sys.path.extend([f'{item[0]}' for item in os.walk(".") if os.path.isdir(item[0])])
import TradingPlatform.Binance.DataSource.BinanceAPI as binance
import TradingPlatform.Binance.DataSource.BinanceSecretKey as apk
import plotly.graph_objects as go
import datetime  as dt
import pandas    as pd
import pandas_ta as ta
import requests
import time

header = {'authorization': 'NDAzMjE3MTIyMTM1NjM4MDE2.Gwwd9N.yLL2EbVN1frbQOG8JFqgicV-v1qpG7Sf-T85ZU',
          'Accept': 'text/plain'}

exchange_info = binance.exchange_info()
def new_func(df):
    my_bbands = ta.bbands(df.Close, length=14, std=2.0)
    return my_bbands

while True:
  for s in exchange_info['symbols']:
    symbol = str(s['symbol'])
    base = s['symbol'][-4:]

    if base != 'USDT':
      continue

    if symbol == "USDCUSDT":
        continue 
    if symbol == "BUSDUSDT":
        continue 
    if symbol == "USDCUSDT":
        continue 
    if symbol == "USDPUSDT":
        continue 

    klines_5min = binance.historical_klines(symbol=symbol)
    data = pd.DataFrame(klines_5min, columns = ['open_time','Open', 'High', 'Low', 'Close', 
                                                'Volume','close_time', 'qav','num_trades',
                                                'taker_base_vol','taker_quote_vol', 'ignore'])
    if data.empty:
      continue   
                                             
    data.dropna(subset=['Open', 'Close', 'Low', 'High', 'Volume'])
    df = data[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
    df = df.astype(float)
    df['open_time'] = pd.to_datetime(data.open_time, unit='ms')
    df.set_index("open_time", inplace=True)
    df=df[df.High!=df.Low]
    tlen = len(df)

    df["VWAP"]=ta.vwap(df.High, df.Low, df.Close, df.Volume)
    df['RSI']=ta.rsi(df.Close, length=16)

    if df.empty:
      continue       

    my_bbands = new_func(df)

    if my_bbands is not None:
      df=df.join(my_bbands)
    else:
      continue


    df['ATR']=ta.atr(high=df.High, low=df.Low, close=df.Close, length=14)

    try:
      slatr = 1.2*df.ATR[-1]
    except TypeError:
      continue 

    try:
      TPSLRatio = 2
      tpatr = slatr*2
    except TypeError:
      continue

    if (df.Close[-1] > df['VWAP'][-1] 
        and df['BBL_14_2.0'][-1]  > df.Close[-1]
        and df['BBL_14_2.0'][-1] > df['VWAP'][-1] 
        and df.RSI[-1] < 45):
            #buy long position
            TP = str(df.Open[-1] + tpatr)
            SL = str(df.Open[-1] - slatr)
            open = str(df.Open[-1])
            content = str('Long position - Symbol: '+symbol+' EP: '+open+' TP: '+TP+' SL: '+SL)
            data = { "content": content }
            r = requests.post("https://discord.com/api/v9/channels/1032975832186093608/messages", headers=header, data=data)
            time.sleep(1)   
            
    if (df['VWAP'][-1] > df.Close[-1] 
        and df.Close[-1] > df['BBU_14_2.0'][-1] 
        and df['VWAP'][-1]  > df['BBU_14_2.0'][-1] 
        and df.RSI[-1] > 55):
            #sell short position
            TP = str(df.Open[-1] - tpatr)
            SL = str(df.Open[-1] + slatr)
            open = str(df.Open[-1])
            content = str('Short position - Symbol: '+symbol+' EP: '+open+' TP: '+TP+' SL: '+SL)
            data = { "content": content }
            r = requests.post("https://discord.com/api/v9/channels/1032975832186093608/messages", headers=header, data=data)
            time.sleep(1)  




#exchange_info = binance.exchange_info()
#historical_klines = binance.historical_klines(symbol='BTCUSDT')
#orderbook_tickers = binance.orderbook_tickers()




