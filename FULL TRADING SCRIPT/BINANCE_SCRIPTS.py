from binance.helpers import round_step_size
from binance.client import Client
from binance.enums import *
import time

from datetime import datetime
import pandas as pd
import numpy as np
import warnings

warnings.filterwarnings("ignore")






def BALANCE(client):
    acc_balance = client.futures_account_balance()

    for check_balance in acc_balance:
            if check_balance["asset"] == "USDT":
                usdt_balance = round(float(check_balance["balance"]),2)


    return usdt_balance


def OPEN_POSITIONS(client, COIN):

    POS_DF                                = pd.DataFrame(client.futures_account()['positions'])
    QTY, DIRECTION_EXIST, ENTRY_PRICE     = 0, 'NA', 0
    
    POS_DF               = POS_DF[POS_DF['symbol'] == COIN]
    
    POS_DF['entryPrice'] = POS_DF['entryPrice'].astype(float)
    POS_DF               = POS_DF[POS_DF['entryPrice'] > 0]
    
    if len(POS_DF) > 0:
        POS_DF               = POS_DF[POS_DF['symbol'] == COIN].reset_index()
        ENTRY_PRICE          = POS_DF.at[0, 'entryPrice']
        DIRECTION_EXIST      = float(POS_DF.at[0, 'positionAmt'])
        QTY                  = abs(float(POS_DF.at[0, 'positionAmt']))

        if DIRECTION_EXIST < 0:
            DIRECTION_EXIST = 'SELL'
        else:
            DIRECTION_EXIST = 'BUY'
    
    return POS_DF, ENTRY_PRICE, DIRECTION_EXIST, QTY


def CREATE_ORDER(client, TICKER, QTY, DIRECTION, LEVERAGE):

    if DIRECTION == 'SHORT':
        SIDE      = 'SELL'
    else:
        SIDE      = 'BUY'

    client.futures_change_leverage(symbol=TICKER, leverage=LEVERAGE)
    client.futures_create_order(symbol=TICKER, side=SIDE, type='MARKET', quantity=QTY)
    
    return


def CLOSE_POSITION(client, TICKER, QTY, DIRECTION_EXIST):
    
    if DIRECTION_EXIST == 'SELL':
        DIRECTION = 'BUY'
    else:
        DIRECTION = 'SELL'
        
    client.futures_create_order(symbol=TICKER, side=DIRECTION, type='MARKET', quantity=QTY)
    
    return


def CREATE_TP_AND_SL(client, TICKER, ENTRY_PRICE, DIRECTION, TAKE_PROFIT, STOP_LOSS, tick_size, TAKE_PROFIT_INC_LT, STOP_LOSS_INC_LT):  

    if DIRECTION == 'BUY':
        SIDE                = 'SELL'
        TAKE_PROFIT_PRICE   = ENTRY_PRICE * (1 + (TAKE_PROFIT/100))
        STOP_LIMIT_PRICE    = ENTRY_PRICE * (1 - (STOP_LOSS/100))   

    else:
        SIDE = 'BUY'
        TAKE_PROFIT_PRICE   = ENTRY_PRICE * (1 - (TAKE_PROFIT/100))
        STOP_LIMIT_PRICE    = ENTRY_PRICE * (1 + (STOP_LOSS/100))        

    TAKE_PROFIT_PRICE = "{:0.0{}f}".format((TAKE_PROFIT_PRICE), tick_size)
    STOP_LIMIT_PRICE = "{:0.0{}f}".format((STOP_LIMIT_PRICE), tick_size)

    print('TAKE PROFIT PRICE : ' + TAKE_PROFIT_PRICE)
    print('STOP LOSS PRICE   : ' + STOP_LIMIT_PRICE)

    if  STOP_LOSS_INC_LT== 'YES':
        try:
            try:
                client.futures_create_order(symbol=TICKER, side=SIDE, type='STOP_MARKET', timeInForce= 'GTE_GTC', stopPrice=STOP_LIMIT_PRICE, closePosition='true') 
            except:
                time.sleep(1)
                client.futures_create_order(symbol=TICKER, side=SIDE, type='STOP_MARKET', timeInForce= 'GTE_GTC', stopPrice=STOP_LIMIT_PRICE, closePosition='true') 
        except:
            pass
        
    if  TAKE_PROFIT_INC_LT== 'YES':
        try:
            try:
                client.futures_create_order(symbol=TICKER, side=SIDE, type='TAKE_PROFIT_MARKET', timeInForce= 'GTE_GTC', stopPrice=TAKE_PROFIT_PRICE, closePosition='true')   
            except:
                time.sleep(1)
                client.futures_create_order(symbol=TICKER, side=SIDE, type='TAKE_PROFIT_MARKET', timeInForce= 'GTE_GTC', stopPrice=TAKE_PROFIT_PRICE, closePosition='true')   
        except:
            pass



    return


def SIZE_2(client, COIN):    
    info = client.futures_exchange_info() 
    info = info['symbols']
    for x in range(len(info)):
        if info[x]['symbol'] == COIN:
            
            return info[x]['quantityPrecision'], info[x]['pricePrecision']
    return None


def SIZES(client, COIN):
    symbol_info = client.get_symbol_info(COIN)
    for filt in symbol_info['filters']:
        if filt['filterType'] == 'LOT_SIZE':
            step_size = float(filt['stepSize'])
        elif filt['filterType'] == 'PRICE_FILTER':
            tick_size = float(filt['tickSize'])

    return step_size, tick_size


def FINISH_TRADE_VIEWS(client, COIN):
        
        df                 = client.futures_account_trades()
        dt_string          = datetime.now().strftime("%Y-%m-%d") 
        df                 = pd.DataFrame(df)
        df['DATE']         = pd.to_datetime(df['time'], unit='ms')
        df['DATE']         = df['DATE'] + pd.DateOffset(hours=1)
        df['DATE']         = pd.to_datetime(df['DATE']).dt.strftime('%Y-%m-%d %H:%M:%S')
        df                 = df.sort_values(by='DATE')
        df                 = df.reset_index()
        df                 = df[(df['symbol'] == COIN)]
        df                 = df.reset_index()
        del df['index']

        df['price']        = round(pd.to_numeric(df['price']),10)
        df['qty']          = round(pd.to_numeric(df['qty']),10)
        df['quoteQty']     = round(pd.to_numeric(df['quoteQty']),10)
        df['commission']   = round(pd.to_numeric(df['commission']),10)

        df1      = pd.pivot_table(df, index=['orderId' ,'DATE', 'symbol', 'side', 'commissionAsset'], aggfunc= {'price': 'mean', 'qty': 'sum', 'quoteQty': 'sum', 'commission':'sum'})
        df1      = df1.sort_values(by='DATE', ascending=True)
        df1      = df1.reset_index()
        
        df1      = df1.rename({'orderId'             :'ORDERID',
                                'DATE'               :'TRADE_DATE', 
                                'symbol'             :'SYMBOL',
                                'side'               :'SIDE', 
                                'price'              :'PRICE', 
                                'qty'                :'QTY',
                                'quoteQty'           :'USDT_VALUE',
                                'commissionAsset'    :'COMMISSION ASSET',
                                'commission'         :'COMMISSION'
                                                    }, axis=1)
        
        return df1





