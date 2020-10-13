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
class Ichimoku(indicator):

    def __init__(self, open, high, low, close):
        indicator.__init__(self, 'Ichimoku', 'momentum')
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
        self.buy = fromBottom
        self.sell = fromTop

        # ClosePrice and kijun sen
        fromBottom, fromTop = FindIntersections(close, self.kijunSen)
        self.buy = self.buy.append(fromBottom)
        self.sell = self.sell.append(fromTop)

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

        self.buyweak, self.buyneutral, self.buystrong = self.FilterSignalsByKumo(
            self.buy)
        self.sellweak, self.sellneutral, self.sellstrong = self.FilterSignalsByKumo(
            self.sell)
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

            # If signal time is in Kumo range
            if (index >= rangeBeg) and (index <= rangeEnd):
                # If signal is lower
                if (value <= self.senkouSpanA[index_str]) and (value <= self.senkouSpanB[index_str]):
                    low = low.append(pd.DataFrame(
                        {'value': value}, index=[index]))
                # If signal is upper
                elif (value >= self.senkouSpanA[index_str]) and (value >= self.senkouSpanB[index_str]):
                    high = high.append(pd.DataFrame(
                        {'value': value}, index=[index]))
                # else signal is inside
                else:
                    middle = middle.append(pd.DataFrame(
                        {'value': value}, index=[index]))
            # Default lower
            else:
                low = low.append(pd.DataFrame({'value': value}, index=[index]))

        return low, middle, high

    def InitIchimoku(self, open, high, low, close):
        ''' Create Ichimoku indicator '''
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
        senkouSpanA = ((tenkanSen+kijunSen)/2).shift(26).dropna()
        # Senkou Span B
        senkouSpanB = ((n52high+n52low)/2).shift(26).dropna()
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
        plt.plot(line.index, line, '--', linewidth=1.0, color='black')
        line = CreateVerticalLine(
            self.tenkanSen.index[-1-9], self.pmin, self.pmax)
        plt.plot(line.index, line, '--', linewidth=1.0, color='black')
        line = CreateVerticalLine(
            self.tenkanSen.index[-1-17], self.pmin, self.pmax)
        plt.plot(line.index, line, '--', linewidth=1.0, color='black')
        line = CreateVerticalLine(
            self.tenkanSen.index[-1-26], self.pmin, self.pmax)
        plt.plot(line.index, line, '--', linewidth=1.0, color='black')

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
        if (self.buyweak is not None and self.buyweak.size):
            plt.plot(self.buyweak.index, self.buyweak,
                     'o', color='#000000', ms=6)
            plt.plot(self.buyweak.index, self.buyweak,
                     'o', color='#53ff4a', ms=4)
        if (self.buyneutral is not None and self.buyneutral.size):
            plt.plot(self.buyneutral.index, self.buyneutral,
                     'o', color='#000000', ms=8)
            plt.plot(self.buyneutral.index, self.buyneutral,
                     'o', color='#00FF00', ms=6)
        if (self.buystrong is not None and self.buystrong.size):
            plt.plot(self.buystrong.index, self.buystrong,
                     'o', color='#000000', ms=12)
            plt.plot(self.buystrong.index, self.buystrong,
                     'o', color='#006b07', ms=10)

        if (self.sellweak is not None and self.sellweak.size):
            plt.plot(self.sellweak.index, self.sellweak,
                     'o', color='#000000', ms=6)
            plt.plot(self.sellweak.index, self.sellweak,
                     'o', color='#ff4a4a', ms=4)
        if (self.sellneutral is not None and self.sellneutral.size):
            plt.plot(self.sellneutral.index, self.sellneutral,
                     'o', color='#000000', ms=8)
            plt.plot(self.sellneutral.index, self.sellneutral,
                     'o', color='#FF0000', ms=6)
        if (self.sellstrong is not None and self.sellstrong.size):
            plt.plot(self.sellstrong.index, self.sellstrong,
                     'o', color='#000000', ms=12)
            plt.plot(self.sellstrong.index, self.sellstrong,
                     'o', color='#8f0000', ms=10)
