from binance.helpers import round_step_size
from binance.client import Client
from binance.enums import *


from BINANCE_OBJ import CLOSE_POSITION, OPEN_POSITIONS, SIZE_2, FINISH_TRADE_VIEWS, CREATE_ORDER, CREATE_TP_AND_SL, GET_BALANCE
from GOOGLE_SHEET import GOOGLE_SHEET_DATAFRAME

from datetime import datetime, timedelta, date
import pandas as pd
import warnings
import time
import os
import sys

warnings.filterwarnings("ignore")











class LONG_TERM():

    def __init__(self, DF_LT, COIN, LEVERAGE,  TAKE_PROFIT, STOP_LOSS ,REFERENCE_DAYS, client, DONE_LT):
        self.client            = client
        self.COIN              = COIN
        self.LEVERAGE          = LEVERAGE
        self.TAKE_PROFIT       = TAKE_PROFIT
        self.STOP_LOSS         = STOP_LOSS
        self.REFERENCE_DAYS    = REFERENCE_DAYS
        self.DF_LT             = DF_LT
        self.DONE_LT           = DONE_LT

        self.DONE_LT           = self.LONG_TERM_STRATEGY()


    def LONG_TERM_STRATEGY(self):
        
        self.DF_LT = self.DF_LT[self.DF_LT['TIME_RELATIVE'] == (datetime.now().replace(second=0, microsecond=0))].reset_index()

        if len(self.DF_LT) > 0:
            for i in range(len(self.DF_LT)):
                if self.DF_LT.at[i, 'COMMENT'] == "LONG - EXIT" or self.DF_LT.at[i, 'COMMENT'] == "SHORT - EXIT":
                    OPEN_POS = OPEN_POSITIONS(self.client, self.COIN)

                    if len(OPEN_POS.POS_DF) != 0:
                        CLOSE_POSITION(self.client, self.COIN, OPEN_POS.QTY, OPEN_POS.DIRECTION_EXIST)
                        time.sleep(3)

                    if len(self.DF_LT) == 1:
                        GOOGLE_SHEET_DATA = GOOGLE_SHEET_DATAFRAME(self.COIN) 
                        self.DF_LT = GOOGLE_SHEET_DATA.DF_LT
                        self.DF_LT = self.DF_LT[self.DF_LT['TIME_RELATIVE'] == (datetime.now().replace(second=0, microsecond=0))].reset_index()
                        for i in range(len(self.DF_LT)):
                            if self.DF_LT.at[i, 'COMMENT'] == "LONG - EXIT" or self.DF_LT.at[i, 'COMMENT'] == "SHORT - EXIT":
                                self.DF_LT = self.DF_LT.drop(i)
                    else:
                        self.DF_LT = self.DF_LT.drop(i)
                

            self.DF_LT = self.DF_LT.reset_index()     

            if self.DF_LT.at[len(self.DF_LT)-1, 'DAY NUMBER'] in self.REFERENCE_DAYS:
                if self.DF_LT.at[len(self.DF_LT)-1, 'COMMENT'] != "LONG - EXIT TP" or self.DF_LT.at[len(self.DF_LT)-1, 'COMMENT'] != "SHORT - EXIT TP":                    
                    STEP_INFO               = SIZE_2(self.client, self.COIN)
                    CURRENT                 = GET_BALANCE(self.client)
                    TRADE_VALUE             = (CURRENT.BALANCE)* (1-(0.0008 * self.LEVERAGE))
                    BALANCE_TO_TRADE        = TRADE_VALUE * self.LEVERAGE 
                    PRICE                   = float(self.client.futures_symbol_ticker(symbol=self.COIN)['price'])
                    QTY                     = "{:0.0{}f}".format((BALANCE_TO_TRADE/PRICE), STEP_INFO.STEP_SIZE)
                    DIRECTION               = self.DF_LT.at[len(self.DF_LT)-1, 'POSITION']
                    
                    if DIRECTION != 'FLAT':
                        CREATE_ORDER(self.client, self.COIN, QTY, DIRECTION, self.LEVERAGE)
                        time.sleep(2)      
                        OPEN_POS = OPEN_POSITIONS(self.client, self.COIN)
                        CREATE_TP_AND_SL(self.client, self.COIN, OPEN_POS.ENTRY_PRICE, OPEN_POS.DIRECTION_EXIST, self.TAKE_PROFIT,  self.STOP_LOSS, STEP_INFO.TICK_SIZE, 'YES', 'YES')

                        self.DONE_LT = 'YES'

        return self.DONE_LT


