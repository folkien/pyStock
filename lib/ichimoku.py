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

    def __init__(self, open, high, low, close):
        self.tenkanSen, self.kijunSen, self.chikouSpan, self.senkouSpanA, self.senkouSpanB = self.InitIchimoku(
            open, high, low, close)

        # Range
        self.pmax = close.max()
        self.pmin = close.min()

        # Signals
        self.buy = None
        self.sell = None

        # Tenkan sen and kijun sen
        fromBottom, fromTop = FindIntersections(self.tenkanSen, self.kijunSen)
#         self.FilterSignalsByKumo(fromBottom)
#         self.FilterSignalsByKumo(fromTop)
        self.buy = fromBottom
        self.sell = fromTop
        # TODO checking Kumo > = <

        # ClosePrice and kijun sen
        fromBottom, fromTop = FindIntersections(close, self.kijunSen)
        self.buy = self.buy.append(fromBottom)
        self.sell = self.sell.append(fromTop)
        # TODO checking Kumo > = <

        # Kumo Breakout

        # Senkou Span cross
        fromBottom, fromTop = FindIntersections(
            self.senkouSpanA, self.senkouSpanB)
        self.buy = self.buy.append(fromBottom)
        self.sell = self.sell.append(fromTop)

        # Chikou Span cross
        fromBottom, fromTop = FindIntersections(self.chikouSpan, close)
        self.buy = self.buy.append(fromBottom)
        self.sell = self.sell.append(fromTop)

#         self.sell = fromBottom
#         fromBottom, fromTop = FindIntersections(self.senkouSpanB, prices)
#         self.buy = fromTop
#         self.consolidation = CreateSubsetByValues(
#             self.absStd, 0, self.consolidationLvl)
#         self.variability = CreateSubsetByValues(
#             self.absStd, self.variabilityLvl, 100)

    def FilterSignalsByKumo(self, signals):
        ''' Filter signals with position based on Kumo'''
        low = pd.DataFrame()
        middle = pd.DataFrame()
        high = pd.DataFrame()

        # Kumo range
        rangeBeg = self.senkouSpanA.index[0]
        rangeEnd = self.senkouSpanA.index[-1]

        for i in range(len(signals)):
            index = signals.index[i]
            index_str = index.strftime('%Y-%m-%d')
            value = signals.values[i]

            # TODO
            if (i >= rangeBeg) and (i <= rangeEnd):
                if (value < self.senkouSpanA[i]) and (value < self.senkouSpanB):
                    low = low.append(signals[i])
                elif (value < self.senkouSpanA) and (value < self.senkouSpanB):
                    middle = middle.append(signals[i])
                else:
                    high = high.append(signals[i])
            else:
                low = low.append(signals[i])

        return low, middle, high

    # Set Ichimoku indicator

    def InitIchimoku(self, open, high, low, close):
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
        reportSignals.AddDataframeSignals(self.buy, 'Ichimoku', 'buy')
        reportSignals.AddDataframeSignals(self.sell, 'Ichimoku', 'sell')

    # Plot method
    def Plot(self, ax):
        # Lines
        plt.plot(self.tenkanSen.index, self.tenkanSen, linewidth=1.2,
                 color='#FF0000', label=('Tenkan(9d) - 1.Resistance'))
        plt.plot(self.kijunSen.index, self.kijunSen, linewidth=1.2,
                 color='#0000FF', label=('Kijun(26d) - 2.Resistance'))
        plt.plot(self.chikouSpan.index, self.chikouSpan,  linewidth=2.0,
                 color='#556B2F', label=('Chikou'))

        # Days before
        line = CreateVerticalLine(
            self.tenkanSen.index[-1], self.pmin, self.pmax)
        plt.plot(line.index, line, '--', linewidth=1.2, color='black')
        line = CreateVerticalLine(
            self.tenkanSen.index[-1-9], self.pmin, self.pmax)
        plt.plot(line.index, line, '--', linewidth=1.2, color='black')
        line = CreateVerticalLine(
            self.tenkanSen.index[-1-17], self.pmin, self.pmax)
        plt.plot(line.index, line, '--', linewidth=1.2, color='black')
        line = CreateVerticalLine(
            self.tenkanSen.index[-1-26], self.pmin, self.pmax)
        plt.plot(line.index, line, '--', linewidth=1.2, color='black')

        # Kumo
        # Get index values for the X axis for facebook DataFrame
        x_axis = self.senkouSpanA.index.get_level_values(0)
        # Plot between
        plt.fill_between(x_axis, self.senkouSpanA,
                         self.senkouSpanB, where=self.senkouSpanA >= self.senkouSpanB, color='#b3ffb3')
        plt.fill_between(x_axis, self.senkouSpanA,
                         self.senkouSpanB, where=self.senkouSpanA < self.senkouSpanB, color='#ffb3b3')
        plt.plot(self.senkouSpanA.index, self.senkouSpanA,
                 linewidth=1.0, color='#80A4AE', label='Senkou A')
        plt.plot(self.senkouSpanB.index, self.senkouSpanB,
                 linewidth=1.0, color='#91CC13', label='Senkou B(52d)')

        # Signals plottting
        if (self.buy is not None and self.buy.size):
            plt.plot(self.buy.index, self.buy, 'o', color='#000000', ms=8)
            plt.plot(self.buy.index, self.buy, 'o',
                     label='Horiz. Buy', color='#00FF00')
        if (self.sell is not None and self.sell.size):
            plt.plot(self.sell.index, self.sell, 'o', color='#000000', ms=8)
            plt.plot(self.sell.index, self.sell, 'o',
                     label='Horiz. Sell', color='#FF0000')
