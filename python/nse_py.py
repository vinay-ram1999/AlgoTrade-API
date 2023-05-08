import pandas as pd
from nsepy import get_history
from nsepy.symbols import get_symbol_list
from nsepy.symbols import get_index_constituents_list
from datetime import date


sbin = get_history(symbol='SBIN', start=date(2015,1,1), end=date(2015,1,10))
print(sbin)


NSE_INDICES = ["NIFTY 50","NIFTY NEXT 50","NIFTY100 LIQ 15","NIFTY 100","NIFTY 200","NIFTY 500","NIFTY MIDCAP 50","NIFTY MIDCAP 100","NIFTY SMALL 100","NIFTY AUTO","NIFTY BANK","NIFTY ENERGY","NIFTY FIN SERVICE","NIFTY FMCG","NIFTY IT","NIFTY MEDIA","NIFTY METAL","NIFTY PHARMA","NIFTY PSU BANK","NIFTY REALTY","NIFTY COMMODITIES","NIFTY CONSUMPTION","NIFTY CPSE","NIFTY INFRA","NIFTY MNC","NIFTY PSE","NIFTY SERV SECTOR","NIFTY SHARIAH 25","NIFTY50 SHARIAH","NIFTY500 SHARIAH","NIFTY100 EQUAL WEIGHT","NIFTY50 USD","NIFTY50 DIV POINT","NIFTY DIV OPPS 50","NIFTY ALPHA 50","NIFTY HIGH BETA 50","NIFTY LOW VOLATILITY 50","NIFTY QUALITY 30","NIFTY50 VALUE 20","NIFTY GROWSECT 15","NIFTY50 TR 2X LEV","NIFTY50 TR 1X INV"]


symbol_list = get_symbol_list()
#print(symbol_list)

nifty50 = get_index_constituents_list(index="NIFTY50")["Symbol"].to_list()
nifty100 = get_index_constituents_list(index="NIFTY100")["Symbol"].to_list()
nifty500 = get_index_constituents_list(index="NIFTY500")["Symbol"].to_list()


path = "~/Downloads/"

n_50 = pd.read_csv(path + "NIFTY-50.csv")
#n_50.drop(n_50.index[0], axis = 0, inplace=True)
syms_50_nse = n_50["SYMBOL \n"].to_list()

n_100 = pd.read_csv(path + "NIFTY-100.csv")
#n_100.drop(n_100.index[0], axis = 0, inplace=True)
syms_100_nse = n_100["SYMBOL \n"].to_list()


n_500 = pd.read_csv(path + "NIFTY-500.csv")
#n_500.drop(n_500.index[0], axis = 0, inplace=True)
syms_500_nse = n_500["SYMBOL \n"].to_list()





for sym in syms_50_nse:
    if sym in nifty50:
        pass
    else:
        print(sym, "is not there in NSEpy")


for sym in syms_100_nse:
    if sym in nifty100:
        pass
    else:
        print(sym, "is not there in NSEpy")


for sym in syms_500_nse:
    if sym in nifty500:
        pass
    else:
        print(sym, "is not there in NSEpy")









