# Add import from parent directory possible
import sys
import pandas as pd
import numpy
import matplotlib.pyplot as plt
from lib.DataOperations import *
from numpy.core.defchararray import lower
from lib.ReportSignals import *
from lib.indicator import indicator

# Creates  object


def CreateBollinger(prices, n=20, k=2):
    return Bollinger(prices, n, k)

# Bollinger object which creates Bollinger data


class Bollinger(indicator):

    def __init__(self, close, n=20, k=2):
        indicator.__init__(self, 'Bollinger', 'momentum', close.index)
        self.n = n
        self.k = k
        self.consolidationLvl = 15  # percent
        self.variabilityLvl = 50  # percent
        self.mavg, self.upperBand, self.lowerBand = self.InitBollinger(
            close, self.n, self.k)
        self.std = self.upperBand - self.lowerBand
        self.absStd = (self.std * 100) / self.std.max()

        # Signals
        fromBottom, fromTop = FindIntersections(self.upperBand, close)
        self.sell = fromBottom
        fromBottom, fromTop = FindIntersections(self.lowerBand, close)
        self.buy = fromTop
        self.consolidation = CreateSubsetByValues(
            self.absStd, 0, self.consolidationLvl)
        self.variability = CreateSubsetByValues(
            self.absStd, self.variabilityLvl, 100)

    # Set Bollinger indicator
    def InitBollinger(self, prices, n=20, k=2):
        mavg = prices.rolling(window=n, min_periods=1).mean()
        std = prices.rolling(window=n, min_periods=1).std()
        upperBand = mavg + (std * 2)
        lowerBand = mavg - (std * 2)
        return mavg, upperBand, lowerBand

    # Export indicator signals to report
    def ExportSignals(self, reportSignals):
        reportSignals.AddDataframeSignals(self.buy, 'Bollinger', 'buy')
        reportSignals.AddDataframeSignals(self.sell, 'Bollinger', 'sell')

    # Plot method
    def Plot(self):
        # Get index values for the X axis for facebook DataFrame
        x_axis = self.toNumIndex(self.upperBand)

        # Plot shaded 21 Day Bollinger Band for Facebook
        plt.fill_between(x_axis, self.upperBand,
                         self.lowerBand, color='#BBBBBB')
        plt.plot(self.toNumIndex(self.upperBand), self.upperBand, '--',
                 linewidth=1.0, color='#940006', label='Sell band')
        plt.plot(self.toNumIndex(self.lowerBand), self.lowerBand, '--',
                 linewidth=1.0, color='#169400', label='Buy band')
        plt.plot(self.toNumIndex(self.mavg), self.mavg, '--', linewidth=1.0,
                 color='#0000FF', label=('MA %s days' % self.n))

        # Signals plottting
        if (self.buy is not None and self.buy.size):
            plt.plot(self.toNumIndex(self.buy), self.buy,
                     'o', color='#000000', ms=8)
            plt.plot(self.toNumIndex(self.buy), self.buy, 'o',
                     label='Horiz. Buy', color='#00FF00')
        if (self.sell is not None and self.sell.size):
            plt.plot(self.toNumIndex(self.sell),
                     self.sell, 'o', color='#000000', ms=8)
            plt.plot(self.toNumIndex(self.sell), self.sell, 'o',
                     label='Horiz. Sell', color='#FF0000')

    # Plot method
    def PlotAbsDeviation(self):
        plt.plot(self.toNumIndex(self.absStd), self.absStd, linewidth=1.0,
                 color='#333333', label='Bol.AbsDeviation')
        plt.ylim(top=100, bottom=0)
        if (self.consolidation is not None and self.consolidation.size):
            plt.plot(self.toNumIndex(self.consolidation), self.consolidation,
                     'o', label='Consolidation', color='cyan')
        if (self.variability is not None and self.variability.size):
            plt.plot(self.toNumIndex(self.variability), self.variability,
                     'o', label='Variability', color='magenta')
