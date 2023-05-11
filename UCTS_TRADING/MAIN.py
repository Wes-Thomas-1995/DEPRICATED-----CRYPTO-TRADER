
from GOOGLE_SHEET import GOOGLE_SHEET_DATAFRAME
from CONTROLLER import LONG_TERM


from binance.client import Client
from datetime import datetime
import warnings
import time

warnings.filterwarnings("ignore")



def FULL_RUN():

    #BRYONY
    #api_key                 = 'JJoa7QdR28rHMeBrfUSrEbcnMj49fG8Dulw5EvH78NBmIQE8khBqpr13gFNOFhFQ'
    #api_secret              = '5Ld8Oy7NdhKz4uubSgNDKTwKODLt7jdOIojxPBgzTTHnewDoKvvjv4R3AyB0xiSM'

    #WES
    api_key                 = 'wSWDRahsJKzs7ev4OqNsE03I3zNjOqKTriD57WUnIQJT5JDuZ7nZHMTh8bmkIRhb'
    api_secret              = '8wyJh1oqU9sAnfe2votXvnS5Np7HpeYqn2j51zMwgzmM5fCUPVrFV9PcxvsI2LvL'
    
    client                  = Client(api_key, api_secret)

    HOUR_CONDITIONS = {"COIN"              : 'XRPUSDT',
                       "REFERENCE_DAYS"    : [0, 4, 5, 6],
                       "LEVERAGE"          : 20,  
                       "TAKE_PROFIT"       : 0.5,  
                       "STOP_LOSS"         : 2}


    DONE = 'NO'
    while DONE == 'NO':
        if datetime.now() >= (datetime.now().replace(minute=59, second=0, microsecond=0)) or datetime.now() <= (datetime.now().replace(minute=0, second=4, microsecond=0)):

            DONE_LT = 'NO'
            while DONE_LT == 'NO':
                if datetime.now() >= (datetime.now().replace(minute=0, second=0, microsecond=0)) and datetime.now() <= (datetime.now().replace(minute=0, second=59, microsecond=0)):

                    GOOGLE_SHEET_DATA = GOOGLE_SHEET_DATAFRAME(HOUR_CONDITIONS["COIN"])                    
                    STATUS            = LONG_TERM(GOOGLE_SHEET_DATA.DF_LT, 
                                                HOUR_CONDITIONS["COIN"], 
                                                HOUR_CONDITIONS["LEVERAGE"], 
                                                HOUR_CONDITIONS["TAKE_PROFIT"],
                                                HOUR_CONDITIONS["STOP_LOSS"],
                                                HOUR_CONDITIONS["REFERENCE_DAYS"], 
                                                client, 
                                                DONE_LT)
                    
                    DONE_LT = STATUS.DONE_LT
                    DONE    = DONE_LT
                    
                else:
                    DONE_LT = 'YES'
        else:
            DONE = 'YES'








if __name__ == '__main__':

    FULL_RUN()

