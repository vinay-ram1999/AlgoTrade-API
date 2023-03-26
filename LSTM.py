import os
import numpy as np
import pandas as pd
import tensorflow as tf
from collections import deque
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM
from sklearn.model_selection import train_test_split
from tensorflow.keras.callbacks import ModelCheckpoint


class LSTM_DL(object):
    def __init__(self, Ticker, Data, Dataset = "Close", delta = 0.9, time_step = 30, epochs = 100):
        self.Data = Data
        self.delta = delta  # training percent
        self.Ticker = Ticker
        self.epochs = epochs
        self.time_step = time_step  # lookback period
        self.Dataset = Data.filter([Dataset]).values
        self.callback_path = "./LSTM_checkpoint/" + Ticker + ".ckpt"
        return


    @property
    def ScaleData(self):
        if hasattr(self, "data_is_scaled"):
            return self.ScaledData
        else:
            self.scaler = MinMaxScaler(feature_range=(0,1))
            scaled_data = self.scaler.fit_transform(self.Dataset)
            self.ScaledData = scaled_data
            self.data_is_scaled = True
            return self.ScaledData


    def InverseTransform(self, Dataset):
        transformed = self.scaler.inverse_transform(Dataset)
        return transformed


    @property
    def Split_XY(self):
        X = []; Y = []
        time_step = self.time_step
        scaled_data = self.ScaleData
        for i in range(time_step, len(scaled_data)):
            X.append(scaled_data[i-time_step:i,0])
            Y.append(scaled_data[i,0])
        return X, Y


    def Split_train_test(self):
        if hasattr(self, "data_is_split"):
            return x_train, x_test, y_train, y_test
        else:
            self.X, self.Y = self.Split_XY
            x_train, x_test, y_train, y_test = train_test_split(self.X, self.Y, train_size = self.delta, shuffle = False)
            x_train = np.array(x_train)
            x_test = np.array(x_train)
            y_train = np.array(x_train)
            y_test = np.array(x_train)
            return x_train, x_test, y_train, y_test


    @property
    def RNN(self):
        self.x_train, self.x_test, self.y_train, self.y_test = self.Split_train_test()
        model = Sequential()
        model.add(LSTM(50, return_sequences = True, input_shape = (self.time_step, 1)))
        model.add(LSTM(50, return_sequences = False))
        model.add(Dense(25))
        model.add(Dense(1))
        model.compile(optimizer = "adam", loss = "mean_squared_error", metrics = ["accuracy"])
        if hasattr(self, "_modeled") or (self.Ticker + ".ckpt.index") in os.listdir("./LSTM_checkpoint/"):
            #latest_cp = tf.train.latest_checkpoint(self.callback_path)
            model.load_weights(self.callback_path)
        else:
            model.fit(self.x_train, self.y_train, batch_size = 1, epochs = self.epochs, validation_data = (self.x_test, self.y_test), callbacks = [self.Callback])
            _modeled = True
        print(model.summary())
        loss, acc = model.evaluate(self.x_test, self.y_test, verbose=2)
        print("Restored model, accuracy: {:5.2f}%".format(100 * acc))
        return model


    @property
    def Callback(self):
        callback = ModelCheckpoint(filepath = self.callback_path, save_weights_only = True, verbose = 1)
        return callback


    def Prediction(self, model, N):
        pred_data = []
        historic_data = deque(self.ScaleData[-self.time_step:,:], maxlen = self.time_step)
        for i in range(N):
            x_data = []
            x_data.append(list(historic_data))
            x_data = np.array(x_data)
            x_data = np.reshape(x_data, (x_data.shape[0], x_data.shape[1], 1))
            pred_value = model.predict(x_data)
            historic_data.append(np.array(pred_value[0]))
            pred_data.append(pred_value[0])
        pred_prices = self.InverseTransform(np.array(pred_data))
        return pred_prices[:,0].tolist()



