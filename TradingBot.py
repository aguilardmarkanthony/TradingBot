import plotly.graph_objects as go
import pandas as pd
import pandas_ta as ta
import numpy as np
from backtesting import Strategy
from backtesting import Backtest
from binance.client import Client

from plotly.subplots import make_subplots
from datetime import datetime
api_key = 'KWVUpuWlJyVeL58wn7dHmKDx2OjJ7uAqq6eo5dZRDirq0XkgFCGe8dX6w7ryZa0m'
api_secret = 'TqGtGj8QuNRPhJb53mPSo3QklF02gZ10XSsXJ5QzXfyggkocsZkeCOlRttcmebUQ'
client = Client(api_key, api_secret)

columns = [
    'open_time', 'open', 'high', 'low', 'close', 'volume',
    'close_time', 'quote_asset_volume', 'number_of_trades',
    'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume',
    'ignore'
]
klines = client.get_historical_klines('BNBUSDT', Client.KLINE_INTERVAL_5MINUTE, "1 day ago UTC")
data = pd.DataFrame(klines, columns = ['open_time','Open', 'High', 'Low', 'Close', 'Volume','close_time', 'qav','num_trades','taker_base_vol','taker_quote_vol', 'ignore'])

data.dropna(subset=['Open', 'Close', 'Low', 'High', 'Volume'])

