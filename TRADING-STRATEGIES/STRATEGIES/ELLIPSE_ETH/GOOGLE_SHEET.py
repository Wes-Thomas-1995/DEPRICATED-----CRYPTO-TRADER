
#!/usr/local/bin/python3
from datetime import datetime  
import pytz  
from time import strftime
from datetime import time
import pandas as pd
import warnings
import os

warnings.filterwarnings("ignore")




class GOOGLE_SHEET_DATAFRAME():

    def __init__(self, ticker):
        self.ticker = ticker
        self.DF_GS_BASIC = self.TRIAL_GOOGLE_SHEET()
        self.DF_ST, self.DF_LT, self.DF_GS, = self.DATAFRAME_PROCESSING()


    def TRIAL_GOOGLE_SHEET(self):

        try:
            DF_GS_BASIC = pd.read_csv(f'https://docs.google.com/spreadsheets/d/1hUtzAU124UtOAABs8TZ7r1JIa_RGso_l331wFgxcibA/gviz/tq?tqx=out:csv&sheet=Sheet1')
        except:
            try:
                DF_GS_BASIC = pd.read_csv(f'https://docs.google.com/spreadsheets/d/1hUtzAU124UtOAABs8TZ7r1JIa_RGso_l331wFgxcibA/gviz/tq?tqx=out:csv&sheet=Sheet1')
            except:
                DF_GS_BASIC = pd.DataFrame(columns=['TIME_ACTION','INTERVAL','TICKER','POSITION','COMMENT','PRICE','TIME_RELATIVE','ZAP_TIME'])
            
        return DF_GS_BASIC


    def DATAFRAME_PROCESSING(self):

        df = self.DF_GS_BASIC

        dt1     = datetime.strptime((str((datetime.now()).strftime("%Y-%m-%d %H:%M:%S"))), "%Y-%m-%d %H:%M:%S")
        dt2     = datetime.strptime((str((datetime.now(pytz.utc)).strftime("%Y-%m-%d %H:%M:%S"))), "%Y-%m-%d %H:%M:%S")
        delta   = int(((dt1 - dt2).total_seconds())/3600)

        if len(df)>0:

            df['COMMENT']          = df['COMMENT'].str.upper()
            df['POSITION']         = df['POSITION'].str.upper()
            df['TIME_ACTION']      = pd.to_datetime(df['TIME_ACTION'], format='%Y-%m-%d %H:%M:%S') + pd.DateOffset(hours=delta)
            df['TIME_RELATIVE']    = pd.to_datetime(df['TIME_RELATIVE'], format='%Y-%m-%d %H:%M:%S') + pd.DateOffset(hours=delta)
            df['ZAP_TIME']         = pd.to_datetime(df['ZAP_TIME'], format='%Y-%m-%d %H:%M:%S') + pd.DateOffset(hours=delta)
            df['DAY OF WEEK']      = df['TIME_ACTION'].dt.day_name()
            df['DAY NUMBER']       = df['TIME_ACTION'].dt.day_of_week
            df['TIME']             = df['TIME_ACTION'].dt.time
            df                     = df[['TIME_ACTION', 'INTERVAL', 'TICKER', 'POSITION', 'COMMENT', 'PRICE', 'TIME_RELATIVE', 'ZAP_TIME', 'DAY OF WEEK', 'DAY NUMBER', 'TIME']]
            DF_ST                  = df
            DF_LT                  = (df[df['INTERVAL'] == 240]).reset_index().iloc[:, 1:]

        else:
            DF_LT = df
            DF_ST = df

        return DF_ST, DF_LT, df