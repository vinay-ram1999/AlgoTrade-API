import numpy as np
import pandas as pd
from technical_analysis import TechnicalAnalysis


class TradingStrategy(TechnicalAnalysis):
    def __init__(self):
        # initiate TechnicalAnalysis class
        super(TradingStrategy, self).__init__()
        return


    def MA_Crossover(self, Data, short_span = 20, long_span = 60, MA_type = "SMA", signal_type = "PMAC"):
        """
        MAC (Moving Avg Crossover)
        Bullish Crossover: Occurs when the short-term SMA crosses above the long-term SMA. Also known as Golden cross.
        Bearish Crossover: Occurs when the short-term SMA crosses below the long-term SMA. Also known as Dead cross.
        PMAC (Price and Moving Avg Crossover)
        Bullish Price Crossover: Price crosses above short-term SMA while the short-term SMA is above the long-term SMA.
        Bearish Price Crossover: Price crosses below short-term SMA while the short-term SMA is below the long-term SMA.
        """
        df = Data.copy()
        DataSet = self.Dataset
        Strat_Data = pd.DataFrame(index = df.index)
        MA_slow = self.MovingAvg(df, n = long_span, MA_type = MA_type)
        MA_fast = self.MovingAvg(df, n = short_span, MA_type = MA_type)
        Strat_Data[DataSet] = df[DataSet]
        Strat_Data["ma_slow"] = MA_slow[f"{MA_type}"]
        Strat_Data["ma_fast"] = MA_fast[f"{MA_type}"]

        #RSI = self.RSI(df, n = 2, UL = 90, LL = 10) # WARNING TEST
        #Strat_Data["rsi"] = RSI["rsi"]
        if signal_type == "MAC":
            Strat_Data["long"] = np.where(Strat_Data["ma_fast"] > Strat_Data["ma_slow"], 1.0, 0.0)
            Strat_Data["short"] = np.where(Strat_Data["ma_fast"] < Strat_Data["ma_slow"], 1.0, 0.0)
        elif signal_type == "PMAC":
            Strat_Data["long"] = np.where(Strat_Data[DataSet] > Strat_Data["ma_slow"], (np.where(Strat_Data["ma_fast"] > Strat_Data["ma_slow"], 1.0, 0.0)), 0.0)
            Strat_Data["short"] = np.where(Strat_Data[DataSet] < Strat_Data["ma_slow"], 1.0, 0.0)
        Strat_Data["long"] = Strat_Data["long"].diff()
        Strat_Data["short"] = Strat_Data["short"].diff()
        return Strat_Data


    def nPeriod_RSI(self, Data, span = 2, short_span = 5, long_span = 60, MA_type = "SMA"):
        """
        1. The price is above its 200-day moving average.
        2. The 2-period RSI of the price closes below 5.
        3. Buy the EQ on the close.
        4. Exit when the price closes above its 5-period moving average.
        """
        df = Data.copy()
        DataSet = self.Dataset
        Strat_Data = pd.DataFrame(index = df.index)
        RSI = self.RSI(df, n = span, UL = 90, LL = 10)
        MA_slow = self.MovingAvg(df, n = long_span, MA_type = MA_type)
        MA_fast = self.MovingAvg(df, n = short_span, MA_type = MA_type)
        Strat_Data[DataSet] = df[DataSet]
        Strat_Data["ma_slow"] = MA_slow[f"{MA_type}"]
        Strat_Data["ma_fast"] = MA_fast[f"{MA_type}"]
        Strat_Data["rsi"] = RSI["rsi"]
        Strat_Data["long"] = np.where(Strat_Data[DataSet] > Strat_Data["ma_slow"], (np.where(RSI["signal"] == "OS", 1.0, 0.0)), 0.0)
        Strat_Data["short"] = np.where(RSI["signal"] == "OB", 1.0, 0.0)
        Strat_Data["long"] = Strat_Data["long"].diff()
        Strat_Data["short"] = Strat_Data["short"].diff()
        return Strat_Data


    def Cumulative_RSI(self, Data, X = 2, Y = 40, span = 2, short_span = 5, long_span = 60, MA_type = "SMA"):
        """
        1. The security being used is above its 200-day moving average.
        2. Use a 2-Period RSI.
        3. Take the past X days of the 2-period RSI and add them up.
        4. Buy if the Cumulative RSI is below Y (I'll share with you results using different numbers for X and Y).
        5. Exit when the 2-period RSI closes above 65 (you can also exit using any of the exit strategies taught later in the Exits chapter).
        """
        df = Data.copy()
        DataSet = self.Dataset
        Strat_Data = pd.DataFrame(index = df.index)
        nRSI = self.nPeriod_RSI(df, span = span, short_span = short_span, long_span = long_span, MA_type = MA_type)
        Strat_Data[DataSet] = nRSI[DataSet]
        Strat_Data["ma_slow"] = nRSI["ma_slow"]
        Strat_Data["ma_fast"] = nRSI["ma_fast"]
        Strat_Data["rsi"] = nRSI["rsi"]
        Strat_Data["crsi"] = nRSI["rsi"].rolling(window = X).sum()
        Strat_Data["long"] = np.where(Strat_Data[DataSet] > Strat_Data["ma_slow"], (np.where(Strat_Data["crsi"] < Y, 1.0, 0.0)), 0.0)
        Strat_Data["short"] = np.where(Strat_Data["crsi"] > 60, 1.0, 0.0)
        Strat_Data["long"] = Strat_Data["long"].diff()
        Strat_Data["short"] = Strat_Data["short"].diff()
        return Strat_Data


    def Double_N(self, Data, N = 7, long_span = 60, MA_type = "SMA"):
        """
        1. The security is above its 200-day moving average
        2. If the security closes at a 7-day low, buy.
        3. If the security closes at a 7-day high, sell your long position.
        """
        df = Data.copy()
        DataSet = self.Dataset
        Strat_Data = pd.DataFrame(index = df.index)
        MA_slow = self.MovingAvg(df, n = long_span, MA_type = MA_type)
        Strat_Data[DataSet] = df[DataSet]
        Strat_Data["ma_slow"] = MA_slow[f"{MA_type}"]
        Strat_Data["N_max"] = Strat_Data[DataSet].rolling(window = N).max()
        Strat_Data["N_min"] = Strat_Data[DataSet].rolling(window = N).min()
        Strat_Data["long"] = np.where(Strat_Data[DataSet] > Strat_Data["ma_slow"], (np.where(Strat_Data[DataSet] == Strat_Data["N_min"], 1.0, 0.0)), 0.0)
        Strat_Data["short"] = np.where(Strat_Data[DataSet] == Strat_Data["N_max"], 1.0, 0.0)
        Strat_Data["long"] = Strat_Data["long"].diff()
        Strat_Data["short"] = Strat_Data["short"].diff()
        return Strat_Data


    def SupportResistance(self, Data, N = 10, Tolerance_pct = 20, Tolerance_limit = 3):
        """
        1. The level of support and resistance is calculated by taking the maximum and minimum price and then subtracting and adding a 20% margin (Tolerance_pct).
        2. We will buy when we reach the support line, and sell when we reach the resistance line.
        """
        df = Data.copy()
        DataSet = self.Dataset
        Strat_Data = pd.DataFrame(index = df.index)
        Strat_Data[DataSet] = df[DataSet]
        Strat_Data["sup"] = Strat_Data[DataSet].rolling(window = N).min()
        Strat_Data["res"] = Strat_Data[DataSet].rolling(window = N).max()
        Strat_Data["sup_tolerance"] = Strat_Data["sup"] + (Tolerance_pct/100)*(abs(Strat_Data["sup"] - Strat_Data["res"]))
        Strat_Data["res_tolerance"] = Strat_Data["res"] - (Tolerance_pct/100)*(abs(Strat_Data["sup"] - Strat_Data["res"]))
        Strat_Data["in_resistance"] = np.where(Strat_Data[DataSet] >= Strat_Data["res_tolerance"], (np.where(Strat_Data[DataSet] <= Strat_Data["res"], 1.0, 0.0)), 0.0)
        Strat_Data["in_support"] = np.where(Strat_Data[DataSet] <= Strat_Data["sup_tolerance"], (np.where(Strat_Data[DataSet] >= Strat_Data["sup"], 1.0, 0.0)), 0.0)
        Strat_Data["sup_count"] = Strat_Data["in_support"].rolling(window = Tolerance_limit).sum()
        Strat_Data["res_count"] = Strat_Data["in_resistance"].rolling(window = Tolerance_limit).sum()
        Strat_Data["long"] = np.where(Strat_Data["sup_count"] == Tolerance_limit, 1.0, 0.0)
        Strat_Data["short"] = np.where(Strat_Data["res_count"] == Tolerance_limit, 1.0, 0.0)
        Strat_Data["long"] = Strat_Data["long"].diff()
        Strat_Data["short"] = Strat_Data["short"].diff()
        return Strat_Data


    def MeanReversion(self, Data, N = 20, short_span = 20, long_span = 60, threshold = 10, MA_type = "EMA"):
        """
        1. The APO trading signal value is above Sell-Entry threshold and the difference between last trade-price and current-price is different enough.
        2. We are long( +ve position ) and either APO trading signal value is at or above 0 or current position is profitable enough to lock profit.
        3. The APO trading signal value is below Buy-Entry threshold and the difference between last trade-price and current-price is different enough.
        4. We are short( -ve position ) and either APO trading signal value is at or below 0 or current position is profitable enough to lock profit.
        """
        df = Data.copy()
        DataSet = self.Dataset
        Strat_Data = pd.DataFrame(index = df.index)
        apo = self.APO(df, a = short_span, b = long_span, MA_type = MA_type)
        Strat_Data[DataSet] = df[DataSet]
        Strat_Data["apo"] = apo["apo"]
        Strat_Data["std"] = Strat_Data[DataSet].rolling(window = N).std(ddof=0)
        Strat_Data["std_factor"] = Strat_Data["std"]/Strat_Data["std"].rolling(window = N).mean()
        Strat_Data["long"] = np.where(Strat_Data["apo"] < (-threshold), 1.0, 0.0) # WARNING doubt
        Strat_Data["short"] = np.where(Strat_Data["apo"] > threshold, 1.0, 0.0) # WARNING doubt
        Strat_Data["long"] = Strat_Data["long"].diff()
        Strat_Data["short"] = Strat_Data["short"].diff()
        return Strat_Data






