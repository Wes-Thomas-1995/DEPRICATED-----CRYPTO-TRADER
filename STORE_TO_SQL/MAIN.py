
from datetime import datetime, timedelta, date
from sqlalchemy import create_engine
from binance.client import Client
from binance.enums import *
import pandas as pd
import warnings
import time

warnings.filterwarnings("ignore")







class RELOAD_SAVE_DATA_SQL():

    def __init__(self, TRADE_DF_UCTS, DAILY_DF_UCTS, TRADE_DF_ELLIPSE, DAILY_DF_ELLIPSE):
        self.TRADE_DF_UCTS           = TRADE_DF_UCTS
        self.DAILY_DF_UCTS           = DAILY_DF_UCTS
        self.TRADE_DF_ELLIPSE        = TRADE_DF_ELLIPSE
        self.DAILY_DF_ELLIPSE        = DAILY_DF_ELLIPSE

        self.RELOAD_SAVE_DATA_SQL()


    def RELOAD_SAVE_DATA_SQL(self):
        DATA_UPLOAD_TRADES_UCTS     = self.TRADE_DF_UCTS
        DATA_UPLOAD_BALANCE_UCTS    = self.DAILY_DF_UCTS
        DATA_UPLOAD_TRADES_ELLIPSE  = self.TRADE_DF_ELLIPSE
        DATA_UPLOAD_BALANCE_ELLIPSE = self.DAILY_DF_ELLIPSE

        if len(DATA_UPLOAD_TRADES_UCTS) > 0:

            engine = create_engine( 'postgresql://postgres:Button0104@localhost:5432/ENKI_STOCK_PORTFOLIO')
            DATA_UPLOAD_TRADES_UCTS.to_sql('ucts_trade_history_portfolio', engine, if_exists='append', index=False, chunksize=100000, method='multi')


        engine = create_engine( 'postgresql://postgres:Button0104@localhost:5432/ENKI_STOCK_PORTFOLIO')
        DATA_UPLOAD_BALANCE_UCTS.to_sql('ucts_portfolio_balance_history', engine, if_exists='append', index=False, chunksize=100000, method='multi')

        if len(DATA_UPLOAD_TRADES_ELLIPSE) > 0:

            engine = create_engine( 'postgresql://postgres:Button0104@localhost:5432/ENKI_STOCK_PORTFOLIO')
            DATA_UPLOAD_TRADES_ELLIPSE.to_sql('ellipse_trade_history_portfolio', engine, if_exists='append', index=False, chunksize=100000, method='multi')


        engine = create_engine( 'postgresql://postgres:Button0104@localhost:5432/ENKI_STOCK_PORTFOLIO')
        DATA_UPLOAD_BALANCE_ELLIPSE.to_sql('ellipse_portfolio_balance_history', engine, if_exists='append', index=False, chunksize=100000, method='multi')


        return 













class SAVING_SCRIPT():

    def __init__(self):

        self.TRADE_DF_UCTS, self.DAILY_DF_UCTS, self.TRADE_DF_ELLIPSE, self.DAILY_DF_ELLIPSE = self.SAVING_SCRIPT()


    def SAVING_SCRIPT(self):
        
        

        def FINISH_TRADE_VIEWS(df, dt_string):
            df          = pd.DataFrame(df)
            
            if len(df) > 0:
                
                df['DATE']  = pd.to_datetime(df['time'], unit='ms')
                df['DATE']  = df['DATE'] + pd.DateOffset(hours=1)
                df['DATE']  = pd.to_datetime(df['DATE']).dt.strftime('%Y-%m-%d %H:%M:00')
                df          = df.sort_values(by='DATE')
                df          = df.reset_index()
                df          = df[(df['DATE'] >= dt_string)]
                df          = df.reset_index()
                del df['index']

                df['price']      = round(pd.to_numeric(df['price']),10)
                df['qty']        = round(pd.to_numeric(df['qty']),10)
                df['quoteQty']   = round(pd.to_numeric(df['quoteQty']),10)
                df['commission']   = round(pd.to_numeric(df['commission']),10)

                df1      = pd.pivot_table(df, index=['orderId' ,'DATE', 'symbol', 'side', 'commissionAsset'], aggfunc= {'price': 'mean', 'qty': 'sum', 'quoteQty': 'sum', 'commission':'sum'})
                df1      = df1.sort_values(by='DATE', ascending=True)
                df1      = df1.reset_index()
                
                df1      = df1.rename({'orderId'             :'orderid',
                                        'DATE'               :'trade_date', 
                                        'symbol'             :'symbol',
                                        'side'               :'side', 
                                        'price'              :'price', 
                                        'qty'                :'qty',
                                        'quoteQty'           :'usdt_value',
                                        'commissionAsset'    :'commission_asset',
                                        'commission'         :'commission'
                                                            }, axis=1)
        
            else:
                df1 = df
        
            return df1




        #WES
        api_key                 = 'ix58QoyRdaQrdaVD5X4MxLhzVIbZ6ByU715VRBH4hZTYTwNPashXzeS5bzLuIp6W'
        api_secret              = 'zM0xYsvslnxpjW5DYaITC2FTKFDrWtKF4P2ROiwBohKlWn31tC4pA4dACbaDjf3A'
        client                  = Client(api_key, api_secret)

        dt_string               = datetime.now().strftime("%Y-%m-%d")
        YEAR_STRING             = datetime.now().strftime("%Y") 
        MONTH_STRING            = datetime.now().strftime("%m")
        acc_balance             = client.futures_account_balance()

        for check_balance in acc_balance:
            if check_balance["asset"] == "USDT":
                usdt_balance = round(float(check_balance["balance"]),2)
        
        
        # Create a empty DataFrame.
        DAILY_DF_UCTS = pd.DataFrame()
        DAILY_DF_UCTS['trade_date'] = [dt_string]
        DAILY_DF_UCTS['usdt_value'] = [usdt_balance]

        df              = client.futures_account_trades()
        TRADE_DF_UCTS   = FINISH_TRADE_VIEWS(df, dt_string)





        #BRYONY
        api_key                 = 'JJoa7QdR28rHMeBrfUSrEbcnMj49fG8Dulw5EvH78NBmIQE8khBqpr13gFNOFhFQ'
        api_secret              = '5Ld8Oy7NdhKz4uubSgNDKTwKODLt7jdOIojxPBgzTTHnewDoKvvjv4R3AyB0xiSM'
        client2                 = Client(api_key, api_secret)
        
        acc_balance             = client2.futures_account_balance()

        for check_balance in acc_balance:
            if check_balance["asset"] == "USDT":
                usdt_balance = round(float(check_balance["balance"]),2)
        
        
        # Create a empty DataFrame.
        DAILY_DF_ELLIPSE = pd.DataFrame()
        DAILY_DF_ELLIPSE['trade_date'] = [dt_string]
        DAILY_DF_ELLIPSE['usdt_value'] = [usdt_balance]

        df2              = client2.futures_account_trades()
        TRADE_DF_ELLIPSE   = FINISH_TRADE_VIEWS(df2, dt_string)


        return  TRADE_DF_UCTS, DAILY_DF_UCTS, TRADE_DF_ELLIPSE, DAILY_DF_ELLIPSE







def FULL_RUN():

    DATA = SAVING_SCRIPT()
    RELOAD_SAVE_DATA_SQL(DATA.TRADE_DF_UCTS, DATA.DAILY_DF_UCTS, DATA.TRADE_DF_ELLIPSE, DATA.DAILY_DF_ELLIPSE)





if __name__ == '__main__':

    FULL_RUN()







