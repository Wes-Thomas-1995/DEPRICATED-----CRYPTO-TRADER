import pandas as pd
import numpy as np
from datetime import time
import matplotlib.pyplot as plt
import warnings

warnings.filterwarnings("ignore")




def DATE_PROCESSING(df_interval, TIMEZONE):

    DATE_LIST                  = []
    OPEN_LIST                  = []
    CLOSE_LIST                 = []

    if TIMEZONE == "NEW_YORK":
        df_interval['DATE'] = df_interval['NEW_YORK']

    df_interval['TIME']        = df_interval['DATE'].dt.time
    df_interval['TRUE_DATE']   = df_interval['DATE'].dt.date
    GROUP_DF                   = df_interval.groupby(['TRUE_DATE']).agg({'HIGH':'max', 'LOW':'min', 'VOLUME':'sum'}).rename(columns={'HIGH':'TRUE HIGH', 'LOW':'TRUE LOW', 'VOLUME':'TRUE VOLUME'})

    for i in range(len(GROUP_DF)):
        DATE_LIST.append(i+1)

    GROUP_DF['DATE_NUMBER'] = DATE_LIST
    df_interval             = df_interval.merge(GROUP_DF,how='left', left_on='TRUE_DATE', right_on='TRUE_DATE')

    for i in range(len(GROUP_DF)):
        df_interval_date   = df_interval[df_interval['DATE_NUMBER'] == (i + 1)] 
        df_interval_date   = df_interval_date.reset_index()
        OPEN               = df_interval_date.at[0, 'OPEN']
        CLOSE              = df_interval_date.at[len(df_interval_date)-1, 'CLOSE']

        OPEN_LIST.append(OPEN)
        CLOSE_LIST.append(CLOSE)


    GROUP_DF            = GROUP_DF.reset_index()
    GROUP_DF['DATE']    = GROUP_DF['TRUE_DATE']
    GROUP_DF            = GROUP_DF.set_index('DATE')

    df_interval         = df_interval[['DATE', 'OPEN', 'HIGH', 'LOW', 'CLOSE', 'VOLUME', 'TIME', 'TRUE_DATE']].copy()
    df_interval         = df_interval.set_index('DATE')

    GROUP_DF['OPEN']    = OPEN_LIST
    GROUP_DF['HIGH']    = GROUP_DF['TRUE HIGH']
    GROUP_DF['LOW']     = GROUP_DF['TRUE LOW'] 
    GROUP_DF['CLOSE']   = CLOSE_LIST
    GROUP_DF['VOLUME']  = GROUP_DF['TRUE VOLUME']
    df                  = GROUP_DF

    del df['TRUE HIGH']
    del df['TRUE LOW']
    del df['TRUE VOLUME']
    del df['DATE_NUMBER']
    del df['TRUE_DATE']

    return df, df_interval


def DATA_MANIPULATION(df, df_interval):

    SHORT_FAIL_LIST                = []
    LONG_FAIL_LIST                 = []

    df_interval                    = df_interval.reset_index()
    df                             = df.reset_index()

    df['DATE']                     = pd.to_datetime(df['DATE']) 
    df_interval['DATE']            = pd.to_datetime(df_interval['DATE']) 


    ############################ DATA MANIPULATION ############################################################################################################


    df['2_EWM']                    = df['OPEN'].ewm(span=2, adjust=False).mean()
    df['4_EWM']                    = df['OPEN'].ewm(span=4, adjust=False).mean()
    df['12_EWM']                   = df['OPEN'].ewm(span=12, adjust=False).mean()
    df['26_EWM']                   = df['OPEN'].ewm(span=26, adjust=False).mean()

    df_interval['2_EWM']           = df_interval['OPEN'].ewm(span=2, adjust=False).mean()
    df_interval['4_EWM']           = df_interval['OPEN'].ewm(span=4, adjust=False).mean()
    df_interval['12_EWM']          = df_interval['OPEN'].ewm(span=12, adjust=False).mean()
    df_interval['26_EWM']          = df_interval['OPEN'].ewm(span=26, adjust=False).mean()


    ####################### PERCENTAGE WINS AND INDIVIDUAL DRAWDOWNS ##############################################


    df_interval                    = df_interval.set_index('DATE')
    df                             = df.set_index('DATE')

    return df, df_interval


def DF_MANIPULATION_EMA_INTRODUCTION(df):
    
    df                             = df.reset_index()

    EMA_DIRECTION_LIST             = []
    EMA_LIST                       = ['2_EWM', '4_EWM', '12_EWM', '26_EWM']

    for d in range(len(EMA_LIST)-1):
        A = d
        B = d + 1

        EMA_DIRECTION_LIST = []
        VALUE_EMA_LIST     = []
        
        for i in range(len(df)):
            if df.at[i, EMA_LIST[A]] > df.at[i, EMA_LIST[B]]:
                EMA_DIRECTION = 'UP'

            elif df.at[i, EMA_LIST[A]] < df.at[i, EMA_LIST[B]]:
                EMA_DIRECTION = 'DOWN'   

            else:
                EMA_DIRECTION = 'STATIC'

            EMA_DIRECTION_LIST.append(EMA_DIRECTION)


        df['EMA_DIRECTION' + str(EMA_LIST[A]) + ' vs ' + str(EMA_LIST[B])]      = EMA_DIRECTION_LIST


    df                         = df.set_index('DATE')
    
    return df
    