df = data[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
df = df.astype(float)

df['open_time'] = pd.to_datetime(data.open_time, unit='ms')

df.set_index("open_time", inplace=True)
df=df[df.High!=df.Low]
tlen = len(df)


df["VWAP"]=ta.vwap(df.High, df.Low, df.Close, df.Volume)
df['RSI']=ta.rsi(df.Close, length=16)
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

df['VWAPSignal'] = VWAPsignal

def TotalSignal(l):
    if (df.VWAPSignal[l]==2
        and df.Close[l]<=df['BBL_14_2.0'][l]
        and df.RSI[l]<45):
            return 2
    if (df.VWAPSignal[l]==1
        and df.Close[l]>=df['BBU_14_2.0'][l]
        and df.RSI[l]>55):
            return 1
    return 0
        
TotSignal = [0]*len(df)
for row in range(backcandles, len(df)): #careful backcandles used previous cell
    TotSignal[row] = TotalSignal(row)
df['TotalSignal'] = TotSignal

df[df.TotalSignal!=0].count()


def pointposbreak(x):
    if x['TotalSignal']==1:
        return x['High']+1e-4
    elif x['TotalSignal']==2:
        return x['Low']-1e-4
    else:
        return np.nan

df['pointposbreak'] = df.apply(lambda row: pointposbreak(row), axis=1)


st=0
dfpl = df[st:tlen]
dfpl.reset_index(inplace=True)
fig = go.Figure(data=[go.Candlestick(x=dfpl.index,
                open=dfpl['Open'],
                high=dfpl['High'],
                low=dfpl['Low'],
                close=dfpl['Close']),
                go.Scatter(x=dfpl.index, y=dfpl.VWAP, 
                           line=dict(color='blue', width=1), 
                           name="VWAP"), 
                go.Scatter(x=dfpl.index, y=dfpl['BBL_14_2.0'], 
                           line=dict(color='green', width=1), 
                           name="BBL"),
                go.Scatter(x=dfpl.index, y=dfpl['BBU_14_2.0'], 
                           line=dict(color='green', width=1), 
                           name="BBU")])

fig.add_scatter(x=dfpl.index, y=dfpl['pointposbreak'], mode="markers",
                marker=dict(size=10, color="MediumPurple"),
                name="Signal")

dfpl = df.copy()

dfpl['ATR']=ta.atr(dfpl.High, dfpl.Low, dfpl.Close, length=7)
#help(ta.atr)
def SIGNAL():
    return dfpl.TotalSignal
#fig.show()

class MyStrat(Strategy):
    initsize = 0.99
    mysize = initsize
    def init(self):
        super().init()
        self.signal1 = self.I(SIGNAL)

    def next(self):
        super().next()
        slatr = 1.2*self.data.ATR[-1]
        TPSLRatio = 2

        if len(self.trades)>0:
            if self.trades[-1].is_long and self.data.RSI[-1]>=90:
                self.trades[-1].close()
            elif self.trades[-1].is_short and self.data.RSI[-1]<=10:
                self.trades[-1].close()
        
        if self.signal1==2 and len(self.trades)==0:
            sl1 = self.data.Close[-1] - slatr
            tp1 = self.data.Close[-1] + slatr*TPSLRatio
            self.buy(sl=sl1, tp=tp1, size=self.mysize)
        
        elif self.signal1==1 and len(self.trades)==0:         
            sl1 = self.data.Close[-1] + slatr
            tp1 = self.data.Close[-1] - slatr*TPSLRatio
            self.sell(sl=sl1, tp=tp1, size=self.mysize)

bt = Backtest(dfpl, MyStrat, cash=100000, margin=1/10, commission=0.00)
stat = bt.run()
stat



import requests
import json
import time
import discord
import numpy as np
import pandas as pd
from datetime import datetime
import datetime
import pandas_ta as ta
import matplotlib.pyplot as plt
import mplfinance as mpf
#import orca
from matplotlib import style
from binance.client import Client
import plotly.graph_objects as go
import plotly.io as pio




api_key = 'KWVUpuWlJyVeL58wn7dHmKDx2OjJ7uAqq6eo5dZRDirq0XkgFCGe8dX6w7ryZa0m'
api_secret = 'TqGtGj8QuNRPhJb53mPSo3QklF02gZ10XSsXJ5QzXfyggkocsZkeCOlRttcmebUQ'
client = Client(api_key, api_secret)

columns = [
    'open_time', 'open', 'high', 'low', 'close', 'volume',
    'close_time', 'quote_asset_volume', 'number_of_trades',
    'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume',
    'ignore'
]



'''
while True:
    time.sleep(1)    
    tickers = client.get_orderbook_tickers()
    ticker_df = pd.DataFrame(tickers, columns = ['symbol','bidPrice', 'bidQty', 'askPrice', 'askQty'])
    ticker_df = ticker_df.astype({'bidPrice':'float','bidQty':'float','askPrice':'float','askQty':'float'})
    ticker_df.dropna(subset=['bidPrice', 'bidQty', 'askPrice', 'askQty'])
    ticker_df['spreadperc'] = (ticker_df['askPrice']/ticker_df['bidPrice'] - 1) * 100.0

    #ticker_df = ticker_df.drop(ticker_df[ticker_df.symbol[-4:] != 'USDT'].index)

    for index, row in ticker_df.iterrows():
        if row['spreadperc'] > 2:
            if row['symbol'][-3:] == 'BTC':
                print('Symbol: ' + row['symbol'] + ' ' + 'Spread Percentage: ' + str(row['spreadperc']))

'''







while True:
    
    exchange_info = client.get_exchange_info()


    for s in exchange_info['symbols']:
        base = s['symbol'][-4:]
        #base = s['symbol']
        if base == 'USDT':
            symbol = str(s['symbol'])
            if symbol == "USDCUSDT":
                continue 
            if symbol == "BUSDUSDT":
                continue 
            if symbol == "USDCUSDT":
                continue 
            if symbol == "USDPUSDT":
                continue 
            klines_1hr = client.get_historical_klines(s['symbol'], Client.KLINE_INTERVAL_1HOUR, "1 day ago UTC")
            klines_1d = client.get_historical_klines(s['symbol'], Client.KLINE_INTERVAL_1DAY, "400 day ago UTC")
                              
            data = pd.DataFrame(klines_1hr, columns = ['open_time','open', 'high', 'low', 'close', 'volume','close_time', 'qav','num_trades','taker_base_vol','taker_quote_vol', 'ignore'])
            data2 = pd.DataFrame(klines_1d, columns = ['open_time','open', 'high', 'low', 'close', 'volume','close_time', 'qav','num_trades','taker_base_vol','taker_quote_vol', 'ignore'])
            
            klines_4hr = client.get_historical_klines(s['symbol'], Client.KLINE_INTERVAL_1HOUR, "30 day ago UTC")
            data3 = pd.DataFrame(klines_4hr, columns = ['open_time','open', 'high', 'low', 'close', 'volume','close_time', 'qav','num_trades','taker_base_vol','taker_quote_vol', 'ignore'])
            
            klines_1hr_2 = client.get_historical_klines(s['symbol'], Client.KLINE_INTERVAL_5MINUTE, "2 day ago UTC")
            data4 = pd.DataFrame(klines_1hr_2, columns = ['open_time','open', 'high', 'low', 'close', 'volume','close_time', 'qav','num_trades','taker_base_vol','taker_quote_vol', 'ignore'])
             

            if data.empty:
                continue
                
            if data2.empty:
                continue 

            if data3.empty:
                continue 

            if data4.empty:
                continue

            data = data.astype({'open':'float','low':'float','close':'float','high':'float', 'volume':'float'})
            data2 = data2.astype({'open':'float','low':'float','close':'float','high':'float', 'volume':'float'})
            data3 = data3.astype({'open':'float','low':'float','close':'float','high':'float', 'volume':'float'})
            data4 = data4.astype({'open':'float','low':'float','close':'float','high':'float', 'volume':'float'})

            data4.dropna(subset=['open', 'close', 'low', 'high', 'volume'])
            data3.dropna(subset=['open', 'close', 'low', 'high', 'volume'])
            data2.dropna(subset=['open', 'close', 'low', 'high', 'volume'])
            data.dropna(subset=['open', 'close', 'low', 'high', 'volume'])           
            # Reset index after drop

            '''
            data4.reset_index(drop=True, inplace=True)
            data3.reset_index(drop=True, inplace=True)
            data2.reset_index(drop=True, inplace=True)
            data.reset_index(drop=True, inplace=True)
            '''

            data3['EMA20'] = ta.ema(data3.close, length = 20)
            data3['EMA25'] = ta.ema(data3.close, length = 25)
            data3['EMA30'] = ta.ema(data3.close, length = 30)
            data3['EMA35'] = ta.ema(data3.close, length = 35)
            data3['EMA40'] = ta.ema(data3.close, length = 40)
            data3['EMA45'] = ta.ema(data3.close, length = 45)
            data3['EMA50'] = ta.ema(data3.close, length = 50)
            data3['EMA55'] = ta.ema(data3.close, length = 55)
            data3['RSI'] = ta.rsi(data3.close, length = 14)
            data3 = data3.tail(150)
            
            data4['EMA9'] = ta.ema(data4.close, length = 9)
            data4['EMA24'] = ta.ema(data4.close, length = 24)
            data4['EMA34'] = ta.ema(data4.close, length = 34)
            data4['RSI'] = ta.rsi(data4.close, length = 14)
            data4 = data4.tail(150)

            data2['SMA20'] = ta.sma(data2.close, length = 20)
            data2['SMA50'] = ta.sma(data2.close, length = 50)
            data2['SMA100'] = ta.sma(data2.close, length = 100)
            data2['SMA200'] = ta.sma(data2.close, length = 200)
            data2['RSI'] = ta.rsi(data2.close, length = 14)
            data2 = data2.tail(150)
            
            
            data2.open_time = pd.to_datetime(data2.open_time, unit='ms')
            data3.open_time = pd.to_datetime(data3.open_time, unit='ms')
            data4.open_time = pd.to_datetime(data4.open_time, unit='ms')
            
            data2 = data2.set_index("open_time")
            data3 = data3.set_index("open_time")
            data4 = data4.set_index("open_time")

            
            '''
            data4.reset_index(drop=True, inplace=True)
            data3.reset_index(drop=True, inplace=True)
            data2.reset_index(drop=True, inplace=True)
            data.reset_index(drop=True, inplace=True)
            '''
            open1 = data.iloc[-1].open
            close1 = data.iloc[-1].close
            SMA20 = data2.iloc[-1].SMA20
            SMA50 = data2.iloc[-1].SMA50
            SMA20_2 = data2.iloc[-2].SMA20
            SMA50_2 = data2.iloc[-2].SMA50
            SMA100_2 = data2.iloc[-2].SMA100
            SMA200_2 = data2.iloc[-2].SMA200
            SMA100 = data2.iloc[-1].SMA100
            SMA200 = data2.iloc[-1].SMA200
            RSI = data2.iloc[-1].RSI

            EMA20 = data3.iloc[-1].EMA20
            EMA25 = data3.iloc[-1].EMA25
            EMA30 = data3.iloc[-1].EMA30
            EMA35 = data3.iloc[-1].EMA35
            EMA40 = data3.iloc[-1].EMA40
            EMA45 = data3.iloc[-1].EMA45
            EMA50 = data3.iloc[-1].EMA50
            EMA55 = data3.iloc[-1].EMA55
            EMA20_2 = data3.iloc[-2].EMA20
            EMA25_2 = data3.iloc[-2].EMA25
            EMA30_2 = data3.iloc[-2].EMA30
            EMA35_2 = data3.iloc[-2].EMA35
            EMA40_2 = data3.iloc[-2].EMA40
            EMA45_2 = data3.iloc[-2].EMA45
            EMA50_2 = data3.iloc[-2].EMA50
            EMA55_2 = data3.iloc[-2].EMA55
            
            EMA20_4 = data3.iloc[-4].EMA20
            EMA25_4 = data3.iloc[-4].EMA25
            EMA30_4 = data3.iloc[-4].EMA30
            EMA35_4 = data3.iloc[-4].EMA35
            EMA40_4 = data3.iloc[-4].EMA40
            EMA45_4 = data3.iloc[-4].EMA45
            EMA50_4 = data3.iloc[-4].EMA50
            EMA55_4 = data3.iloc[-4].EMA55
            RSI_2 = data3.iloc[-1].RSI

            EMA9 = data4.iloc[-1].EMA9
            EMA24 = data4.iloc[-1].EMA24
            EMA34 = data4.iloc[-1].EMA34
            EMA9_2 = data4.iloc[-2].EMA9
            EMA24_2 = data4.iloc[-2].EMA24
            EMA34_2 = data4.iloc[-2].EMA34
            EMA9_3 = data4.iloc[-3].EMA9
            EMA24_3 = data4.iloc[-3].EMA24
            EMA34_3 = data4.iloc[-3].EMA34
            EMA9_4 = data4.iloc[-4].EMA9
            EMA24_4 = data4.iloc[-4].EMA24
            EMA34_4 = data4.iloc[-4].EMA34
            EMA9_5 = data4.iloc[-5].EMA9
            EMA24_5 = data4.iloc[-5].EMA24
            EMA34_5 = data4.iloc[-5].EMA34

            EMA24_4 = data4.iloc[-3].EMA24
            EMA24_5 = data4.iloc[-4].EMA24

            RSI_3 = data4.iloc[-1].RSI

            data4 = data4.tail(50)

            try:
                RSI = int(round(RSI))
            except:
                RSI = ''
            RSI_str = str(RSI)

            try:
                RSI_2 = int(round(RSI_2))
            except:
                RSI_2 = ''
            RSI_str_2 = str(RSI_2)

            try:
                RSI_3 = int(round(RSI_3))
            except:
                RSI_3 = ''
            RSI_str_3 = str(RSI_3)
            
            new_df = data2.tail(150)
            #new_df.reset_index(drop=True, inplace=True)

            zoom_df = data2.tail(50)
            #zoom_df.reset_index(drop=True, inplace=True)

            zoom_df_2 = data3.tail(100)
            #zoom_df_2.reset_index(drop=True, inplace=True)
            #zoom_df.reset_index(drop=True, inplace=True)
            

            try:
                if EMA9 > EMA34:
                    if EMA9_2 < EMA34_2:
                        #if EMA24_3 in range(EMA9_5, EMA34_5):   
                        if EMA9_4  <= EMA24_5 < EMA34_5:
                            min_price = data4.min()
                            max_price = data4.max()
                            header = {
                            'authorization': 'MTAxMDQ2NjA3MDYwOTU0MzIxMQ.GzuuTh.cvAwmQYiCxd_y2tD8wKekNj7xfV7p_3uRL-n2g',
                            'Accept': 'text/plain'
                            }
                            ap0 = [
                            mpf.make_addplot(data4['EMA9'], color='#3CCF4E', panel=0),
                            mpf.make_addplot(data4['EMA24'], color='#3120E0', panel=0),
                            mpf.make_addplot(data4['EMA34'], color='#FFEA11', panel=0),

                            mpf.make_addplot(data4['RSI'], color='#0000ff', panel=2, ylabel='RSI')
                            ]
                            mpf.plot(
                                data4,
                                addplot=ap0,
                                title = f"{symbol} Price",  
                                show_nontrading=False, 
                                figratio=(10,7), 
                                figscale=1.5, 
                                xrotation=90, 
                                tight_layout=False,  
                                type='candle',
                                update_width_config=dict(candle_linewidth=1.5),
                                ylim=(min_price.low, max_price.high),
                                volume=True,
                                num_panels=3,
                                savefig="C:/Users/maaguilar/Documents/Chart/fig.png" 
                                )

                            files = {'media': open("C:/Users/maaguilar/Documents/Chart/fig.png", 'rb')}

                            
                            ema3_content = str('3EMA Cross(5MIN TF)- Symbol: '+symbol+' RSI: '+RSI_str_3)
                            
                            data = {
                                "content": ema3_content
                            }
                            
                            r = requests.post("https://discord.com/api/v9/channels/1011660577447358576/messages", headers=header, data=data, files=files)
                            time.sleep(1)                     
            except:
                print('Error in 3ema (5MINS TF)' + symbol)

            try:
                if EMA20 > EMA55:
                    if EMA20_2 < EMA55_2:                        
                        if EMA20_4  <= EMA35_4 < EMA55_4:
                            if EMA20_4  <= EMA40_4 < EMA55_4:
                                if EMA20_4  <= EMA45_4 < EMA55_4:
                                    if EMA20_4  <= EMA50_4 < EMA55_4:
                                        min_price = data3.min()
                                        max_price = data3.max()
                                        header = {
                                        'authorization': 'MTAxMDQ2NjA3MDYwOTU0MzIxMQ.GzuuTh.cvAwmQYiCxd_y2tD8wKekNj7xfV7p_3uRL-n2g',
                                        'Accept': 'text/plain'
                                        }
                                        ap0 = [
                                        mpf.make_addplot(data3['EMA20'], color='#11cf11', panel=0),
                                        mpf.make_addplot(data3['EMA25'], color='#66bd00', panel=0),
                                        mpf.make_addplot(data3['EMA30'], color='#8ba900', panel=0),
                                        mpf.make_addplot(data3['EMA35'], color='#a59300', panel=0),
                                        mpf.make_addplot(data3['EMA40'], color='#b87b00', panel=0),
                                        mpf.make_addplot(data3['EMA45'], color='#c66000', panel=0),
                                        mpf.make_addplot(data3['EMA50'], color='#cf3f00', panel=0),
                                        mpf.make_addplot(data3['EMA55'], color='#d10505', panel=0),
                                        mpf.make_addplot(data3['RSI'], color='#0000ff', panel=2, ylabel='RSI')
                                        ]
                                        mpf.plot(
                                            data3,
                                            addplot=ap0,
                                            title = f"{symbol} Price",  
                                            show_nontrading=False, 
                                            figratio=(10,7), 
                                            figscale=1.5, 
                                            xrotation=90, 
                                            tight_layout=False,  
                                            type='candle',
                                            update_width_config=dict(candle_linewidth=1.5),
                                            ylim=(min_price.low, max_price.high),
                                            volume=True,
                                            num_panels=3,
                                            savefig="C:/Users/maaguilar/Documents/Chart/fig.png" 
                                            )

                                        files = {'media': open("C:/Users/maaguilar/Documents/Chart/fig.png", 'rb')}

                        
                                        ema_content = str('EMA Rainbow - Symbol:'+symbol+' RSI: '+RSI_str_2)
                        
                                        data = {
                                            "content": ema_content
                                        }
                        
                                        r = requests.post("https://discord.com/api/v9/channels/1011660577447358576/messages", headers=header, data=data, files=files)
                                        time.sleep(1)                     
            except:
                print("Error in ema")

            try:
                if SMA20 > open1:
                    if SMA20 < close1:  
                        min_price = new_df.tail(150).min()
                        max_price = new_df.tail(150).max()
                        ap0 = [
                        mpf.make_addplot(new_df['SMA20'], color='#277BC0', panel=0),
                        #mpf.make_addplot(zoom_df['SMA20'], color='#f00c0c', panel=0),
                        mpf.make_addplot(new_df['RSI'], color='#0000ff', panel=2, ylabel='RSI')                       
                        ]
                        
                        mpf.plot(
                            new_df,
                            addplot=ap0, 
                            title = f"{symbol} Price",  
                            show_nontrading=False, 
                            figratio=(10,7), 
                            figscale=1.5, 
                            xrotation=90, 
                            tight_layout=False,  
                            type='candle',
                            update_width_config=dict(candle_linewidth=1.5),
                            ylim=(min_price.low, max_price.high),
                            volume=True,
                            num_panels=3,
                            savefig="C:/Users/maaguilar/Documents/Chart/fig.png"                            
                            )

                        files = {'media': open("C:/Users/maaguilar/Documents/Chart/fig.png", 'rb')}

                        header = {
                        'authorization': 'MTAxMDQ2NjA3MDYwOTU0MzIxMQ.GzuuTh.cvAwmQYiCxd_y2tD8wKekNj7xfV7p_3uRL-n2g',
                        'Accept': 'text/plain'
                        }
                        SMA20_content = str('MA20 - Symbol:'+symbol+' RSI: '+RSI_str)
                                
                        data = {
                            "content": SMA20_content
                        }
                        

                        r = requests.post("https://discord.com/api/v9/channels/1010098756663922728/messages", headers=header, data=data, files=files)
                        
                        
                        time.sleep(1)
            except:
                print("Error in MA20")    
            try:
                if SMA50 > open1:
                    if SMA50 < close1:        
                        min_price = new_df.tail(150).min()
                        max_price = new_df.tail(150).max()
                        header = {
                        'authorization': 'MTAxMDQ2NjA3MDYwOTU0MzIxMQ.GzuuTh.cvAwmQYiCxd_y2tD8wKekNj7xfV7p_3uRL-n2g',
                        'Accept': 'text/plain'
                        }
                        ap0 = [
                        mpf.make_addplot(new_df['RSI'], color='#0000ff', panel=2, ylabel='RSI'),
                        mpf.make_addplot(new_df['SMA50'], color='#42032C', panel=0) 
                        ]
                        mpf.plot(
                            new_df,
                            addplot=ap0,
                            title = f"{symbol} Price",  
                            show_nontrading=False, 
                            figratio=(10,7), 
                            figscale=1.5, 
                            xrotation=90, 
                            tight_layout=False,  
                            type='candle',
                            update_width_config=dict(candle_linewidth=1.5),
                            ylim=(min_price.low, max_price.high),
                            volume=True,
                            num_panels=3,
                            savefig="C:/Users/maaguilar/Documents/Chart/fig.png" 
                            )

                        files = {'media': open("C:/Users/maaguilar/Documents/Chart/fig.png", 'rb')}

                        
                        SMA50_content = str('MA50 - Symbol:'+symbol+' RSI: '+RSI_str)
                          
                        data = {
                            "content": SMA50_content
                        }
                        
                        r = requests.post("https://discord.com/api/v9/channels/1010098756663922728/messages", headers=header, data=data, files=files)
                        time.sleep(1)        
            except:
                print("Error in MA50")    
            try:
                if SMA100 > open1:
                    if SMA100 < close1:     
                        min_price = new_df.tail(150).min()
                        max_price = new_df.tail(150).max()

                        header = {
                        'authorization': 'MTAxMDQ2NjA3MDYwOTU0MzIxMQ.GzuuTh.cvAwmQYiCxd_y2tD8wKekNj7xfV7p_3uRL-n2g',
                        'Accept': 'text/plain'
                        }
                        ap0 = [
                            mpf.make_addplot(new_df['RSI'], color='#0000ff', panel=2, ylabel='RSI'),
                            mpf.make_addplot(new_df['SMA100'], color='#1C3879', panel=0) 
                        ]
                        mpf.plot(
                            new_df,
                            addplot=ap0,
                            title = f"{symbol} Price",  
                            show_nontrading=False, 
                            figratio=(10,7), 
                            figscale=1.5, 
                            xrotation=90, 
                            tight_layout=False,  
                            type='candle',
                            update_width_config=dict(candle_linewidth=1.5),
                            ylim=(min_price.low, max_price.high),
                            volume=True,
                            num_panels=3,
                            savefig="C:/Users/maaguilar/Documents/Chart/fig.png" 
                        )

                        files = {'media': open("C:/Users/maaguilar/Documents/Chart/fig.png", 'rb')}

                    
                        SMA100_content = str('MA100 - Symbol:'+symbol+' RSI: '+RSI_str)
                      
                        data = {
                            "content": SMA100_content
                        }
                    
                        r = requests.post("https://discord.com/api/v9/channels/1010098756663922728/messages", headers=header, data=data, files=files)
                        time.sleep(1)
            except:
                print("Error in MA100")    
            try:
                if SMA200 > open1:
                    if SMA200 < close1:     
                        min_price = new_df.tail(150).min()
                        max_price = new_df.tail(150).max()
                        header = {
                        'authorization': 'MTAxMDQ2NjA3MDYwOTU0MzIxMQ.GzuuTh.cvAwmQYiCxd_y2tD8wKekNj7xfV7p_3uRL-n2g',
                        'Accept': 'text/plain'
                        }
                    
                        ap0 = [
                            mpf.make_addplot(new_df['RSI'], color='#0000ff', panel=2, ylabel='RSI'),
                            mpf.make_addplot(new_df['SMA200'], color='#2B7A0B', panel=0) 
                        ]
                        
                        mpf.plot(
                            new_df,
                            addplot=ap0,
                            title = f"{symbol} Price",  
                            show_nontrading=False, 
                            figratio=(10,7), 
                            figscale=1.5, 
                            xrotation=90, 
                            tight_layout=False,  
                            type='candle',
                            update_width_config=dict(candle_linewidth=1.5),
                            ylim=(min_price.low, max_price.high),
                            volume=True,
                            num_panels=3,
                            savefig="C:/Users/maaguilar/Documents/Chart/fig.png"
                            
                        )

                        files = {'media': open("C:/Users/maaguilar/Documents/Chart/fig.png", 'rb')}

                    
                        SMA200_content = str('MA200 - Symbol:'+symbol+' RSI: '+RSI_str)
                      
                        data = {
                            "content": SMA200_content
                        }
                    
                    
                        r = requests.post("https://discord.com/api/v9/channels/1010098756663922728/messages", headers=header, data=data, files=files)
                        
                        time.sleep(1)
            except:
                print("Error in MA200")          

            
            try:
                if SMA20_2 < SMA50_2:
                    if SMA20 > SMA50:        
                        min_price = new_df.tail(202).min()
                        max_price = new_df.tail(202).max()
                        header = {
                        'authorization': 'MTAxMDQ2NjA3MDYwOTU0MzIxMQ.GzuuTh.cvAwmQYiCxd_y2tD8wKekNj7xfV7p_3uRL-n2g',
                        'Accept': 'text/plain'
                        }
                        ap0 = [
                        mpf.make_addplot(new_df['RSI'], color='#0000ff', panel=2, ylabel='RSI'),
                        mpf.make_addplot(new_df['SMA50'], color='#42032C', panel=0), 
                        mpf.make_addplot(new_df['SMA20'], color='#277BC0', panel=0),
                        ]
                        mpf.plot(
                            new_df,
                            addplot=ap0,
                            title = f"{symbol} Price",  
                            show_nontrading=False, 
                            figratio=(10,7), 
                            figscale=1.5, 
                            xrotation=90, 
                            tight_layout=False,  
                            type='candle',
                            update_width_config=dict(candle_linewidth=1.5),
                            ylim=(min_price.low, max_price.high),
                            volume=True,
                            num_panels=3,
                            savefig="C:/Users/maaguilar/Documents/Chart/fig.png" 
                            )

                        files = {'media': open("C:/Users/maaguilar/Documents/Chart/fig.png", 'rb')}

                        
                        SMA20_SMA50_content = str('MA20 crossed to MA50 - Symbol:'+symbol+' RSI: '+RSI_str)
                          
                        data = {
                            "content": SMA20_SMA50_content
                        }
                        
                        r = requests.post("https://discord.com/api/v9/channels/1011651186723651696/messages", headers=header, data=data, files=files)
                        time.sleep(1)        
            except:
                print("Error in cross 20 50")
            
            try:
                if SMA20_2 < SMA100_2:
                    if SMA20 > SMA100:        
                        min_price = new_df.tail(150).min()
                        max_price = new_df.tail(150).max()
                        header = {
                        'authorization': 'MTAxMDQ2NjA3MDYwOTU0MzIxMQ.GzuuTh.cvAwmQYiCxd_y2tD8wKekNj7xfV7p_3uRL-n2g',
                        'Accept': 'text/plain'
                        }
                        ap0 = [
                        mpf.make_addplot(new_df['RSI'], color='#0000ff', panel=2, ylabel='RSI'),
                        mpf.make_addplot(new_df['SMA100'], color='#1C3879', panel=0), 
                        mpf.make_addplot(new_df['SMA20'], color='#277BC0', panel=0),
                        ]
                        mpf.plot(
                            new_df,
                            addplot=ap0,
                            title = f"{symbol} Price",  
                            show_nontrading=False, 
                            figratio=(10,7), 
                            figscale=1.5, 
                            xrotation=90, 
                            tight_layout=False,  
                            type='candle',
                            update_width_config=dict(candle_linewidth=1.5),
                            ylim=(min_price.low, max_price.high),
                            volume=True,
                            num_panels=3,
                            savefig="C:/Users/maaguilar/Documents/Chart/fig.png" 
                            )

                        files = {'media': open("C:/Users/maaguilar/Documents/Chart/fig.png", 'rb')}

                        
                        SMA20_SMA100_content = str('MA20 crossed to MA100 - Symbol:'+symbol+' RSI: '+RSI_str)
                          
                        data = {
                            "content": SMA20_SMA100_content
                        }
                        
                        r = requests.post("https://discord.com/api/v9/channels/1011651186723651696/messages", headers=header, data=data, files=files)
                        time.sleep(1)        
            except:
                print("Error in cross 20 100")
            
            try:
                if SMA20_2 < SMA200_2:
                    if SMA20 > SMA200:        
                        min_price = new_df.tail(150).min()
                        max_price = new_df.tail(150).max()
                        header = {
                        'authorization': 'MTAxMDQ2NjA3MDYwOTU0MzIxMQ.GzuuTh.cvAwmQYiCxd_y2tD8wKekNj7xfV7p_3uRL-n2g',
                        'Accept': 'text/plain'
                        }
                        ap0 = [
                        mpf.make_addplot(new_df['RSI'], color='#0000ff', panel=2, ylabel='RSI'),
                        mpf.make_addplot(new_df['SMA200'], color='#2B7A0B', panel=0), 
                        mpf.make_addplot(new_df['SMA20'], color='#277BC0', panel=0),
                        ]
                        mpf.plot(
                            new_df,
                            addplot=ap0,
                            title = f"{symbol} Price",  
                            show_nontrading=False, 
                            figratio=(10,7), 
                            figscale=1.5, 
                            xrotation=90, 
                            tight_layout=False,  
                            type='candle',
                            update_width_config=dict(candle_linewidth=1.5),
                            ylim=(min_price.low, max_price.high),
                            volume=True,
                            num_panels=3,
                            savefig="C:/Users/maaguilar/Documents/Chart/fig.png" 
                            )

                        files = {'media': open("C:/Users/maaguilar/Documents/Chart/fig.png", 'rb')}

                        
                        SMA20_SMA200_content = str('MA20 crossed to MA200 - Symbol:'+symbol+' RSI: '+RSI_str)
                          
                        data = {
                            "content": SMA20_SMA200_content
                        }
                        
                        r = requests.post("https://discord.com/api/v9/channels/1011651186723651696/messages", headers=header, data=data, files=files)
                        time.sleep(1)        
            except:
                print("Error in cross 20 200")

            try:
                if SMA50 > SMA100:
                    if SMA50_2 < SMA100_2:
                        if SMA20 > SMA50:
                            min_price = zoom_df.tail(50).min()
                            max_price = zoom_df.tail(50).max()
                            header = {
                            'authorization': 'MTAxMDQ2NjA3MDYwOTU0MzIxMQ.GzuuTh.cvAwmQYiCxd_y2tD8wKekNj7xfV7p_3uRL-n2g',
                            'Accept': 'text/plain'
                            }
                            ap0 = [
                            mpf.make_addplot(zoom_df['RSI'], color='#0000ff', panel=2, ylabel='RSI'),
                            mpf.make_addplot(zoom_df['SMA20'], color='#3CCF4E', panel=0),
                            mpf.make_addplot(zoom_df['SMA50'], color='#3120E0', panel=0),
                            mpf.make_addplot(zoom_df['SMA100'], color='#FFEA11', panel=0),
                            ]
                            mpf.plot(
                                zoom_df,
                                addplot=ap0,
                                title = f"{symbol} Price",  
                                show_nontrading=False, 
                                figratio=(10,7), 
                                figscale=1.5, 
                                xrotation=90, 
                                tight_layout=False,  
                                type='candle',
                                update_width_config=dict(candle_linewidth=1.5),
                                ylim=(min_price.low, max_price.high),
                                volume=True,
                                num_panels=3,
                                savefig="C:/Users/maaguilar/Documents/Chart/fig.png" 
                                )

                            files = {'media': open("C:/Users/maaguilar/Documents/Chart/fig.png", 'rb')}

                        
                            triple_threat_content = str('3ple Threat MA - Symbol:'+symbol+' RSI: '+RSI_str)
                          
                            data = {
                                "content": triple_threat_content
                            }
                        
                            r = requests.post("https://discord.com/api/v9/channels/1011889683573256233/messages", headers=header, data=data, files=files)
                            time.sleep(1)                     
            except:
                print("Error in cross 20 50 100")
            del klines_1hr, klines_1d
    

'''
for x in prices:
    for y in x:
        time.sleep(1)
        #print (y, ': ' , x[y])
        klines = client.get_historical_klines("BNBBTC", Client.KLINE_INTERVAL_1MINUTE, "1 day ago UTC")

        

        #print(message)
    message = str(x)
    data = {
    "content": message
    }
        
    header = {
    'authorization': 'MTAxMDQ2NjA3MDYwOTU0MzIxMQ.GzuuTh.cvAwmQYiCxd_y2tD8wKekNj7xfV7p_3uRL-n2g',
     'Accept': 'text/plain'
     }
        
    r = requests.post("https://discord.com/api/v9/channels/1009805115026325535/messages", headers=header, data=data).json()
        
        


message = str(price)

print(message)


data = {
    "content": message
    }
        
header = {
     'authorization': 'MTAxMDQ2NjA3MDYwOTU0MzIxMQ.GzuuTh.cvAwmQYiCxd_y2tD8wKekNj7xfV7p_3uRL-n2g',
      'Accept': 'text/plain'
     }
        
r = requests.post("https://discord.com/api/v9/channels/1009805115026325535/messages", headers=header, data=data).json()
        
'''