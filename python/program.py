import time
import pandas as pd
from ks_API import KSTrade_API
import matplotlib.pyplot as plt
from datetime import datetime as dt
#from backtesting import BackTestingEngine
from trading_strategy import TradingStrategy
from nsepy.symbols import get_index_constituents_list


def Main(broker_API, tickers):
    strategy = {}
    OHLCV_NSE = {}
    Analysis_NSE = TradingStrategy()
    Analysis_NSE.Exchange = "NSE"
    Analysis_NSE.Dataset = "Close"
    for ticker in tickers:
        df = Analysis_NSE.HistoricData(ticker, interval = "5m")
        OHLCV_NSE[ticker] = df[["Open", "High", "Low", "Close", "Volume"]].copy()
    for ticker in OHLCV_NSE:
        strategy[ticker] = Analysis_NSE.MA_Crossover(OHLCV_NSE[ticker], MA_type = "HMA")
    broker_API.TickersData = strategy
    orders = broker_API.Run()
    return



if __name__ == "__main__":
    Nifty50 = get_index_constituents_list(index = "Nifty50")["Symbol"].to_list()
    Nifty100 = get_index_constituents_list(index = "Nifty100")["Symbol"].to_list()
    Broker_API = KSTrade_API()
    start = time.time()
    timeout = time.time() + 60*11
    print("waiting...!")
    print(Nifty50)
    while time.time() <= timeout:
        try:
            if (dt.now().second == 0) and (dt.now().minute % 5 == 0):
                print(dt.now())
                st_time = time.time()
                Trade = Main(Broker_API, Nifty50)
                ed_time = time.time()
                time.sleep((60*5) - (ed_time - st_time + 2))
                print(dt.now())
        except Exception as ex:
            print(ex)
            break

    Broker_API.Client.logout()

