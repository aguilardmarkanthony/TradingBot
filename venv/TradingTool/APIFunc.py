import pandas_ta as ta
import TradingPlatform.Binance.DataSource.BinanceAPI as binance
import TradingTool.APIAttr as attr
import TradingTool.APIFunc as func
import pandas as pd
def get_bb(df):
    my_bbands = ta.bbands(df.Close, length=14, std=2.0)
    return my_bbands

def get_symbol(s):
    symbol = str(s['symbol'])
    return symbol

def get_base(s):
    base = s[-3:]
    return base

def check_base(base):
    if base != 'USD':
        return True

def check_contract_type(contract_type):
    if contract_type != 'PERP':
        return True

def exclude_fiat(symbol):
    if   symbol == "USDCUSDT":
        return True
    elif symbol == "BUSDUSDT":
        return True
    elif symbol == "USDCUSDT":
        return True
    elif symbol == "USDPUSDT":
        return True

def check_df_empty(data):
    if data.empty:
        return True

def get_vwap(df):
    df["VWAP"]=ta.vwap(df.High, df.Low, df.Close, df.Volume)
    return df

def get_rsi(df, length):
    df['RSI']=ta.rsi(df.Close, length=length)
    return df

def get_atr(df, length):
    df['ATR']=ta.atr(high=df.High, low=df.Low, close=df.Close, length=length)
    return df

def get_slatr(df, perc_loss):
    slatr = float(perc_loss)*float(df.ATR[-1])
    return slatr

def get_tpatr(slatr, perc_gain):
    tpatr = float(slatr)*float(perc_gain)
    return tpatr

def get_price(symbol, all_tickers):
    for t in all_tickers:
        if t['symbol'] != symbol:
            continue
        else:
            price = float(t['price'])
            break
    return price


def get_base_df(symbol, start):
    klines = binance.futures_historical_klines(symbol=symbol, start=start)
    data = pd.DataFrame(klines, columns=attr.columns)
    if data.empty:
        pass
        #print("Empty df")
    else:
        data.dropna(subset=['Open', 'Close', 'Low', 'High', 'Volume'])
        df = data[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
        df = df.astype(float)
        df['open_time'] = pd.to_datetime(data.open_time, unit='ms') 
        df=df[df.High!=df.Low]
        df.set_index("open_time", inplace=True, drop=True)
        return df

def get_contract_type(symbol_raw):
    symbol_raw = str(symbol_raw)
    symbol_split = symbol_raw.split('_')
    contract_type = symbol_split[1]
    return contract_type

def get_symbol(symbol_raw):
    symbol_raw = str(symbol_raw)
    symbol_split = symbol_raw.split('_')
    symbol = symbol_split[0]
    return symbol

def modify_symbol(symbol):
    symbol = str(symbol)+str('T')
    return symbol

