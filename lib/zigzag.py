# Add import from parent directory possible
import sys
import pandas as pd
import numpy
import matplotlib.pyplot as plt
from lib.DataOperations import *
from numpy.core.defchararray import lower
from lib.ReportSignals import *
from lib.indicator import indicator


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
        return zigzag

    def ExportSignals(self, reportSignals):
        ''' No indicators to Export.'''

    def Plot(self, ax):
        ''' Plotting method.'''
        # Lines
        plt.plot(self.zigzag.index, self.zigzag, linewidth=1.2,
                 color='magenta', label=('ZigZag'))
