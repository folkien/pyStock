# Add import from parent directory possible
import sys
import pandas as pd
import numpy
import matplotlib.pyplot as plt
from lib.DataOperations import *
from lib.ReportSignals import *
from lib.indicator import *

# Creates MACD object


def CreateMACD(prices):
    return MACD(prices)

# Plots MACD object


def PlotMACD(rsi):
    rsi.Plot()

# MACD object which creates MACD data


class MACD(indicator):

    def __init__(self, prices):
        indicator.__init__(self, 'MACD', 'trend')
        self.macd, self.signal = self.InitMACD(prices)
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

    # Plot MACD
    def Plot(self):
        # Create ZeroLine
        zeroLine = CreateHorizontalLine(self.macd.index, 0, 0)

        # Plot backgrounds
        x_axis = self.signal.index.get_level_values(0)
        plt.fill_between(x_axis, self.signal, self.macd,
                         where=self.signal < self.macd, color='#b3ffb3')
        plt.fill_between(x_axis, self.signal, self.macd,
                         where=self.signal >= self.macd, color='#ffb3b3')

        # Plot
        plt.plot(zeroLine.index, zeroLine, '--', color='#777777')
        plt.plot(self.macd.index, self.macd, label='AMD MACD',
                 linewidth=1.0, color='#FF0000')
        plt.plot(self.signal.index, self.signal, label='Signal Line',
                 linewidth=1.0, color='#008800')

        # Signals plottting
        if (self.buy is not None and self.buy.size):
            plt.plot(self.buy.index, self.buy, 'o', color='#000000', ms=8)
            plt.plot(self.buy.index, self.buy, 'o',
                     label='Buy', color='#00FF00')
        if (self.sell is not None and self.sell.size):
            plt.plot(self.sell.index, self.sell, 'o', color='#000000', ms=8)
            plt.plot(self.sell.index, self.sell, 'o',
                     label='Sell', color='#FF0000')

    # Plot Histogram
    def Histogram(self):
        # Create ZeroLine
        zeroLine = CreateHorizontalLine(self.macd.index, 0, 0)
        plt.plot(zeroLine.index, zeroLine, '--', color='#777777')

        plt.bar(self.hplus.index, self.hplus['value'], color='green')
        plt.bar(self.hminus.index, self.hminus['value'], color='red')
