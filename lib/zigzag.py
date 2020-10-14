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


def CreateZigZagPoints(dfSeries, minSegSize=1, sizeInDevs=0.5, slopes=[1, -1]):
    ''' Creates ZigZag points'''
    curVal = dfSeries[0]
    curPos = dfSeries.index[0]
    curDir = 1
    dfRes = pd.DataFrame(index=dfSeries.index, columns=['Dir', 'Value'])
    for index in dfSeries.index:
        if((dfSeries[index] - curVal)*curDir >= 0):
            curVal = dfSeries[index]
            curPos = index
        else:
            diffrence = abs((dfSeries[index]-curVal)/curVal*100)
            if(diffrence >= minSegSize):
                # Store only given slopes
                if (curDir in slopes):
                    dfRes.loc[curPos, 'Value'] = curVal
                    dfRes.loc[curPos, 'Dir'] = curDir
                # Set new search
                curVal = dfSeries[index]
                curPos = index
                curDir = -1*curDir

    dfRes[['Value']] = dfRes[['Value']].astype(float)
    return (dfRes.dropna())

# Ichimoku object which creates Ichimoku data


class ZigZag(indicator):

    def __init__(self, open, high, low, close):
        ''' Constructor '''
        indicator.__init__(self, 'ZigZag', 'momentum')
        self.zigzag = self.InitZigZag(open, high, low, close)

    def InitZigZag(self, open, high, low, close):
        ''' Create ZigZag indicator '''
        highPt = CreateZigZagPoints(high, slopes=[1])
        lowPt = CreateZigZagPoints(low, slopes=[-1])
        zigzag = highPt.append(lowPt).sort_index().drop(['Dir'], axis=1)
        zigzag = self.__filterPointsInBetween(zigzag)
        return zigzag

    def __filterPointsInBetween(self, zigzag):
        ''' Remove points in between in zigzag.'''
        result = pd.DataFrame(index=zigzag.index, columns=['Value'])
        result.values[0] = zigzag.values[0]
        # Copy only points that are not between surrounding points
        for i in range(1, len(zigzag.index)-1):
            if (not PointInBetween(zigzag.values[i-1], zigzag.values[i], zigzag.values[i+1])):
                result.values[i] = zigzag.values[i]

        result.values[-1] = zigzag.values[-1]
        return result.dropna()

    def ExportSignals(self, reportSignals):
        ''' No indicators to Export.'''

    def Plot(self, ax):
        ''' Plotting method.'''
        # Lines
        plt.plot(self.zigzag.index, self.zigzag, linewidth=1.2,
                 color='magenta', label=('ZigZag'))
