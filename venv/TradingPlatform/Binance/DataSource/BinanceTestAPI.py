import sys, os
sys.path.extend([f'{item[0]}' for item in os.walk(".") if os.path.isdir(item[0])])
import BinanceSecretKey as apk
import TradingTool.APIAttr as attr
import pandas as pd
import BinanceAPI as binance
from binance.client import Client
from binance.helpers import round_step_size


def exchange_info():
  try:
    client = Client(apk.api_key, apk.api_secret)
    exchange_info = client.get_exchange_info()
    return exchange_info
  except:
    print("Cannot get exchange info")
  

def historical_klines(symbol, interval):
  try:
    client = Client(apk.api_key, apk.api_secret)
    historical_klines = client.get_historical_klines(symbol, Client.KLINE_INTERVAL_5MINUTE, interval) #need to change, temporarily hard coded params
    return historical_klines
  except:
    print("Cannot get historical klines")

def orderbook_tickers():
  try:
    client = Client(apk.api_key, apk.api_secret)
    orderbook_tickers = client.get_orderbook_tickers()
    return orderbook_tickers
  except:
    print("Cannot get orderbook tickers")

def all_tickers():
  try:
      client = Client(apk.api_key, apk.api_secret)
      all_tickers = client.get_all_tickers()
      return all_tickers
  except:
      print("Cannot get all tickers")

def futures_historical_klines(symbol, start):
  try:
    client = Client(apk.api_key, apk.api_secret)
    futures_historical_klines = client.futures_historical_klines(symbol=symbol, interval=attr.KLINE_INTERVAL_5MINUTE, start_str=start) #need to change, temporarily hard coded params
    return futures_historical_klines
  except:
    print("Cannot get futures historical klines")

def futures_exchange_info():
  try:
    client = Client(apk.api_key, apk.api_secret)
    futures_exchange_info = client.futures_coin_exchange_info()
    return futures_exchange_info
  except:
    print("Cannot get futures exchange info")

#MARKET order
def futures_market_order(symbol, quantity, positionSide): 
  try:
    client = Client(apk.api_key, apk.api_secret)
    client.futures_create_order( symbol=symbol, side='BUY', positionSide=positionSide, type='MARKET', quantity=quantity )
  except:
    print("Cannot create order")


#TAKE_PROFIT_MARKET order
def futures_tp_market_order(symbol,tp, positionSide):
  try:
    client = Client(apk.api_key, apk.api_secret)
    client.futures_create_order(symbol=symbol, side='SELL', positionSide=positionSide, type='TAKE_PROFIT_MARKET', stopPrice=tp, closePosition=True, timeInForce='GTE_GTC', workingType='MARK_PRICE', priceProtect=True )
  except:
    print("Cannot create tp market order")

#STOP_MARKET order
def futures_sl_market_order(symbol, sl, positionSide):
  try:
    client = Client(apk.api_key, apk.api_secret)
    client.futures_create_order( symbol=symbol, side='SELL', positionSide=positionSide, type='STOP_MARKET', stopPrice=sl, closePosition=True, timeInForce='GTE_GTC', workingType='MARK_PRICE', priceProtect=True ) 
  except:
    print("Cannot create sl market order")

def get_account_balance():
  try:
    client = Client(apk.api_key, apk.api_secret)
    balance = client.futures_account_balance()[6]['balance']
    return float(balance)
  except:
    print("Cannot get account balance")

def get_min_quantity(symbol):
  try:
    client = Client(apk.api_key, apk.api_secret)
    info = exchange_info()
    for item in info['symbols']:
        if item['symbol'] == symbol:
            for f in item['filters']:
                if f['filterType'] == 'PRICE_FILTER':
                    return f['tickSize']
  except:
    print("Cannot get get_min_quantity")

def futures_account_balance(symbol):
  try:
    client = Client(apk.api_key, apk.api_secret)
    acc_balance = client.futures_account_balance()[0]
    for check_balance in acc_balance["accountAlias"]:
        if check_balance["asset"] == symbol:
            balance = check_balance["balance"]
  except:
    print("Cannot get futures_account_balance")


