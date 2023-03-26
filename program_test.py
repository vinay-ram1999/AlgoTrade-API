import pandas as pd
#import pynse
import datetime as dt
from ks_API import KSTrade_API
import matplotlib.pyplot as plt
from backtesting import BackTestingEngine
from trading_strategy import TradingStrategy



if __name__ == "__main__":
    st = dt.datetime.now().timestamp()
    print(dt.datetime.now())

    #pyNSE = pynse.Nse()
    #pyNSE_tickers = pyNSE.symbols
    #close_df = pd.DataFrame()
    IND_tickers = ["ITC", "TRIDENT", "BRITANNIA", "MARUTI", "MRF", "ADANIPORTS", "EICHERMOT", "TITAN", "TATAMOTORS", "ONGC", "NTPC", "LT", "TATASTEEL", "WIPRO", "SBIN", "AXISBANK", "ICICIBANK", "BPCL", "HDFCBANK", "IOC"]
    #Nifty50 = pyNSE_tickers["Nifty50"]
    #Nifty100 = pyNSE_tickers["Nifty100"]

    #print(Nifty50)
    Nifty50 = ["TATAMOTORS"]

    OHLCV_NSE = {}

    start_date = dt.date(2011,1,1)
    end_date = dt.date.today()

    Analysis_NSE = TradingStrategy()

    Analysis_NSE.Exchange = "NSE"
    Analysis_NSE.Dataset = "Close"

    for ticker in IND_tickers:
        df = Analysis_NSE.HistoricData(ticker)    # default gives 1d ohlcv data for 5y
        #df = Analysis_NSE.HistoricData(ticker, interval = "15m")
        OHLCV_NSE[ticker] = df[["Open", "High", "Low", "Close", "Volume"]].copy()

    ed = dt.datetime.now().timestamp()

    #print(OHLCV_NSE)

    indicators = {}
    strategies = {}

    for ticker in OHLCV_NSE:
        #indicators[ticker]["MACD"] = Analysis_NSE.MACD(OHLCV_NSE[ticker])
        #indicators[ticker]["BBANDS"] = Analysis_NSE.BollingerBand(OHLCV_NSE[ticker])
        strategies[ticker] = Analysis_NSE.MA_Crossover(OHLCV_NSE[ticker], MA_type = "HMA")
        #strategies[ticker] = Analysis_NSE.nPeriod_RSI(OHLCV_NSE[ticker])
        #strategies[ticker] = Analysis_NSE.nPeriod_RSI(OHLCV_NSE[ticker])

    #print(strategies)
    #print(strategies["TATAMOTORS"][["long", "short"]].tail(60))
    #print(strategies["TATAMOTORS"][["long", "short"]].diff().tail(60))
    #exit()

    trade_API = KSTrade_API()
    trade_API.TickersData = strategies
    #c = trade_API.WatchlistName_req()
    #o = trade_API.Buy_order(1407)
    #c = trade_API.TStop_loss()
    #print(o,c)
    s = trade_API.Scripmaster_req()
    print(s["ITC"])
    #quo = trade_API.Client.quote(instrument_token = 1407)
    #print(quo["success"][0]["stk_name"])
    #d = trade_API.Watchlist_req("TradeAPI")
    #balance = trade_API.Margin_req()
    #print(balance)
    #a = trade_API.OrderExecution()
    #print(a)

    #print(ed-st)




