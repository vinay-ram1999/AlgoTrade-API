#import talib
import numpy as np
import pandas as pd
import yfinance as yf
import statsmodels.api as sm
import matplotlib.pyplot as plt
from pyti.hull_moving_average import hull_moving_average as hma
from pyti.weighted_moving_average import weighted_moving_average as wma


class TechnicalAnalysis(object):
    def __init__(self):
        self.exchange = None
        self.dataset = None
        return

    @property
    def Exchange(self):
        if self.exchange:
            return self.exchange
        else:
            raise ValueError("Declare the Exchange")

    @Exchange.setter
    def Exchange(self, EX):
        self.exchange = EX

    @property
    def Ticker_ext(self):
        ext = ""
        if self.exchange == "NSE":
            ext = ".NS"
        elif self.exchange == "BSE":
            ext = ".BS"
        elif self.exchange == None:
            raise ValueError("Declare the Exchange")
        self.yf_ticker_ext = ext
        return self.yf_ticker_ext

    @property
    def Dataset(self):
        if self.dataset:
            return self.dataset
        else:
            raise ValueError("Declare the Dataset")

    @Dataset.setter
    def Dataset(self, Var):
        self.dataset = Var


    def HistoricData(self, ticker, interval = "1d", threads = None, start = None, end = None):
        self.yfTicker = yf.Ticker(ticker + self.Ticker_ext)
        period = None
        if start == None and end == None:
            if interval in ["1m"]:
                period = "7d"
            elif interval in ["2m", "5m", "15m", "30m", "90m"]:
                period = "60d"
            elif interval in ["60m", "1hr"]:
                period = "730d"
            elif interval in ["1d", "5d", "1wk", "1mo", "3mo"] and period == None:
                period = "5y"
            #historic_data = self.yfTicker.history(period = period, interval = interval, threads = threads)
            historic_data = self.yfTicker.history(period = period, interval = interval)
        else:
            #historic_data = self.yfTicker.history(start = start, end = end, threads = threads) # WARNING history() got an unexpected keyword argument 'threads'
            historic_data = self.yfTicker.history(start = start, end = end)
        historic_data.fillna(method = "bfill", inplace = True)
        #historic_data.drop(historic_data.tail(1).index,inplace=True)
        return historic_data


    def MovingAvg(self, Data, n=9, MA_type = "SMA"):
        df = Data.copy()
        DataSet = self.Dataset
        if MA_type == "SMA":
            df[f"{MA_type}"] = df[DataSet].rolling(window = n).mean()
        elif MA_type == "EMA":
            df[f"{MA_type}"] = df[DataSet].ewm(span=n, min_periods=n).mean()
        elif MA_type == "WMA":
            df[f"{MA_type}"] = wma(df[DataSet], n)
        elif MA_type == "HMA":
            df[f"{MA_type}"] = hma(df[DataSet], n)
        else:
            print("Enter a valid Moving average type")
            raise(TypeError)
        return df[[DataSet, f"{MA_type}"]]


    def MACD_Crossover(self, Data, a=12 ,b=26, c=9, signal_type = "SLC", MA_type = "EMA"):
        """function to calculate MACD
        typical values a(fast moving average) = 12;
                        b(slow moving average) =26;
                        c(signal line ma window) =9;
            SLC (Signal Line Crossover)
        Bullish Signal Line Crossovers occur when the MACD Line crosses above the Signal Line.
        Bearish Signal Line Crossovers occur when the MACD Line crosses below the Signal Line.
            ZLC (Zero Line Crossover)
        Bullish Zero Line Crossovers occur when the MACD Line crosses above the Zero Line and go from negative to positive.
        Bearish Zero Line Crossovers occur when the MACD Line crosses below the Zero Line and go from positive to negative.
        """
        df = Data.copy()
        DataSet = self.Dataset
        MA_fast = self.MovingAvg(df, n = a, MA_type = MA_type)
        MA_slow = self.MovingAvg(df, n = b, MA_type = MA_type)
        df["ma_fast"] = MA_fast[f"{MA_type}"]
        df["ma_slow"] = MA_slow[f"{MA_type}"]
        df["macd"] = df["ma_fast"] - df["ma_slow"]
        df["signal_line"] = df["macd"].ewm(span=c, min_periods=c).mean()
        df["signal"] = 0.0
        if signal_type == "SLC":
            df["signal"] = np.where(df["macd"] > df["signal_line"], 1.0, 0.0)
        elif signal_type == "ZLC":
            df["signal"] = np.where(df["macd"] > 0, 1.0, 0.0)
        df["%s_signal" %signal_type] = df["signal"].diff()
        for i in df["%s_signal" %signal_type]:
            if i==1.0:
                print("BUY")
            elif i==-1.0:
                print("SELL")
        return df[[DataSet, "macd", "signal_line", "%s_signal" %signal_type]]


    def RSI(self, Data, n=14, UL = 70, LL = 30):
        """ RSI (RSI value range is 0-100)
        Any number above 70 should be considered overbought (OB).
        Any number below 30 should be considered oversold (OS).
        """
        df = Data.copy()
        DataSet = self.Dataset
        df["change"] = df[DataSet] - df[DataSet].shift(1)
        df["gain"] = np.where(df["change"]>=0, df["change"], 0)
        df["loss"] = np.where(df["change"]<0, -1*df["change"], 0)
        df["avgGain"] = df["gain"].ewm(span=n, min_periods=n).mean()
        df["avgLoss"] = df["loss"].ewm(span=n, min_periods=n).mean()
        df["rs"] = df["avgGain"]/df["avgLoss"]
        df["rsi"] = 100 - (100/ (1 + df["rs"]))
        df["signal"] = np.where(df["rsi"] <= LL, "OS", (np.where(df["rsi"] >= UL, "OB", "N")))
        return df[[DataSet, "rsi", "signal"]]


    def BollingerBand(self, Data, n=20, s=2):
        """ Used to measure the volatality in conjunction with ATR
        When prices move up near the upper band or even break through the upper band, that security may be seen as overbought.
        When prices move down near the lower band or even break through the lower band, that security may be seen as oversold.
        """
        df = Data.copy()
        DataSet = self.Dataset
        df["MB"] = df[DataSet].rolling(window = n).mean()
        df["UB"] = df["MB"] + s*df[DataSet].rolling(window = n).std(ddof=0)
        df["LB"] = df["MB"] - s*df[DataSet].rolling(window = n).std(ddof=0)
        df["BB_Width"] = df["UB"] - df["LB"]
        df["signal"] = np.where(df[DataSet] > df["UB"], "OB", (np.where(df[DataSet] < df["LB"], "OS", "N")))
        return df[[DataSet, "MB", "UB", "LB", "BB_Width", "signal"]]


    def ATR(self, Data, n=14):
        """ Average True Range which can used to measure the volatality in conjunction with Bollinger Band
        """
        df = Data.copy()
        DataSet = self.Dataset
        df["H-L"] = df["High"] - df["Low"]
        df["H-PC"] = abs(df["High"] - df[DataSet].shift(1))
        df["L-PC"] = abs(df["Low"] - df[DataSet].shift(1))
        df["TR"] = df[["H-L","H-PC","L-PC"]].max(axis=1, skipna=False)
        df["ATR"] = df["TR"].ewm(span=n, min_periods=n).mean()
        return df["ATR"]


    def ADX(self, Data, n=14, UL = 25, LL = 20, DI_Crossover = False):
        """ Trend Strength (TS)
        To analyze trend strength, the focus should be on the ADX line and not the +DI or -DI lines.
        ADX reading above 25 indicated a strong trend (ST), while a reading below 20 indicated a weak or non-existent trend (WT).
        A reading between those two values, would be considered indeterminable (NA).
            DI Crossover (DIC)
        Bullish DI Crossover:
        ADX must be over 25 (strong trend).
        The +DI crosses above the -DI.
        Bearish DI Crossover:
        ADX must be over 25 (strong trend).
        The +DI crosses below the -DI.
        """
        df = Data.copy()
        DataSet = self.Dataset
        df["ATR"] = self.ATR(df, n)
        df["upmove"] = df["High"] - df["High"].shift(1)
        df["downmove"] = df["Low"].shift(1) - df["Low"]
        df["+dm"] = np.where((df["upmove"]>df["downmove"]) & (df["upmove"] >0), df["upmove"], 0)
        df["-dm"] = np.where((df["downmove"]>df["upmove"]) & (df["downmove"] >0), df["downmove"], 0)
        df["+di"] = 100 * (df["+dm"]/df["ATR"]).ewm(span=n, min_periods=n).mean()
        df["-di"] = 100 * (df["-dm"]/df["ATR"]).ewm(span=n, min_periods=n).mean()
        df["ADX"] = 100 * abs((df["+di"] - df["-di"])/(df["+di"] + df["-di"])).ewm(span=n, min_periods=n).mean()
        df["TS"] = np.where(df["ADX"] > UL, "ST", (np.where(df["ADX"] < LL, "WT", "NA")))
        df["DI_signal"] = 0.0
        if DI_Crossover:
            df["DI_signal"] = np.where(df["ADX"] > UL, (np.where(df["+di"] > df["-di"], 1.0, 0.0)), 0.0)
            df["DI_signal"] = df["DI_signal"].diff()
        return df[[DataSet, "ATR", "+di", "-di", "ADX", "TS", "DI_signal"]]


    def CMF(self, Data, n=20):
        """ Chaikin Money Flow (CMF) is a technical analysis indicator used to measure Money Flow Volume
            CMF_Crossover
        Bullish Crosses occur when Chaikin Money Flow crosses from below the Zero Line to above the Zero Line. Price then rises.
        Bearish Crosses occur when Chaikin Money Flow crosses from above the Zero Line to below the Zero Line. Price then falls.
        We can adjust value of zero line to reduce false signals. (ex: 0.05 <--> -0.05 )
        """
        df = Data.copy()
        DataSet = self.Dataset
        df["multiplier"] = (2*df[DataSet] - df["High"] - df["Low"])/(df["High"] - df["Low"])
        df["MFV"] = df["multiplier"] * df["Volume"]
        df["CMF"] = df["MFV"].rolling(window = n).sum()/df["Volume"].rolling(window = n).sum()
        df["signal"] = np.where(df["CMF"] > 0.05, 1.0, 0.0)
        df["signal"] = df["signal"].diff()
        #print(df.tail(50))
        return df[[DataSet, "CMF", "signal"]]


    def Slope(self, series, span = 50):
        """Calculates the slope of regression line for n(span) consecutive points on a plot"""
        ser = (series - series.min())/(series.max() - series.min())
        x = np.array(range(len(ser)))
        x = (x - x.min())/(x.max() - x.min())
        slopes = [i*0 for i in range(span-1)]
        for i in range(span, len(ser)+1):
            y_scaled = ser[i-span:i]
            x_scaled = x[:span]
            x_scaled = sm.add_constant(x_scaled)
            model = sm.OLS(y_scaled, x_scaled)
            results = model.fit()
            slopes += [results.params[-1]]
        slope_angle = (np.rad2deg(np.arctan(np.array(slopes))))
        return np.array(slope_angle)


    def APO(self, Data, a = 20, b = 60, MA_type = "EMA"):
        """
        """
        df = Data.copy()
        DataSet = self.Dataset
        MA_fast = self.MovingAvg(df, n = a, MA_type = MA_type)
        MA_slow = self.MovingAvg(df, n = b, MA_type = MA_type)
        df["ma_fast"] = MA_fast[f"{MA_type}"]
        df["ma_slow"] = MA_slow[f"{MA_type}"]
        df["apo"] = df["ma_fast"] - df["ma_slow"]
        df["signal"] = 0.0 #WARNING should add
        return df[[DataSet, "ma_slow", "ma_fast", "apo"]]




    # ---------------------------------------------------------------------------- #







