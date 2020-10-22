'''
Created on 22 paź 2020

@author: spasz
'''

import pytest


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


def toNumIndex(baseDateTime, dataframe):
    '''
        Recreates index with numbers instead of datetimes.
        Use base datetime as offset 0.
    '''
    deltas = (dataframe.index.date - baseDateTime)
    newIndex = [i.days-2*int(i.days/5) for i in deltas]
    return newIndex
