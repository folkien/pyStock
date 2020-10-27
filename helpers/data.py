'''
Created on 22 paź 2020

@author: spasz
'''

import pytest
import pandas as pd
import datetime as dt
from math import ceil


def GetStartDateTime(dataframe):
    '''
        Returns begin datetime.
    '''
    return dataframe.index.date[0]


def GetEndDateTime(dataframe):
    '''
        Returns end datetime.
    '''
    return dataframe.index.date[-1]


def TimeShift(df, days):
    ''' Shift dataframe in time.'''
    # Shift right - positive
    if (days > 0):
        day_range = days+2*ceil(abs(days)/5+1)
        wideindex = pd.bdate_range(
            df.index.min(), df.index.max()+dt.timedelta(days=day_range))
        df_new = df.reindex(wideindex)
        return df_new.shift(days).dropna()
    # Shift left - negative
    else:
        day_range = days-2*ceil(abs(days)/5+1)
        wideindex = pd.bdate_range(
            df.index.min()+dt.timedelta(days=day_range), df.index.max())
        df_new = df.reindex(wideindex)
        return df_new.shift(days).dropna()


def toNumIndex(index, df):
    ''' Changed df index to numbers index
        calculated from base DateTime
    '''
    indexBegin = min(index.min(), df.index.min())
    indexEnd = max(index.max(), df.index.max())
    wideindex = pd.bdate_range(indexBegin, indexEnd)
    result = [wideindex.get_loc(i) for i in df.index]
    # subtract beginging offset
    if (index.min() > indexBegin):
        offset = len(pd.bdate_range(indexBegin, index.min())) - 1
        result = [(r - offset) for r in result]
    return result


def GenerateOHLCSawFunction(index, period=26):
    ''' Generates dataframe with OHLC saw function.'''
    direction = 1
    value = 0

    open = []
    high = []
    low = []
    close = []
    volume = []

    for i in range(len(index)):
        # Generate data
        if (direction == 1):
            low.append(value)
            open.append(value+1)
            close.append(value+2)
            high.append(value+3)
        else:
            low.append(value)
            open.append(value+2)
            close.append(value+1)
            high.append(value+3)
        volume.append(1)

        # increment
        value += direction
        if (i % period == 0):
            direction *= -1

    return pd.DataFrame(list(zip(open, high, low, close, volume)), columns=['Open', 'High', 'Low', 'Close', 'Volume']).set_index(index)
