import vectorbt as vbt
import numpy as np

btc_price_1d = vbt.YFData.download("BTC-USD", missing_index='drop', interval="1D").get('Close')


class MA():
    def __init__(self):
        return

    def ma_strategy(self,close, window = 730, lower_multiplier=1, upper_multiplier=4):
        signal = np.full(close.shape, np.nan)
        for x in range(len(close)):
            if x >= window:
                mavg = np.mean( close[x-window:x])
                if close[x] < mavg*lower_multiplier:
                    signal[x] = 1
                elif close[x] > mavg*upper_multiplier:
                    signal[x] = -1
                else:
                    signal[x] = 0

        return signal

ma = MA()

my_indicator = vbt.IndicatorFactory(
         class_name="ma_strategy",
         short_name="ma",
         input_names=["close"],
         param_names=["window","lower_multiplier","upper_multiplier"],
         output_names=["signal"]
         ).from_apply_func(
             ma.ma_strategy,
             window=730,
             lower_multiplier=1,
             upper_multiplier=4
         )

results = my_indicator.run(btc_price_1d)
print(results.signal)
