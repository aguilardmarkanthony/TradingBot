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
