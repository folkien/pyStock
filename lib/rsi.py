# Add import from parent directory possible
import matplotlib.pyplot as plt
import pandas as pd
import numpy
from helpers.DataOperations import CreateSubsetByValues, FindIntersections, CreateHorizontalLine
from core.indicator import indicator
from lib.trend import trend


class RSI(indicator):
    # RSI object which creates RSI data

    def __init__(self, close, n=14):
        indicator.__init__(self, 'RSI%u' % n, 'momentum', close.index)
        self.n = n
        self.overBoughtLvl = 70
        self.overSellLvl = 30
        self.hystersis = 5
        self.rsi = self.InitRSI(close, self.n)
        self.notSellSignal = CreateSubsetByValues(self.rsi, 0, 30)
        self.notBuySignal = CreateSubsetByValues(self.rsi, 70, 100)
        self.trendToFall = CreateSubsetByValues(
            self.rsi, 100 - self.hystersis, 100)
        self.trendToRise = CreateSubsetByValues(self.rsi, 0, self.hystersis)
        self.fromBottom50, self.fromTop50 = FindIntersections(self.rsi, 50)

    # Set RSI indicator
    def InitRSI(self, prices, n):
        deltas = numpy.diff(prices)
        seed = deltas[:n + 1]
        up = seed[seed >= 0].sum() / n
        down = -seed[seed < 0].sum() / n
        rs = up / down
        rsi = numpy.zeros_like(prices)
        rsi[:n] = 100. - 100. / (1. + rs)

        for i in range(n, len(prices)):
            delta = deltas[i - 1]  # cause the diff is 1 shorter

            if delta > 0:
                upval = delta
                downval = 0.
            else:
                upval = 0.
                downval = -delta

            up = (up * (n - 1) + upval) / n
            down = (down * (n - 1) + downval) / n

            rs = up / down
            rsi[i] = 100. - 100. / (1. + rs)

        return pd.Series(data=rsi, index=prices.index)

    # Export indicator signals to report
    def ExportSignals(self, reportSignals):
        reportSignals.AddDataframeSignals(self.fromBottom50, 'RSI', 'MayBuy')
        reportSignals.AddDataframeSignals(self.notSellSignal, 'RSI', 'NotSell')
        reportSignals.AddDataframeSignals(self.notBuySignal, 'RSI', 'NotBuy')

    # retunrs -100...100 value
    def GetUnifiedValue(self):
        return (self.rsi[-1] - 50) * 2

    # Plot method
    def Plot(self):
        # Base 50% line
        line50 = CreateHorizontalLine(self.rsi.index, 50, 50)
        plt.plot(self.toNumIndex(line50), line50,
                 '-.', linewidth=1.0, color='#333333')
        # RSI
        plt.plot(self.toNumIndex(self.rsi), self.rsi, label='RSI'
                 + str(self.n), linewidth=1.0, color='#000000')
        x_axis = self.toNumIndex(self.rsi)
        # OverBought
        overBought = CreateHorizontalLine(self.rsi.index, 70, 70, True)
        plt.plot(self.toNumIndex(overBought), overBought, '--',
                 label='Overbought', color='#940006')
        plt.fill_between(x_axis, self.rsi, overBought['value'],
                         where=self.rsi >= overBought['value'], color='#ffb3b3')
        # OverSold
        overSold = CreateHorizontalLine(self.rsi.index, 30, 30, True)
        plt.plot(self.toNumIndex(overSold), overSold, '--',
                 label='Oversold', color='#169400')
        plt.fill_between(x_axis, self.rsi, overSold['value'],
                         where=self.rsi <= overSold['value'], color='#b3ffb3')
        # Trend to Fall
        if (self.trendToFall.size):
            plt.plot(self.toNumIndex(self.trendToFall), self.trendToFall,
                     '*', label='ToFall', color='#FFFF00')
        # Trend to Rise
        if (self.trendToRise.size):
            plt.plot(self.toNumIndex(self.trendToRise), self.trendToRise,
                     '*', label='ToRise', color='#00FFFF')
        # May buy 50
        if (self.fromBottom50.size):
            plt.plot(self.toNumIndex(self.fromBottom50),
                     self.fromBottom50, 'go', label='MayBuy')

        # Plot trend lines
        upTrends = trend(self.rsi, 'rising')
        downTrends = trend(self.rsi, 'falling')
        upTrends.Plot('green', 'rising', 0.6)
        downTrends.Plot('red', 'falling', 0.6)

        plt.ylim(top=100, bottom=0)
