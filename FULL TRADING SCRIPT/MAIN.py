
from BINANCE_SCRIPTS import BALANCE, OPEN_POSITIONS, CREATE_ORDER, CREATE_TP_AND_SL, CLOSE_POSITION, SIZES, FINISH_TRADE_VIEWS, SIZE_2
from GOOGLE_SHEET_DATA import GOOGLE_SHEET_DATAFRAME
from DATA import HISTORICAL_DATA
from HOLD_TP import HTT_STRATEGY


from binance.helpers import round_step_size
from binance.client import Client
from binance.enums import *


from datetime import datetime, timedelta, date
from pytimedinput import timedInput
import pandas as pd
import numpy as np
import warnings
import time
import os

warnings.filterwarnings("ignore")

api_key                 = 'wSWDRahsJKzs7ev4OqNsE03I3zNjOqKTriD57WUnIQJT5JDuZ7nZHMTh8bmkIRhb'
api_secret              = '8wyJh1oqU9sAnfe2votXvnS5Np7HpeYqn2j51zMwgzmM5fCUPVrFV9PcxvsI2LvL'
client                  = Client(api_key, api_secret)




#################################################################################################################
#------------------------------------------- FUNCTIONS FOR STRATEGY --------------------------------------------#
#################################################################################################################



def HOLD_TILL_TP_STRATEGY(COIN,  LEVERAGE, TAKE_PROFIT, client, DIRECTION_CHOSEN, DONE):

    POS_DF, ENTRY_PRICE, DIRECTION_EXIST, QTY = OPEN_POSITIONS(client, COIN)

    if len(POS_DF) != 1:

        print('\n-- HOLD UNTIL TP --')
        
        DIRECTION_EXIST         = DIRECTION_CHOSEN
        STEP_SIZE, TICK_SIZE    = SIZE_2(client, COIN)
        TRADE_DF                = FINISH_TRADE_VIEWS(client, COIN)

        if TRADE_DF.at[len(TRADE_DF)-1, 'SIDE'] == "BUY": PREV_DIRECTION = -1
        else: PREV_DIRECTION = 1

        PROFIT                  = ((TRADE_DF.at[len(TRADE_DF)-1, 'USDT_VALUE'] - TRADE_DF.at[len(TRADE_DF)-2, 'USDT_VALUE']) * PREV_DIRECTION)/2
        START_AMOUNT            = TRADE_DF.at[len(TRADE_DF)-2, 'USDT_VALUE']/LEVERAGE

        COMMISION               = TRADE_DF.at[len(TRADE_DF)-1, 'COMMISSION']
        TRADE_VALUE             = START_AMOUNT + PROFIT - COMMISION
        BALANCE_TO_TRADE        = (TRADE_VALUE * LEVERAGE) * (1-((0.0004)))
        PRICE                   = float(client.futures_symbol_ticker(symbol=COIN)['price'])
        QTY                     = "{:0.0{}f}".format((BALANCE_TO_TRADE/PRICE), STEP_SIZE)

        #if DIRECTION_EXIST != "NA":
            #CREATE_ORDER(client, COIN, QTY, DIRECTION_EXIST, LEVERAGE)
            #time.sleep(2)
            #POS_DF, ENTRY_PRICE, DIRECTION_EXIST, QTY = OPEN_POSITIONS(client, COIN)
            
            #print('ENTRY_PRICE       : ' + str(ENTRY_PRICE))

            #CREATE_TP_AND_SL(client, COIN, ENTRY_PRICE, DIRECTION_EXIST, TAKE_PROFIT, 0, TICK_SIZE, 'YES', 'NO')


    DONE = 'YES'
    
    return DONE


def LONG_TERM_STRATEGY(DF_LT, COIN, LEVERAGE,  TAKE_PROFIT, REFERENCE_DAYS, client, DONE):

    DF_LT = DF_LT[DF_LT['TIME_RELATIVE'] == (datetime.now().replace(second=0, microsecond=0))].reset_index()

    if len(DF_LT) > 0:
        if DF_LT.at[len(DF_LT)-1, 'DAY NUMBER'] in REFERENCE_DAYS:
            for i in range(len(DF_LT)):
                if DF_LT.at[i, 'COMMENT'] == "LONG - EXIT" or DF_LT.at[i, 'COMMENT'] == "SHORT - EXIT":
                    DF_LT = DF_LT.drop(i)

            DF_LT = DF_LT.reset_index()        

            if DF_LT.at[len(DF_LT)-1, 'COMMENT'] != "LONG - EXIT TP" or DF_LT.at[len(DF_LT)-1, 'COMMENT'] != "SHORT - EXIT TP":
                
                print('')
                print(DF_LT)
                print(' ')
                
                POS_DF, ENTRY_PRICE, DIRECTION_EXIST, QTY = OPEN_POSITIONS(client, COIN)

                print('\n-- LONG TERM STRATEGY --')

                if len(POS_DF) != 0:
                    CLOSE_POSITION(client, COIN, QTY, DIRECTION_EXIST)

                STEP_SIZE, TICK_SIZE    = SIZE_2(client, COIN)
                TRADE_DF                = FINISH_TRADE_VIEWS(client, COIN)

                if TRADE_DF.at[len(TRADE_DF)-1, 'SIDE'] == "BUY": PREV_DIRECTION = -1
                else: PREV_DIRECTION = 1

                PROFIT                  = ((TRADE_DF.at[len(TRADE_DF)-1, 'USDT_VALUE'] - TRADE_DF.at[len(TRADE_DF)-2, 'USDT_VALUE']) * PREV_DIRECTION)/2
                START_AMOUNT            = TRADE_DF.at[len(TRADE_DF)-2, 'USDT_VALUE']/LEVERAGE

                COMMISION               = TRADE_DF.at[len(TRADE_DF)-1, 'COMMISSION']
                TRADE_VALUE             = START_AMOUNT + PROFIT - COMMISION
                BALANCE_TO_TRADE        = (TRADE_VALUE * LEVERAGE) * (1-((0.0004)))
                PRICE                   = float(client.futures_symbol_ticker(symbol=COIN)['price'])
                QTY                     = "{:0.0{}f}".format((BALANCE_TO_TRADE/PRICE), STEP_SIZE)
                DIRECTION               = DF_LT.at[len(DF_LT)-1, 'POSITION']

                if DIRECTION != 'FLAT':
                    CREATE_ORDER(client, COIN, QTY, DIRECTION, LEVERAGE)
                    time.sleep(2)
                    POS_DF, ENTRY_PRICE, DIRECTION_EXIST, QTY = OPEN_POSITIONS(client, COIN)       
                    
                    print('ENTRY_PRICE       : ' + str(ENTRY_PRICE))
                                 
                    CREATE_TP_AND_SL(client, COIN, ENTRY_PRICE, DIRECTION_EXIST, TAKE_PROFIT, 0, TICK_SIZE, 'YES', 'NO')

                    DONE = 'YES'


    return DONE


