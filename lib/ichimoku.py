# Add import from parent directory possible
import sys
import pandas as pd
import numpy
import matplotlib.pyplot as plt
from lib.DataOperations import *
from numpy.core.defchararray import lower
from lib.ReportSignals import *
from lib.indicator import indicator
import matplotlib.dates as mdates


# Ichimoku object which creates Ichimoku data
class Ichimoku(indicator):

    def __init__(self, open, high, low, close):
        indicator.__init__(self, 'Ichimoku', 'momentum')
        self.tenkanSen, self.kijunSen, self.chikouSpan, self.senkouSpanA, self.senkouSpanB = self.__initIchimoku(
            open, high, low, close)
        self.low = low

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

        # Senkou Span cross
        fromBottom, fromTop = FindIntersections(
            self.senkouSpanA, self.senkouSpanB)
        self.buy = self.buy.append(fromBottom)
        self.sell = self.sell.append(fromTop)

        # Chikou Span cross
        fromBottom, fromTop = FindIntersections(self.chikouSpan, close)
        # Store original signals positions
        self.buyChikou = fromBottom
        self.sellChikou = fromTop
        # Shift signals back 26 days for chikou span
        fromBottom = self.__shiftIndex(fromBottom, 26)
        fromTop = self.__shiftIndex(fromTop, 26)
        # Append to group
        self.buy = self.buy.append(fromBottom)
        self.sell = self.sell.append(fromTop)

        self.buyweak, self.buyneutral, self.buystrong = self.__filterSignalsByKumo(
            self.buy)
        self.sellweak, self.sellneutral, self.sellstrong = self.__filterSignalsByKumo(
            self.sell)

        # Kumo Breakout
        kumoTop = pd.concat([self.senkouSpanA, self.senkouSpanB]).max(level=0)
        kumoBottom = pd.concat(
            [self.senkouSpanA, self.senkouSpanB]).min(level=0)
        fromBottom, fromTop = FindIntersections(close, kumoTop)
        self.buyneutral = self.buyneutral.append(fromBottom)
        fromBottom, fromTop = FindIntersections(close, kumoBottom)
        self.sellneutral = self.sellneutral.append(fromTop)

    def __shiftIndex(self, data, days=0):
        ''' Shift dataframe index by days.'''
        if (data is not None) and (len(data) > 0):
            data.index = data.index.shift(days, freq='D')
        return data

    def __filterSignalsByKumo(self, signals):
        ''' Filter signals with position based on Kumo'''
        low = pd.DataFrame()
        middle = pd.DataFrame()
        high = pd.DataFrame()

        # Kumo range
        rangeBeg = self.senkouSpanA.index[0]
        rangeEnd = self.senkouSpanA.index[-1]

        for i in range(len(signals)):
            index = signals.index[i]
            # Saturday
            if (index.weekday() == 5):
                index += datetime.timedelta(days=-1)
            # Sunday
            if (index.weekday() == 6):
                index += datetime.timedelta(days=-2)
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

    def __initIchimoku(self, open, high, low, close):
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

    def __plotDayLine(self, ax, days):
        '''
         price - dataframe/series with price values and indexes,
        '''
        line = CreateVerticalLine(
            self.tenkanSen.index[-1-days], self.pmin, self.low.values[-1-days])
        ax.plot(line.index, line, '--', linewidth=1.0, color='black')

        bbox_props = dict(boxstyle='larrow,pad=0.3',
                          fc='w', ec='0.5', alpha=0.6)
        ax.annotate('%d' % days, xy=(mdates.date2num(line.index[-1]), line.values[0]),
                    xytext=(15, -3), textcoords='offset points', bbox=bbox_props)

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
            self.tenkanSen.index[-1], self.pmin, self.low.values[-1])
        plt.plot(line.index, line, '--', linewidth=1.0, color='black')
        self.__plotDayLine(plt, 9)
        self.__plotDayLine(plt, 26)
        self.__plotDayLine(plt, 52)

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
