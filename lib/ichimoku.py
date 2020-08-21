# Add import from parent directory possible
import sys
import pandas as pd
import numpy
import matplotlib.pyplot as plt
from lib.DataOperations import *
from numpy.core.defchararray import lower
from lib.ReportSignals import *
from lib.indicator import indicator


# Ichimoku object which creates Ichimoku data
class Ichimoku:

    def __init__(self, high, low, open, close):
        self.tenkanSen, self.kijunSen, self.chikouSpan, self.senkouSpanA, self.senkouSpanB = self.InitIchimoku(
            high, low, open, close)

#         # Signals
#         fromBottom, fromTop = FindIntersections(self.senkouSpanA, prices)
#         self.sell = fromBottom
#         fromBottom, fromTop = FindIntersections(self.senkouSpanB, prices)
#         self.buy = fromTop
#         self.consolidation = CreateSubsetByValues(
#             self.absStd, 0, self.consolidationLvl)
#         self.variability = CreateSubsetByValues(
#             self.absStd, self.variabilityLvl, 100)

    # Set Ichimoku indicator
    def InitIchimoku(self, high, low, open, close):
        n9high = high.rolling(window=9, min_periods=0).max()
        n9low = low.rolling(window=9, min_periods=0).min()
        n26high = high.rolling(window=26, min_periods=0).max()
        n26low = low.rolling(window=26, min_periods=0).min()
        n52high = high.rolling(window=52, min_periods=0).max()
        n52low = low.rolling(window=52, min_periods=0).min()

        #  Tenkan sen line
        tenkanSen = (n9high+n9low)/2
        #  Kijun sen line
        kijunSen = (n26high+n26low)/2
        # Chikou Span
        chikouSpan = close.shift(-26)
        # Senkou Span A
        senkouSpanA = ((tenkanSen+kijunSen)/2).shift(26)
        # Senkou Span B
        senkouSpanB = ((n52high+n52low)/2).shift(26)
        # Kumo
        return tenkanSen, kijunSen, chikouSpan, senkouSpanA, senkouSpanB

    # Export indicator signals to report
    def ExportSignals(self, reportSignals):
        return
#         reportSignals.AddDataframeSignals(self.buy, 'Ichimoku', 'buy')
#         reportSignals.AddDataframeSignals(self.sell, 'Ichimoku', 'sell')

    # Plot method
    def Plot(self):
        # Lines
        plt.plot(self.tenkanSen.index, self.tenkanSen, '--', linewidth=1.0,
                 color='#FF0000', label=('TenkanSen'))
        plt.plot(self.kijunSen.index, self.kijunSen, '--', linewidth=1.0,
                 color='#0000FF', label=('KijunSen'))
        plt.plot(self.chikouSen.index, self.chikouSen, '--', linewidth=1.0,
                 color='#00FF00', label=('Chikou Span'))

        # Kumo
        # Get index values for the X axis for facebook DataFrame
        x_axis = self.senkouSpanA.index.get_level_values(0)
        # Plot shaded 21 Day Ichimoku Band for Facebook
        plt.fill_between(x_axis, self.senkouSpanA,
                         self.senkouSpanB, color='#BBBBBB')
        plt.plot(self.senkouSpanA.index, self.senkouSpanA, '--',
                 linewidth=1.0, color='#940006', label='Sell band')
        plt.plot(self.senkouSpanB.index, self.senkouSpanB, '--',
                 linewidth=1.0, color='#169400', label='Buy band')

        # Signals plottting
        if (self.buy is not None and self.buy.size):
            plt.plot(self.buy.index, self.buy, 'o', color='#000000', ms=8)
            plt.plot(self.buy.index, self.buy, 'o',
                     label='Horiz. Buy', color='#00FF00')
        if (self.sell is not None and self.sell.size):
            plt.plot(self.sell.index, self.sell, 'o', color='#000000', ms=8)
            plt.plot(self.sell.index, self.sell, 'o',
                     label='Horiz. Sell', color='#FF0000')
