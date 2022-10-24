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

header = {'authorization': 'MTAxMDQ2NjA3MDYwOTU0MzIxMQ.GzuuTh.cvAwmQYiCxd_y2tD8wKekNj7xfV7p_3uRL-n2g',
          'Accept': 'text/plain'}

exchange_info = binance.exchange_info()
while True:
  for s in exchange_info['symbols']:
    symbol = str(s['symbol'])
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
    my_bbands = ta.bbands(df.Close, length=14, std=2.0)
    df=df.join(my_bbands)
    VWAPsignal = [0]*len(df)
    backcandles = 15

    for row in range(backcandles, len(df)):
        upt = 1
        dnt = 1
        for i in range(row-backcandles, row+1):
            if max(df.Open[i], df.Close[i])>=df.VWAP[i]:
                dnt=0
            if min(df.Open[i], df.Close[i])<=df.VWAP[i]:
                upt=0
        if upt==1 and dnt==1:
            VWAPsignal[row]=3
        elif upt==1:
            VWAPsignal[row]=2
        elif dnt==1:
            VWAPsignal[row]=1

    df['ATR']=ta.atr(high=df.High, low=df.Low, close=df.Close, length=14)


    slatr = 1.2*df.ATR[-1]
    TPSLRatio = 2
    tpatr = slatr*2

    fig = go.Figure(data=[go.Candlestick(x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close']),
                go.Scatter(x=df.index, y=df.VWAP, 
                           line=dict(color='blue', width=1), 
                           name="VWAP"), 
                go.Scatter(x=df.index, y=df['BBL_14_2.0'], 
                           line=dict(color='green', width=1), 
                           name="BBL"),
                go.Scatter(x=df.index, y=df['BBU_14_2.0'], 
                           line=dict(color='green', width=1), 
                           name="BBU")])

    if (df.Close[-1]<=df['BBL_14_2.0'][-1]
        and df.RSI[-1]<45):
            #buy long position
            TP = str(df.Open[-1] + tpatr)
            SL = str(df.Open[-1] - slatr)
            open = str(df.Open[-1])
            content = str('Long position - Symbol:'+symbol+' EP: '+open+' TP: '+TP+' SL: '+SL)
            data = { "content": content }
            r = requests.post("https://discord.com/api/v9/channels/1032975832186093608/messages", headers=header, data=data)
            time.sleep(1)   
            
    if (df.Close[-1]>=df['BBU_14_2.0'][-1]
        and df.RSI[-1]>55):
            #sell short position
            TP = str(df.Open[-1] - tpatr)
            SL = str(df.Open[-1] + slatr)
            open = str(df.Open[-1])
            content = str('Long position - Symbol:'+symbol+' EP: '+open+' TP: '+TP+' SL: '+SL)
            data = { "content": content }
            r = requests.post("https://discord.com/api/v9/channels/1032975832186093608/messages", headers=header, data=data)
            time.sleep(1)  




#exchange_info = binance.exchange_info()
#historical_klines = binance.historical_klines(symbol='BTCUSDT')
#orderbook_tickers = binance.orderbook_tickers()




