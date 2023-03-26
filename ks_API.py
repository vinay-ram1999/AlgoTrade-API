import json
import urllib3
import requests
import pandas as pd
import datetime as dt
from ks_api_client import ks_api
from credentials.info import KSAPI_Credentials
from trading_platform import TradingPlatform
from ks_api_client.models.tsloplace import Tsloplace


class KSTrade_API(TradingPlatform):
    def __init__(self):
        #Initiate TradingPlatform class
        super(KSTrade_API, self).__init__()

        """
        try:
            with open("credentials.txt") as file:
                credentials = [line.rstrip() for line in file]      # Opens the credentials file, reads all the lines and strips off the \n at the end of the lines
        except Exception as ex:
            print("credentials not found:", ex)
            pass
        """

        credentials = KSAPI_Credentials()
        self.access_token = credentials.access_token
        self.userid = credentials.userid
        self.password = credentials.password
        self.consumer_key = credentials.consumer_key
        self.consumer_secret_key = credentials.consumer_secret_key
        self.ip_address = credentials.ip_address
        self.app_id = credentials.app_id
        self.scripmaster_url = "/scripmaster/1.1/filename"
        self.margin_url = "/margin/1.0/margin"
        self.watchlists_url = "/watchlist/2.1/watchlists"
        self.portfolio_url = "/portfolio/1.0/portfolio/holdings/all"
        self.session_2fa_url = "/session/1.0/session/2FA/oneTimeToken"
        #self.OTP = "3340"  # We can bypass this step by using oneTimeToken system
        return


    # SessionLogin
    def Session_init(self):
        urllib3.disable_warnings() # This disables the warnings that pop up on terminal
        # Defining the host is optional and defaults to https://sbx.kotaksecurities.com/apim
        # See configuration.py for a list of all supported configuration parameters.
        client = ks_api.KSTradeApi(access_token = self.access_token, userid = self.userid, consumer_key = self.consumer_key,ip = self.ip_address, app_id = self.app_id)
        # Initiate login and generate OTT
        client.login(password = self.password)
        #client.session_2fa(access_code = self.OTP)  # We can bypass this step by using oneTimeToken system

        # TwoFactorAuthentication
        header = {"accept ": "application/json", "oneTimeToken " : f"{client.one_time_token}", "consumerKey " : f"{client.consumer_key}", "ip " : f"{client.ip}",
                  "appId " : f"{client.app_id}", "Content-Type " : "application/json", "Authorization" : f"Bearer {client.access_token}"}
        data = '{"userid": "' + client.userid + '"}'
        link = client.host + self.session_2fa_url
        response = requests.post(url = link, headers = header, data = data).json()
        client.session_token = response["success"]["sessionToken"]
        print("Session initiated at", dt.datetime.now())
        return client


    @property
    def Client(self):
        if hasattr(self, "session_initiated"):
            return self.client
        else:
            client = self.Session_init()
            self.client = client
            self.session_initiated = True
            return self.client


    # WatchlistName
    def WatchlistName_req(self):
        client = self.Client
        header = {"accept ": "application/json", "userid " : f"{client.userid}", "consumerKey " : f"{client.consumer_key}", "sessionToken" : f"{client.session_token}",
                  "Authorization" : f"Bearer {client.access_token}"}
        link = client.host + self.watchlists_url
        response = requests.get(url = link, headers = header).json()
        lists = response["Success"]
        list_name = []
        for name in lists:
            list_name += [name["watchlistName"]]
        return list_name


    # WatchlistData
    def Watchlist_req(self, list_name):
        client = self.Client
        header = {"accept ": "application/json", "userid " : f"{client.userid}", "consumerKey " : f"{client.consumer_key}", "sessionToken" : f"{client.session_token}",
                  "Authorization" : f"Bearer {client.access_token}"}
        link = client.host + self.watchlists_url + "/byName/" + list_name
        response = requests.get(url = link, headers = header).json()
        symbols = response["Success"]
        print(json.dumps(symbols, indent = 2))
        return symbols


    # PortfolioHoldings
    def Portfolio_req(self):
        client = self.Client
        header = {"accept ": "application/json", "consumerKey " : f"{client.consumer_key}", "sessionToken" : f"{client.session_token}",
                  "Authorization" : f"Bearer {client.access_token}"}
        link = client.host + self.portfolio_url
        response = requests.get(url = link, headers = header).json()
        holdings = response["Success"]
        return holdings


    # Scripmaster
    def Scripmaster_req(self):
        client = self.Client
        header = {"accept ": "application/json", "consumerKey " : f"{client.consumer_key}", "Authorization" : f"Bearer {client.access_token}"}
        link = client.host + self.scripmaster_url
        response = requests.get(url = link, headers = header).json()
        #fno_url = response["Success"]["fno"]; fno_df = pd.read_csv(fno_url, sep="|")
        cash_url = response["Success"]["cash"]
        cash_df = pd.read_csv(cash_url, sep = "|")
        NSE_equity = cash_df[(cash_df.exchange == "NSE") & (cash_df.instrumentType == "EQ")]
        tokens = NSE_equity.instrumentToken
        names = NSE_equity.instrumentName
        assert len(names) == len(tokens)
        #ltp = NSE_equity.lastPrice
        data = {}
        for i in range(len(tokens)):
            data[names[i]] = tokens[i]
        return data


    # MarginAvailable
    @property
    def Margin_req(self):
        """
        header = {"accept ": "application/json", "consumerKey " : f"{client.consumer_key}", "sessionToken" : f"{client.session_token}",
                  "Authorization" : f"Bearer {client.access_token}"}
        link = client.host + self.margin_url
        response = requests.get(url = link, headers = header).json()
        currency = response["Success"]["currency"]
        derivatives = response["Success"]["derivatives"]

        Instead of this we can use client.margin() in order to get this data
        """
        client = self.Client
        margin = client.margin()
        equity = margin["Success"]["equity"][0]
        #print(dt.datetime.now())
        #print(json.dumps(equity, indent = 2))
        CashBalance = margin["Success"]["equity"][0]["cash"]["availableCashBalance"]
        return CashBalance


    def PlaceOrder(self, *args, **kwargs):
        client = self.Client
        try:
            Order = client.place_order(*args, **kwargs)
            return Order
        except Exception as ex:
            return ex


    def TStop_loss(self, spread = 2, trailingPrice = 0):
        client = self.Client
        model = Tsloplace(spread = spread, trailingPrice = trailingPrice)
        return model


    def Run(self, OrderType = "MIS", qty = 1, price = 0, StopLoss = True):
        TickerPosition = self.Get_TickerPosition
        Instrument_tokens = self.Scripmaster_req()
        margin = self.Margin_req
        for ticker in TickerPosition:
            Price = TickerPosition[ticker][1]
            if StopLoss:
                trigger_price = Price - 2.0
            else:
                trigger_price = 0
            Position = TickerPosition[ticker][0]
            if Position == "BUY":
                print("Buy", ticker, Instrument_tokens[ticker], " @ ", TickerPosition[ticker][1])
                #if Price <= (margin*4):
                    #try:
                        #order = self.PlaceOrder(order_type = OrderType, instrument_token = Instrument_tokens[ticker], transaction_type = "BUY", quantity = qty, price = price, disclosed_quantity = 0, trigger_price = trigger_price, tag = "", validity = "GFD", variety = "INTRADAY")
                        #print(order)
                    #except Exception as ex:
                        #print(ex)
            elif Position == "SELL":
                print("Sell", ticker, Instrument_tokens[ticker], " @ ", TickerPosition[ticker][1])
                #try:
                    #order = self.PlaceOrder(order_type = OrderType, instrument_token = Instrument_tokens[ticker], transaction_type = "SELL", quantity = qty, price = price, disclosed_quantity = 0, trigger_price = trigger_price, tag = "", validity = "GFD", variety = "INTRADAY")
                    #print(order)
                #except Exception as ex:
                        #print(ex)
            else:
                pass
        return



    # ---------------------------------------------------------------------------- #






