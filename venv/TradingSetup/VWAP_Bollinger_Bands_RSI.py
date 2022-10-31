import sys, os
sys.path.extend([f'{item[0]}' for item in os.walk(".") if os.path.isdir(item[0])])
import TradingPlatform.Binance.DataSource.BinanceAPI as binance
import TradingPlatform.Binance.DataSource.BinanceSecretKey as apk
import TradingTool.APIAttr as attr
import TradingTool.APIFunc as func
import plotly.graph_objects as go
import datetime  as dt
import pandas    as pd
import pandas_ta as ta
import requests
import time

header = attr.header

def VWAP_BB_RSI(df,symbol):  
    try: 
        df = func.get_vwap(df)
    except: 
        pass
        #print("Error getting vwap")

    try: 
        df = func.get_rsi(df, length=16)
    except: 
        pass
        #print("Error getting rsi")

    try: 
        my_bbands = func.get_bb(df)
    except: 
        pass
        #print("Error getting bbands")

    if my_bbands is not None: 
        df=df.join(my_bbands)
    else:
        pass
        #print("Error getting bollinger band")
    
    try: 
        df = func.get_atr(df, length=14)
    except: 
        pass
        #print("Error getting atr")

    try: 
        slatr = func.get_slatr(df, perc_loss=1.2)
    except TypeError: 
        pass
        #print("Error getting slatr")

    try: 
        tpatr = func.get_tpatr(slatr=slatr, perc_gain=2)
    except TypeError: 
        pass
        #print("Error getting tpatr")

    try:
        if (df.Close[-1] > df['VWAP'][-1] 
            and df['BBL_14_2.0'][-1]  > df.Close[-1]
            and df['BBL_14_2.0'][-1] > df['VWAP'][-1] 
            and df.RSI[-1] < 45):
                #buy long position
                all_tickers = binance.all_tickers()
                price = float(func.get_price(symbol, all_tickers))
                TP = str(price + tpatr)
                SL = str(price - slatr)
                open = str(price)
#will remove starting here   
                content = str('Long position - Symbol: '+symbol+' EP: '+open+' TP: '+TP+' SL: '+SL)
                data = { "content": content }
                r = requests.post("https://discord.com/api/v9/channels/1032975832186093608/messages", headers=header, data=data)
                print(content)
#will remove ending here  
                time.sleep(1)   
                return open, TP,  SL
    except: print("Error getting long position")
        
    try:        
        if (df['VWAP'][-1] > df.Close[-1] 
            and df.Close[-1] > df['BBU_14_2.0'][-1] 
            and df['VWAP'][-1]  > df['BBU_14_2.0'][-1] 
            and df.RSI[-1] > 55):
                #sell short position
                all_tickers = binance.all_tickers()
                price = float(func.get_price(symbol, all_tickers))
                TP = str(price - tpatr)
                SL = str(price + slatr)
                open = str(price)               
#will remove starting here                
                content = str('Short position - Symbol: '+symbol+' EP: '+open+' TP: '+TP+' SL: '+SL)
                data = { "content": content }
                r = requests.post("https://discord.com/api/v9/channels/1032975832186093608/messages", headers=header, data=data)
                print(content)
#will remove ending here                  
                time.sleep(1)  
                return open, TP,  SL
    except: print("Error getting short position")