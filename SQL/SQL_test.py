import time
import sqlite3
import sqlalchemy
import pandas as pd
import yfinance as yf



engine = sqlalchemy.create_engine("sqlite:///ITCStream.db")

ticker = yf.Ticker("ITC.NS")
data = ticker.history(period = "60d", interval = "5m")
print(data)
data[["Open", "High", "Low", "Close", "Volume"]].copy().to_sql("ITC", engine, index = True, if_exists = "replace")

while True:
    new = ticker.history(period = "5m", interval = "5m")[["Open", "High", "Low", "Close", "Volume"]]
    new.drop(new.index[0], inplace=True)
    new.to_sql("ITC", engine, index = True, if_exists = "append")
    df = pd.read_sql("ITC", engine, index_col = "Datetime")
    print(df)
    time.sleep(300)
