# Add import from parent directory possible
import sys
import pandas as pd
import numpy
import matplotlib.pyplot as plt
from lib.DataOperations import *
from numpy.core.defchararray import lower
from lib.ReportSignals import *
from lib.indicator import indicator
from helpers.algebra import PointInBetween


def CreateZigZagPoints(price, high, low, minSegSize=5, slopes=[1, -1]):
    ''' Creates ZigZag points'''
    curVal = price[0]
    curPos = price.index[0]
    curDir = 1
    dfRes = pd.DataFrame(index=price.index, columns=['Dir', 'Value'])
    for index in price.index:
        if((price[index] - curVal)*curDir >= 0):
            curVal = price[index]
            curPos = index
        else:
            diffrence = abs((price[index]-curVal)/curVal*100)
            if(diffrence >= minSegSize):
                # Store only given slopes
                if (curDir in slopes):
                    if(curDir == 1):
                        dfRes.loc[curPos, 'Value'] = high[curPos]
                    else:
                        dfRes.loc[curPos, 'Value'] = low[curPos]
                    dfRes.loc[curPos, 'Dir'] = curDir
                # Set new search
                curVal = price[index]
                curPos = index
                curDir = -1*curDir

    dfRes[['Value']] = dfRes[['Value']].astype(float)
    return (dfRes.dropna())

# Ichimoku object which creates Ichimoku data


class ZigZag(indicator):

    def __init__(self, open, high, low, close):
        ''' Constructor '''
        indicator.__init__(self, 'ZigZag', 'momentum')
        self.zigzag = self.__initZigZag(open, high, low, close)

    def __initZigZag(self, open, high, low, close):
        ''' Create ZigZag indicator '''
#         highPt = CreateZigZagPoints(high, slopes=[1])
#         lowPt = CreateZigZagPoints(low, slopes=[-1])
#         zigzag = highPt.append(lowPt).sort_index().drop(['Dir'], axis=1)
        zigzag = CreateZigZagPoints(close, high, low).drop(['Dir'], axis=1)
        zigzag = self.__filterPointsInBetween(zigzag)
        return zigzag

    def __filterPointsInBetween(self, zigzag):
        ''' Remove points in between in zigzag.'''
        i = 1
        while (i < (len(zigzag.index)-1)):
            # If point b between a..c then remove it.
            if (PointInBetween(zigzag.values[i-1], zigzag.values[i], zigzag.values[i+1])):
                zigzag.drop([zigzag.index[i]], inplace=True)
            else:
                i += 1

        return zigzag

    def ExportSignals(self, reportSignals):
        ''' No indicators to Export.'''

    def Plot(self, ax):
        ''' Plotting method.'''
        # Lines
        plt.plot(self.zigzag.index, self.zigzag, '--', linewidth=1.0,
                 color='#000000', label=('ZigZag'))