def ENTER_PARAMETER(DURATION, REQUIREMENTS_EMA, TIMEZONE_OPTION, COIN, client, INTERVAL, PERIOD):
    DF_INTERVAL_TEMP             = HISTORICAL_DATA(client, COIN, INTERVAL, PERIOD)
    DF_TEMP, DIRECTION_EXIST_1     = HTT_STRATEGY(DF_INTERVAL_TEMP, DURATION, REQUIREMENTS_EMA, TIMEZONE_OPTION)

    print('\nDATAFRAME OF DATA : \n')
    print(DF_TEMP)
    print('\nDIRECTION PROPOSED BY STRATEGY : ' + DIRECTION_EXIST_1 + '\n')

    userText, timedOut = timedInput("PLEASE ENTER THE DIRECTION (LONG / SHORT) YOU WOULD LIKE : ", timeout=1800)
    DONE_COMMENT       = 'YES'

    if(timedOut): DIRECTION_CHOSEN = DIRECTION_EXIST_1
    else: DIRECTION_CHOSEN = userText

    return DIRECTION_CHOSEN 



#################################################################################################################
#--------------------------------------------- FINAL STAGE PROCESS ---------------------------------------------#
#################################################################################################################




def run_app(client):

    HOUR_CONDITIONS     = {"COIN"              : 'XRPUSDT',
                           "REFERENCE_DAYS"    : [0, 4, 5, 6],
                           "LEVERAGE"          : 20,
                           "TAKE_PROFIT"       : 0.5,
                          }
    
    TP_CONDITIONS       = {"COIN"              : 'BTCUSDT',
                           "REQUIREMENTS_EMA"  : [2, 4],
                           "DURATION"          : 0,
                           "TIMEZONE"          : 0,
                           "LEVERAGE"          : 10,
                           "TAKE_PROFIT"       : 0.5,
                          }

    ALLOW                                                   = 0
    while ALLOW                                             == 0:
        if datetime.now() >= (datetime.now().replace(minute=0, second=0, microsecond=1)) and datetime.now() <= (datetime.now().replace(minute=0, second=4, microsecond=0)):
            DONE_LT, DONE_TP, DONE_FULL          = 'NO', 'NO', 'NO'

            while DONE_FULL == 'NO':
                while DONE_TP == 'NO':
                    if datetime.now() >= (datetime.now().replace(hour=1, minute=0, second=0, microsecond=1)) and datetime.now() <= (datetime.now().replace(hour=1, minute=0, second=4, microsecond=0)):
                        DONE_TP = HOLD_TILL_TP_STRATEGY(TP_CONDITIONS["COIN"],
                                                        TP_CONDITIONS["LEVERAGE"], 
                                                        TP_CONDITIONS["TAKE_PROFIT"],
                                                        client, 
                                                        'LONG',
                                                        DONE_TP)
                    else:
                        DONE_TP = 'YES'


                while DONE_LT == 'NO':
                    if datetime.now() >= (datetime.now().replace(minute=0, second=0, microsecond=0)) and datetime.now() <= (datetime.now().replace(minute=0, second=59, microsecond=0)):
                        DF_ST, DF_LT, DF  = GOOGLE_SHEET_DATAFRAME()
                        DONE_LT           = LONG_TERM_STRATEGY(DF_LT, 
                                                               HOUR_CONDITIONS["COIN"], 
                                                               HOUR_CONDITIONS["LEVERAGE"], 
                                                               HOUR_CONDITIONS["TAKE_PROFIT"], 
                                                               HOUR_CONDITIONS["REFERENCE_DAYS"], 
                                                               client, 
                                                               DONE_LT)
                    
                    else:
                        DONE_LT = 'YES'

                if DONE_LT == 'YES' and  DONE_TP == 'YES':
                    DONE_FULL = 'YES'

        else:
            time.sleep(3)




        





if __name__ == '__main__':

    run_app(client)
    





#################################################################################################################
#---------------------------------------------------------------------------------------------------------------#
#################################################################################################################