def EMA_TREND_SMALL_INTERVAL(df_interval, df):
    
    EMA_LIST                       = ['2_EWM', '4_EWM', '12_EWM', '26_EWM']
    TIME_LIST                      = []

    df_interval                    = df_interval.reset_index()
    df                             = df.reset_index()

    for i in range(len(df_interval)):
        if i == 0:
            TIME = 'YES'
        elif df_interval.at[i, 'DATE'] == df_interval.at[i, 'DATE'].replace(hour=0, minute=0, second=0):
            TIME = 'YES'
        else:
            TIME = 'NO'

        TIME_LIST.append(TIME)

    df['TRUE_DATE']                   = df['DATE'].dt.date
    df_interval['TIME REFERENCE']     = TIME_LIST
    
    for d in range(len(EMA_LIST)-1):
        A                      = d
        B                      = d + 1
        EMA_DIRECTION_LIST_INT = []
        
        for i in range(len(df_interval)):
            if df_interval.at[i, EMA_LIST[A]] > df_interval.at[i, EMA_LIST[B]]:
                EMA_DIRECTION = 'UP'
            elif df_interval.at[i, EMA_LIST[A]] < df_interval.at[i, EMA_LIST[B]]:
                EMA_DIRECTION = 'DOWN'    
            else:
                EMA_DIRECTION = 'STATIC'

            EMA_DIRECTION_LIST_INT.append(EMA_DIRECTION)

        df_interval['EMA_DIRECTION_SHORT_INTERVALS' + str(EMA_LIST[A]) + ' vs ' + str(EMA_LIST[B])]      = EMA_DIRECTION_LIST_INT
        
    df_TIME_YES                       = df_interval[df_interval['TIME REFERENCE'] == 'YES'] 
    df_TIME_YES                       = df_TIME_YES.reset_index()
    

    COLUMNS_CHOICE = ['DATE', 'TRUE_DATE', 'EMA_DIRECTION_SHORT_INTERVALS' + str(EMA_LIST[0]) + ' vs ' + str(EMA_LIST[1]),
                                           'EMA_DIRECTION_SHORT_INTERVALS' + str(EMA_LIST[1]) + ' vs ' + str(EMA_LIST[2]),
                                           'EMA_DIRECTION_SHORT_INTERVALS' + str(EMA_LIST[2]) + ' vs ' + str(EMA_LIST[3])]
    
    
    df_TIME_YES                       = df_TIME_YES[COLUMNS_CHOICE].copy()
    df_TIME_YES                       = df_TIME_YES.set_index('DATE')

    df_interval                       = df_interval.merge(df_TIME_YES,how='left', left_on='TRUE_DATE', right_on='TRUE_DATE')
    df                                = df.merge(df_TIME_YES,how='left', left_on='TRUE_DATE', right_on='TRUE_DATE')

    df_interval                       = df_interval.set_index('DATE')
    df                                = df.set_index('DATE')

    del df['TRUE_DATE']
    del df['2_EWM']
    del df['4_EWM']
    del df['12_EWM']
    del df['26_EWM']

    return df_interval, df


def STRATEGY_OUTPUT(df, REQUIREMENTS_EMA, REQUIREMENTS_DURATION):

    COLUMN_CONFIG = str(REQUIREMENTS_DURATION) + str(REQUIREMENTS_EMA[0]) + '_EWM vs ' + str(REQUIREMENTS_EMA[1]) + '_EWM'
    df            = df[['OPEN', 'HIGH', 'LOW', 'CLOSE', 'VOLUME', COLUMN_CONFIG]].copy()
    df            = df.rename(columns={COLUMN_CONFIG:'SIGNAL'})


    return df





def HTT_STRATEGY(df_interval, DURATION, REQUIREMENTS_EMA, TIMEZONE_OPTION):

    DIRECTIONAL_OPTIONS            = ['EMA_DIRECTION', 'EMA_DIRECTION_SHORT_INTERVALS']
    OPTIONS                        = ['NORMAL', 'NEW_YORK'] 

    REQUIREMENTS_DURATION          = DIRECTIONAL_OPTIONS[DURATION]
    TIMEZONE                       = OPTIONS[TIMEZONE_OPTION]


    df_interval['DATE']      = pd.to_datetime(df_interval['DATE']) 
    df_interval['NORMAL']    = pd.to_datetime(df_interval['DATE']) 
    df_interval['NEW_YORK']  = df_interval['DATE'] + pd.DateOffset(hours=-5) 

    df, df_interval          = DATE_PROCESSING(df_interval, TIMEZONE) 
    df, df_interval          = DATA_MANIPULATION(df, df_interval) 
    df                       = DF_MANIPULATION_EMA_INTRODUCTION(df) 
    df_interval, df          = EMA_TREND_SMALL_INTERVAL(df_interval, df) 
    df                       = STRATEGY_OUTPUT(df, REQUIREMENTS_EMA, REQUIREMENTS_DURATION)
    
    df = df.reset_index()

    if df.at[(len(df)-1), 'SIGNAL'] == "DOWN":
        DIRECTION_EXIST = "SHORT"
    elif df.at[(len(df)-1), 'SIGNAL'] == "UP":
        DIRECTION_EXIST = "LONG"
    else:
        DIRECTION_EXIST = "NA"




    return df, DIRECTION_EXIST



