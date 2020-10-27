# Add import from parent directory possible
import matplotlib.pyplot as plt
import pandas as pd
from helpers.DataOperations import CreateMovingAverage, CreateMovingStd, FindIntersections, CreateHorizontalLine
from core.indicator import indicator
# Creates CCI object


def CreateCCI(high, low, close, n=20):
    return CCI(high, low, close, n)


# CCI object which creates CCI data
class CCI(indicator):

    def __init__(self, high, low, close, n=14):
        indicator.__init__(self, 'CCI%u' % n, 'momentum', close.index)
        self.n = n
        self.factor = 0.015
        self.cci = self.InitCCI(high, low, close)
        self.cciSignal = CreateMovingAverage(self.cci, self.n * 1.5)

        # Signals
        fromBottom, fromTop = FindIntersections(self.cci, -100)
        self.buy = fromBottom
        fromBottom, fromTop = FindIntersections(self.cci, 100)
        self.sell = fromTop

    # Set CCI indicator
    def InitCCI(self, high, low, close):
        ct = (high + low + close) / 3
        self.rollingMean = CreateMovingAverage(ct, self.n)
        self.rollingStd = CreateMovingStd(ct, self.n)
        data = pd.Series((ct - self.rollingMean) / (self.factor
                                                    * self.rollingStd), name='CCI_' + str(self.n))
        data = data.fillna(0)
        return data

    # Export indicator signals to report
    def ExportSignals(self, reportSignals):
        reportSignals.AddDataframeSignals(self.buy, 'CCI', 'buy')
        reportSignals.AddDataframeSignals(self.sell, 'CCI', 'sell')

    # retunrs -100...100 value
    def GetUnifiedValue(self):
        absmax = max(self.cci.values.max(), abs(self.cci.values.min()))
        return (self.cci[-1]*100 / absmax)

    # Plot method
    def Plot(self):
        # CCI
        plt.plot(self.toNumIndex(self.cci), self.cci, label='CCI'
                 + str(self.n), linewidth=1.0, color='#000000')
#             plt.plot(self.toNumIndex(self.cciSignal), self.cciSignal, label='signal', linewidth=1.0, color = '#FF0000')
        x_axis = self.toNumIndex(self.cci)

        # Historic average
        hAverage = CreateHorizontalLine(self.cci.index, 0, 0)
        plt.plot(self.toNumIndex(hAverage), hAverage, '--',
                 linewidth=1.0, color='#333333')
        # OverBought
        overBought = CreateHorizontalLine(self.cci.index, 100, 100, True)
        plt.plot(self.toNumIndex(overBought), overBought, '--',
                 label='Overbought', linewidth=1.0, color='#940006')
        plt.fill_between(x_axis, self.cci, overBought['value'],
                         where=self.cci > overBought['value'], color='#ffb3b3')
        # OverSold
        overSold = CreateHorizontalLine(self.cci.index, -100, -100, True)
        plt.plot(self.toNumIndex(overSold), overSold, '--',
                 label='Oversold', linewidth=1.0, color='#169400')
        plt.fill_between(x_axis, self.cci, overSold['value'],
                         where=self.cci < overSold['value'], color='#b3ffb3')

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

        # Limits of plot
        # plt.ylim(top=100,bottom=-100)
