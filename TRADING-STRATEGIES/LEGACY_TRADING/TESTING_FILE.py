
from BINANCE_SCRIPTS import BALANCE, OPEN_POSITIONS, CREATE_ORDER, CREATE_TP_AND_SL, CLOSE_POSITION, SIZES, FINISH_TRADE_VIEWS, SIZE_2
from GOOGLE_SHEET_DATA import GOOGLE_SHEET_DATAFRAME
from DATA import HISTORICAL_DATA
from HOLD_TP import HTT_STRATEGY

from binance.helpers import round_step_size
from binance.client import Client
from binance.enums import *

from datetime import datetime, timedelta, date

import pandas as pd
import numpy as np
import warnings
import time
import os

warnings.filterwarnings("ignore")

api_key                 = 'wSWDRahsJKzs7ev4OqNsE03I3zNjOqKTriD57WUnIQJT5JDuZ7nZHMTh8bmkIRhb'
api_secret              = '8wyJh1oqU9sAnfe2votXvnS5Np7HpeYqn2j51zMwgzmM5fCUPVrFV9PcxvsI2LvL'
client                  = Client(api_key, api_secret)

COINS = ['XRPUSDT', 'BTCUSDT']

TP_CONDITIONS       = {"COIN"              : 'BTCUSDT',
                        "REQUIREMENTS_EMA"  : [2, 4],
                        "DURATION"          : 0,
                        "TIMEZONE"          : 0,
                        "LEVERAGE"          : 20,
                        "TAKE_PROFIT"       : 1,
                        }


PORTFOLIO_SUMMARY      = False
NEXT_DAY_FORECAST_HTTP = True


if PORTFOLIO_SUMMARY == True:
    for i in range(len(COINS)):
        

        COIN = COINS[i]
        LEVERAGE = 20


        STEP_SIZE, TICK_SIZE    = SIZE_2(client, COIN)
        TRADE_DF                = FINISH_TRADE_VIEWS(client, COIN)

        if TRADE_DF.at[len(TRADE_DF)-1, 'SIDE'] == "BUY": PREV_DIRECTION = -1
        else: PREV_DIRECTION = 1

        PROFIT                  = (TRADE_DF.at[len(TRADE_DF)-1, 'USDT_VALUE'] - TRADE_DF.at[len(TRADE_DF)-2, 'USDT_VALUE']) * PREV_DIRECTION
        START_AMOUNT            = TRADE_DF.at[len(TRADE_DF)-2, 'USDT_VALUE']/LEVERAGE

        COMMISION               = TRADE_DF.at[len(TRADE_DF)-1, 'COMMISSION']
        TRADE_VALUE             = START_AMOUNT + PROFIT - COMMISION
        BALANCE_TO_TRADE        = (TRADE_VALUE * LEVERAGE) * (1-((0.0004)))
        PRICE                   = float(client.futures_symbol_ticker(symbol=COIN)['price'])
        QTY                     = "{:0.0{}f}".format((BALANCE_TO_TRADE/PRICE), STEP_SIZE)
        
        print('    ')
        print('COIN OF REFERENCE           : ' + COIN)
        print('START AMOUNT LAST TRADE     : ' + str(START_AMOUNT))
        print('PROFIT OF LAST TRADE        : ' + str(PROFIT))
        print('COMMISSION OF LAST TRADE    : ' + str(COMMISION))
        print('TRADE VALUE OF NEXT TRADE   : ' + str(TRADE_VALUE))
        print('BALANCE TO TRADE WITH       : ' + str(BALANCE_TO_TRADE))
        print(' ')
        print('CURRENT PRICE OF COIN       : ' + str(PRICE))
        print('CURRENT QUANTITY TO TRADE   : ' + str(QTY))
        print(' ')
        print('TRADE HISTORY OF OUR COIN   :')
        print('    ')
        print(TRADE_DF)
        print('    ')
        print('    ')
        print('    ')
        print('    ')
        


if NEXT_DAY_FORECAST_HTTP == True:
    df_interval             = HISTORICAL_DATA(client, TP_CONDITIONS["COIN"], '1d', 30)
    df, DIRECTION_EXIST     = HTT_STRATEGY(df_interval, TP_CONDITIONS["DURATION"], TP_CONDITIONS["REQUIREMENTS_EMA"], TP_CONDITIONS["TIMEZONE"])
    
    print('DATAFRAME OF MOVEMENTS   :')
    print('    ')
    print(df)

    print('    ')  
    print('NEXT DAY MOVEMENT        : ' + DIRECTION_EXIST)
    print('    ')  
    print('    ')  
    print('    ')  
    print('    ')  
    
        