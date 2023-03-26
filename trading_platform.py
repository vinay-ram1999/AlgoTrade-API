import numpy as np
import pandas as pd
from collections import deque
from technical_analysis import TechnicalAnalysis


class TradingPlatform(object):
    def __init__(self):
        self.Data = None
        self.Tickers = list()
        self.long_dataset = "long"
        self.short_dataset = "short"
        self.TickerPosition = dict()
        self.x = deque(maxlen = 10) #
        self.position = None
        self.order_pending = None
        return


    @property
    def TickersData(self):
        if self.Data:
            return self.Data
        else:
            raise ValueError("Set the TickersData")


    @TickersData.setter
    def TickersData(self, data):
        self.Data = data


    @property
    def Get_Tickers(self):
        data = self.TickersData
        for ticker in data:
            self.Tickers += [ticker]
        return self.Tickers


    def SignalParser(self, Data):
        self.is_long = None
        self.is_short = None
        self.signal_parsed = None
        try:
            if Data[self.long_dataset][-1] == 1.0:
                self.is_long = True
                delattr(self, "is_short")
            elif Data[self.short_dataset][-1] == 1.0:
                self.is_short = True
                delattr(self, "is_long")
            else:
                delattr(self, "is_long")
                delattr(self, "is_short")
            self.signal_parsed = True
        except Exception as ex:
            print("SignalParser error:", type(ex).__name__, ex)
            print("Please provide the Strategy implemented Data")
            pass
        return self.signal_parsed


    def PositionType(self, Data):
        signal = self.SignalParser(Data)
        if signal:
            if hasattr(self, "is_long") and self.is_long:
                self.position = "BUY"
            elif hasattr(self, "is_short") and self.is_short:
                self.position = "SELL"
            else:
                self.position = None
        else:
            print("Signal is not parsed. Check SignalParser")
        return self.position


    @property
    def Get_TickerPosition(self):
        data = self.TickersData
        for ticker in data:
            position = self.PositionType(data[ticker])
            price = data[ticker]["Close"][-1]
            self.TickerPosition[ticker] = [position, price]
        return self.TickerPosition




