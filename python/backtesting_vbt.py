import numpy as np
import pandas as pd
import vectorbt as vbt
from pyti.hull_moving_average import hull_moving_average as hma
from pyti.weighted_moving_average import weighted_moving_average as wma



class BackTestingEngine():
    def __init__(self):
        self.long_dataset = "long"
        self.short_dataset = "short"
        return


    def Plot(self, pf, title):
        plt = pf.plot()
        plt.layout.title = title
        plt.show()
        return


    def CustomIndicator(self, Data, Dataset = "Close", plot = False, title = ""):
        entries = Data[self.long_dataset] == 1.0
        exits = Data[self.short_dataset] == 1.0
        pf = vbt.Portfolio.from_signals(Data[Dataset], entries, exits)
        if plot:
            self.Plot(pf, title)
        return pf


    def bt_Double_N(self, Dataset, N = 7, MA_span = 100):
        N_max = Dataset.rolling(window = N).max()
        N_min = Dataset.rolling(window = N).min()
        ma = Dataset.rolling(window = MA_span).mean()
        signal = np.where(Dataset == N_min, 1.0, 0.0)
        signal = np.where(Dataset < ma, -1.0, signal)
        return signal


    @property
    def vbt_Double_N(self):
        double_N = vbt.IndicatorFactory(
                    class_name = "Double_N",
                    short_name = "double_N",
                    input_names = ["Close"],
                    param_names = ["N", "MA_span"],
                    output_names = ["signal"]
                    ).from_apply_func(self.bt_Double_N, N = 7, MA_span = 100,
                                      keep_pd = True, param_product = True)
        return double_N


    def bt_nPeriod_RSI(self, Dataset, N = 2, MA_span = 100, LL = 30, UL = 70):
        rsi = vbt.RSI.run(Dataset, window = N, ewm = True)
        ma = Dataset.rolling(window = MA_span).mean()
        signal = np.where(rsi.rsi <= LL, 1.0, 0.0)
        signal = np.where(ma > Dataset, -1.0, signal)
        return signal


    @property
    def vbt_nPeriod_RSI(self):
        nPeriod_RSI = vbt.IndicatorFactory(
                    class_name = "nPeriod_RSI",
                    short_name = "nP_RSI",
                    input_names = ["Close"],
                    param_names = ["N", "MA_span", "LL", "UL"],
                    output_names = ["signal"]
                    ).from_apply_func(self.bt_nPeriod_RSI, N = 2, MA_span = 100, LL = 30, UL = 70, keep_pd = True, param_product = True)
        return nPeriod_RSI


    def bt_Cumulative_RSI(self, Dataset, X = 2, Y = 4, N = 2, LL = 10, UL = 90):
        rsi = vbt.RSI.run(Dataset, window = N, ewm = True)
        crsi = rsi.rsi.rolling(window = X).sum()
        signal = np.where((crsi <= Y*LL) | (rsi.rsi <= LL), 1.0, 0.0)
        signal = np.where((crsi >= UL) | (rsi.rsi >= UL), -1.0, signal)
        return signal


    @property
    def vbt_Cumulative_RSI(self):
        Cumulative_RSI = vbt.IndicatorFactory(
                    class_name = "Cumulative_RSI",
                    short_name = "CRSI",
                    input_names = ["Close"],
                    param_names = ["X", "Y", "N", "LL", "UL"],
                    output_names = ["signal"]
                    ).from_apply_func(self.bt_Cumulative_RSI, X = 2, Y = 4, N = 2, LL = 10, UL = 90, keep_pd = True, param_product = True)
        return Cumulative_RSI


    def bt_HMA_Crossover(self, Dataset, short_span = 20, long_span = 60):
        #print(Dataset);exit()
        if len(Dataset.columns) > 1:
            for i in range(len(Dataset.columns)):
                column_name = Dataset.columns[i]
                MA_slow = hma(Dataset[column_name], long_span)
                MA_fast = hma(Dataset[column_name], short_span)
                MA_slow = np.array(MA_slow)
                MA_fast = np.array(MA_fast)
                signal = np.where(MA_fast > MA_slow, 1.0, 0.0)
                signal = np.where(MA_fast < MA_slow, -1.0, signal)
                return signal
        else:
            MA_slow = hma(Dataset["Close"], long_span)
            MA_fast = hma(Dataset["Close"], short_span)
            MA_slow = np.array(MA_slow)
            MA_fast = np.array(MA_fast)
            signal = np.where(MA_fast > MA_slow, 1.0, 0.0)
            signal = np.where(MA_fast < MA_slow, -1.0, signal)
            return signal


    @property
    def vbt_HMA_Crossover(self):
        HMA_Crossover = vbt.IndicatorFactory(
                    class_name = "HMA_Crossover",
                    short_name = "HMA",
                    input_names = ["Close"],
                    param_names = ["short_span", "long_span"],
                    output_names = ["signal"]
                    ).from_apply_func(self.bt_HMA_Crossover, short_span = 20, long_span = 60, keep_pd = True, param_product = True)
        return HMA_Crossover









