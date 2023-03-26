import pandas as pd
import vectorbt as vbt
from backtesting_vbt import BackTestingEngine


bte = BackTestingEngine()


tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'WMT', 'BAC', 'KO', 'DIS', 'PFE', 'FB', 'BABA', 'MA', 'V', 'TM', 'PEP', 'AMD', 'INTC', 'NKE', 'ORCL', 'ACN']

tickers += ["ITC.NS", "TRIDENT.NS", "BRITANNIA.NS", "MARUTI.NS", "MRF.NS", "ADANIPORTS.NS", "EICHERMOT.NS", "TITAN.NS", "TATAMOTORS.NS", "ONGC.NS", "NTPC.NS", "LT.NS", "TATASTEEL.NS", "WIPRO.NS", "SBIN.NS", "AXISBANK.NS", "ICICIBANK.NS", "BPCL.NS", "HDFCBANK.NS", "IOC.NS"]

#tickers = ['MSFT']


def load_financial_data(output_file, period, tickers):
    try:
        df = pd.read_pickle(output_file)
        print('File data found...')
    except FileNotFoundError:
        print('File data not found...downloading the data')
        df = vbt.YFData.download(tickers, missing_index='drop', interval="1D", period = period).get('Close')
        df.to_pickle(output_file)
    return df


def postprocess(data, Pf):
    values = {}
    for i in range(len(data.columns)):
        column_name = data.columns[i]
        stat = Pf.stats(column = i)
        values[column_name] = stat
    strat_res = Pf.stats(group_by = True)
    returns = Pf.total_return()
    #print(returns.to_string())
    total_values = Pf.stats(agg_func = None)
    print(strat_res)
    print(returns.max(), "--->", returns.idxmax())
    print(returns.min(), "--->", returns.idxmin())
    #print(total_values[["Start Value", "End Value", "Total Return [%]", "Sharpe Ratio", "Sortino Ratio"]].to_string())
    return total_values, values


def bt_Double_N(data, N, MA_span):
    dN = bte.vbt_Double_N
    res = dN.run(data, N = N, MA_span = MA_span)
    entries = res.signal == 1.0
    exits = res.signal == -1.0
    pf = vbt.Portfolio.from_signals(data, entries, exits, freq='d')
    total_values, values = postprocess(data, pf)
    return pf, values


def bt_nPeriod_RSI(data, N, MA_span, LL, UL):
    nRSI = bte.vbt_nPeriod_RSI
    res = nRSI.run(data, N = N, MA_span = MA_span, LL = LL, UL = UL)
    entries = res.signal == 1.0
    exits = res.signal == -1.0
    pf = vbt.Portfolio.from_signals(data, entries, exits, freq='d')
    total_values, values = postprocess(data, pf)
    return pf, values


def bt_Cumulative_RSI(data, X, Y, N, LL, UL, sl_stop):
    cRSI = bte.vbt_Cumulative_RSI
    res = cRSI.run(data, X = X, Y = Y, N = N, LL = LL, UL = UL)
    entries = res.signal == 1.0
    exits = res.signal == -1.0
    pf = vbt.Portfolio.from_signals(data, entries, exits, freq='d', sl_stop = sl_stop)
    total_values, values = postprocess(data, pf)
    return pf, values


def bt_HMA_Crossover(data, short_span, long_span):
    HMA = bte.vbt_HMA_Crossover
    res = HMA.run(data, short_span = short_span, long_span = long_span)
    entries = res.signal == 1.0
    exits = res.signal == -1.0
    pf = vbt.Portfolio.from_signals(data, entries, exits, freq='d')
    #total_values, values = postprocess(data, pf)
    values = None
    return pf, values




close_price = load_financial_data("BackTest_DATA/data.pkl", period = "20y", tickers = tickers)
dN_pf, dN_res = bt_Double_N(close_price, N = [5,6,7], MA_span = [100,200])
#nRSI_pf, nRSI_res = bt_nPeriod_RSI(close_price, N = [2,3,4], MA_span = [100,200], LL = [10,20,30], UL = [70,80,90])
#cRSI_pf, cRSI_res = bt_Cumulative_RSI(close_price, X = [2], Y = [4], N = [2], LL = [10], UL = [80], sl_stop = 0.01)
#HMA_pf, HMA_res = bt_HMA_Crossover(close_price, short_span = [10,20,30], long_span = [60,70,80])


#fig = HMA_pf.total_return().vbt.heatmap(x_level = "HMA_short_span", y_level = "HMA_long_span")
#fig.show()








