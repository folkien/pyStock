'''
Created on 22 paź 2020

@author: spasz
'''

import pytest
import pandas as pd
import datetime
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
    if (days > 0):
        wideindex = pd.bdate_range(df.index.min(), df.index.max(
        )+datetime.timedelta(days=days+ceil(days/7)*2+1))
        df_new = df.reindex(wideindex)
        return df_new.shift(days).dropna()
    else:
        wideindex = pd.bdate_range(
            df.index.min()+datetime.timedelta(days=days+ceil(days/7)*2+1), df.index.max())
        df_new = df.reindex(wideindex)
        return df_new.shift(days).dropna()
