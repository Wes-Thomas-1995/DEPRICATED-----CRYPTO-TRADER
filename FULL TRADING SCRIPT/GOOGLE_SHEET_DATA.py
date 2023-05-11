from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build

from datetime import datetime
from datetime import time
import pandas as pd
import warnings
import os.path
import os

warnings.filterwarnings("ignore")





def TRIAL_GOOGLE_SHEET():
    try:
        SHEET_ID = '16Oggq_lwENhBtw-WncemxoSIyfYE_YZvUT06bghDXMQ'
        SHEET_NAME = 'Sheet1'
        url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}'
        DF_GS = pd.read_csv(url)
    except:
        try:
            SHEET_ID = '16Oggq_lwENhBtw-WncemxoSIyfYE_YZvUT06bghDXMQ'
            SHEET_NAME = 'Sheet1'
            url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}'
            DF_GS = pd.read_csv(url)
        except:
            DF_GS = pd.DataFrame(columns=['TIME_ACTION','INTERVAL','TICKER','POSITION','COMMENT','PRICE','TIME_RELATIVE','ZAP_TIME'])
        
    
    return DF_GS




def DATAFRAME_PROCESSING(df):

    if len(df)>0:

        COMMENT_LIST           = []
        df['COMMENT']          = df['COMMENT'].str.upper()
        df['POSITION']         = df['POSITION'].str.upper()
        df['TIME_ACTION']      = pd.to_datetime(df['TIME_ACTION'], format='%Y-%m-%d %H:%M:%S') + pd.DateOffset(hours=1)
        df['TIME_RELATIVE']    = pd.to_datetime(df['TIME_RELATIVE'], format='%Y-%m-%d %H:%M:%S') + pd.DateOffset(hours=1)
        df['ZAP_TIME']         = pd.to_datetime(df['ZAP_TIME'], format='%Y-%m-%d %H:%M:%S') + pd.DateOffset(hours=1)
        df['DAY OF WEEK']     = df['TIME_ACTION'].dt.day_name()
        df['DAY NUMBER']      = df['TIME_ACTION'].dt.day_of_week
        df['TIME']            = df['TIME_ACTION'].dt.time

        df                     = df[['TIME_ACTION', 'INTERVAL', 'TICKER', 'POSITION', 'COMMENT', 'PRICE', 'TIME_RELATIVE', 'ZAP_TIME', 'DAY OF WEEK', 'DAY NUMBER', 'TIME']]
        
        for i in range(len(df)):   

                if df.at[i, 'COMMENT'] == "EXIT LONG PROFIT":
                    COMMENT = "LONG - EXIT TP"

                elif df.at[i, 'COMMENT'] == "EXIT SHORT PROFIT":
                    COMMENT = "SHORT - EXIT TP"

                elif df.at[i, 'COMMENT'] == "ENTER SHORT":
                    COMMENT = "SHORT - ENTRY"

                elif df.at[i, 'COMMENT'] == "ENTER LONG":
                    COMMENT = "LONG - ENTRY"

                elif df.at[i, 'COMMENT'] == "EXIT LONG LOSS":
                    COMMENT = "LONG - EXIT SL"

                elif df.at[i, 'COMMENT'] == "CLOSE ENTRY(B) ORDER ENTER SHORT":
                    COMMENT = "SHORT - EXIT"

                elif df.at[i, 'COMMENT'] == "CLOSE ENTRY(S) ORDER ENTER LONG":
                    COMMENT = "LONG - EXIT"

                elif df.at[i, 'COMMENT'] == "EXIT SHORT LOSS":
                    COMMENT = "SHORT - EXIT SL"
                    
                else:
                    COMMENT = "------"            

                COMMENT_LIST.append(COMMENT)
                
        df['COMMENT']               = COMMENT_LIST
        DF_ST                       = (df[df['INTERVAL'] == 15]).reset_index().iloc[:, 1:]
        DF_LT                       = (df[df['INTERVAL'] == 60]).reset_index().iloc[:, 1:]

    else:
        DF_LT = df
        DF_ST = df

    return DF_ST, DF_LT, df


def GOOGLE_SHEET_DATAFRAME():
    
    DF_GS               = TRIAL_GOOGLE_SHEET()
    DF_ST, DF_LT, DF    = DATAFRAME_PROCESSING(DF_GS)

    return DF_ST, DF_LT, DF

