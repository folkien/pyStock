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
  
    
