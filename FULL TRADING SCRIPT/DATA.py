from binance.helpers import round_step_size
from binance.client import Client
from binance.enums import *

from datetime import datetime, timedelta, date
import datetime, time

import numpy as np
import pandas as pd
import warnings
import time
import os

warnings.filterwarnings("ignore")


def HISTORICAL_DATA(client, TICKER, INTERVAL, PERIOD):

    END   = datetime.datetime.now()
    START = END - datetime.timedelta(days = PERIOD)

    intervals = {'1m'  : client.KLINE_INTERVAL_1MINUTE,
                '5m'   : client.KLINE_INTERVAL_5MINUTE,
                '15m'  : client.KLINE_INTERVAL_15MINUTE,
                '30m'  : client.KLINE_INTERVAL_30MINUTE,
                '1h'   : client.KLINE_INTERVAL_1HOUR,
                '2h'   : client.KLINE_INTERVAL_2HOUR,
                '4h'   : client.KLINE_INTERVAL_4HOUR,
                '6h'   : client.KLINE_INTERVAL_6HOUR,
                '8h'   : client.KLINE_INTERVAL_8HOUR,
                '12h'  : client.KLINE_INTERVAL_12HOUR,
                '1d'   : client.KLINE_INTERVAL_1DAY,
                '3d'   : client.KLINE_INTERVAL_3DAY,
                '1w'   : client.KLINE_INTERVAL_1WEEK,
                '1M'   : client.KLINE_INTERVAL_1MONTH}

    candle = np.asarray(client.get_historical_klines(TICKER, 
                                                intervals.get(INTERVAL), 
                                                str(START), 
                                                str(END)
                                                ))

    candle = candle[:, :6]
    candle = pd.DataFrame(candle, columns=['datetime', 'open', 'high', 'low', 'close', 'volume']).astype(float).rename(columns={'datetime':'DATE', 'open':'OPEN', 'high':'HIGH', 'low':'LOW', 'close':'CLOSE', 'volume':'VOLUME'})
    candle.DATE = pd.to_datetime(candle.DATE, unit='ms')
    
    return candle


