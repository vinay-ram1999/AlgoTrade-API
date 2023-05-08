import pandas as pd
import yfinance as yf
from LSTM import LSTM_DL
import matplotlib.pyplot as plt


ticker = yf.Ticker("MRF.NS")
data = ticker.history(start = "2022-04-01", end = "2022-05-25", interval = "5m")
#print(data)


lstm = LSTM_DL("MRF", data, time_step = 75, epochs=100)
model = lstm.RNN
a = lstm.Prediction(model, 75)


daterange = pd.date_range(start ='2022-05-25 09:15', freq ='5min', periods = 75, tz ='Asia/Calcutta')
new = pd.DataFrame({"Pred_Close" : a}, index = pd.DatetimeIndex(daterange))



print(data)
print(new)

plt.plot(data["Close"], label="closing")
plt.plot(new["Pred_Close"], label="nextday_prediction")
plt.legend()
plt.show()



