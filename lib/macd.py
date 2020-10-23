# Add import from parent directory possible
import sys
import pandas as pd
import numpy
import matplotlib.pyplot as plt
from lib.DataOperations import *
from lib.ReportSignals import *
from lib.indicator import *
from lib.trend import *

# Creates MACD object


def CreateMACD(close):
    return MACD(close)


class MACD(indicator):

    def __init__(self, close):
        indicator.__init__(self, 'MACD', 'trend', close.index)
        self.macd, self.signal = self.InitMACD(close)
        self.buy, self.sell = FindIntersections(self.macd, self.signal)
        # Create histogram
        histogram = self.macd.subtract(self.signal)
        self.hplus = CreateSubsetByValues(histogram, 0, 100)
        self.hminus = CreateSubsetByValues(histogram, -100, 0)

    # Initializes MACD
    def InitMACD(self, price):
        exp1 = price.ewm(span=12, adjust=False).mean()
        exp2 = price.ewm(span=26, adjust=False).mean()

        macdLine = exp1 - exp2
        signalLine = macdLine.ewm(span=9, adjust=False).mean()

        return macdLine, signalLine

    # Export indicator signals to report
    def ExportSignals(self, reportSignals):
        reportSignals.AddDataframeSignals(self.buy, 'MACD', 'buy')
        reportSignals.AddDataframeSignals(self.sell, 'MACD', 'sell')

    # returns -100...100 value
    def GetUnifiedValue(self):
        absmax = max(self.hplus.values.max(), abs(self.hminus.values.min()))
        if (self.macd.values[-1] >= self.signal.values[-1]):
            return (self.hplus.values[-1]*100/absmax)
        else:
            return (self.hminus.values[-1]*100/absmax)

    # Plot MACD

    def Plot(self):
        # Create ZeroLine
        zeroLine = CreateHorizontalLine(self.macd.index, 0, 0)

        # Plot backgrounds
        x_axis = self.toNumIndex(self.signal)
        plt.fill_between(x_axis, self.signal, self.macd,
                         where=self.signal < self.macd, color='#b3ffb3')
        plt.fill_between(x_axis, self.signal, self.macd,
                         where=self.signal >= self.macd, color='#ffb3b3')

        # Plot
        plt.plot(self.toNumIndex(zeroLine), zeroLine, '--', color='#777777')
        plt.plot(self.toNumIndex(self.macd), self.macd, label='AMD MACD',
                 linewidth=1.0, color='#FF0000')
        plt.plot(self.toNumIndex(self.signal), self.signal, label='Signal Line',
                 linewidth=1.0, color='#008800')

        # Signals plottting
        if (self.buy is not None and self.buy.size):
            plt.plot(self.toNumIndex(self.buy), self.buy,
                     'o', color='#000000', ms=8)
            plt.plot(self.toNumIndex(self.buy), self.buy, 'o',
                     label='Buy', color='#00FF00')
        if (self.sell is not None and self.sell.size):
            plt.plot(self.toNumIndex(self.sell),
                     self.sell, 'o', color='#000000', ms=8)
            plt.plot(self.toNumIndex(self.sell), self.sell, 'o',
                     label='Sell', color='#FF0000')

        # Plot trend lines
        upTrends = trend(self.macd, 'rising')
        downTrends = trend(self.macd, 'falling')
        upTrends.Plot('green', 'rising', 0.6)
        downTrends.Plot('red', 'falling', 0.6)

    # Plot Histogram
    def Histogram(self):
        # Create ZeroLine
        zeroLine = CreateHorizontalLine(self.macd.index, 0, 0)
        plt.plot(self.toNumIndex(zeroLine), zeroLine, '--', color='#777777')

        plt.bar(self.toNumIndex(self.hplus),
                self.hplus['value'], color='green')
        plt.bar(self.toNumIndex(self.hminus),
                self.hminus['value'], color='red')
