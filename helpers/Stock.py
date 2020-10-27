#!/usr/bin/python3
"""
 Stock object.
"""


def SetVolumeWithTrend(price, volumeTotal):
    # Change volumeTotal to neg/pos value
    # Assert condition
    if (price.size != volumeTotal.size):
        return

    lastPrice = price.values[-1]
    # We start from end because data from Stooq is reversed
    for i in reversed(range(1, len(price.values))):
        # If price drop then volumeTotal wih minus value
        if (lastPrice > price.values[i]):
            volumeTotal.values[i] = -volumeTotal.values[i]

        lastPrice = price.values[i]


def GetReturnRates(price, days=1):
    """
    Returns percent return rate for last N days.
    """
    startPrice = price[-1 - days]
    endPrice = price[-1]
    return ((endPrice - startPrice) * 100) / startPrice


def typical_price(data, high_col='High', low_col='Low', close_col='Close'):
    """
    Typical Price
    Source: https://en.wikipedia.org/wiki/Typical_price
    Params:
        data: pandas DataFrame
        high_col: the name of the HIGH values column
        low_col: the name of the LOW values column
        close_col: the name of the CLOSE values column

    Returns:
        copy of 'data' DataFrame with 'typical_price' column added
    """
    data['typical_price'] = (
        data[high_col] + data[low_col] + data[close_col]) / 3
    return data
