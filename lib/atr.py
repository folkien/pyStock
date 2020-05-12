# Add import from parent directory possible
import sys
import pandas as pd
import numpy
import matplotlib.pyplot as plt
from lib.DataOperations import *
from lib.ReportSignals import *
from lib.indicator import indicator

# Creates ATR object


def CreateATR(high, low, close, n=14):
    return ATR(high, low, close, n)


# ATR object which creates ATR data
class ATR:

    def __init__(self, high, low, close, n=14):
        self.n = n
        self.tr, self.atr = self.InitATR(high, low, close)

        # Signals
#             fromBottom,fromTop=FindIntersections(self.atr,-100)
#             self.buy  = fromBottom
#             fromBottom,fromTop=FindIntersections(self.atr,100)
#             self.sell = fromTop

    # returns TrueRange
    def GetTr(self):
        return self.tr

    # returns AverageTrueRange
    def GetAtr(self):
        return self.atr

    # Set ATR indicator
    def InitATR(self, high, low, close):
        tr = pd.DataFrame()

        for i in range(len(high.values)):
            value = max(high.values[i] - low.values[i],
                        abs(high.values[i] - close.values[i]),
                        abs(low.values[i] - close.values[i]))
            tr = tr.append(pd.DataFrame(
                {'value': value}, index=[high.index[i]]))

        atr = CreateMovingAverage(tr, self.n)
        return tr, atr

    # Export indicator signals to report
    def ExportSignals(self, reportSignals):
        return 0
#             reportSignals.AddDataframeSignals(self.buy,"ATR","buy")
#             reportSignals.AddDataframeSignals(self.sell,"ATR","sell")

    # Plot method
    def Plot(self):
        # ATR
        plt.plot(self.atr.index, self.atr, label='ATR'
                 + str(self.n), linewidth=1.0, color='#000000')

        # Historic average
#             hAverage = CreateHorizontalLine(self.atr.index, 0, 0)
#             plt.plot(hAverage.index, hAverage, '--', label='H.Average', linewidth=1.0, color = '#333333')
#             #OverBought
#             overBought = CreateHorizontalLine(self.atr.index, 100, 100)
#             plt.plot(overBought.index, overBought, '--', label='Overbought', linewidth=1.0, color = '#940006')
#             #OverSold
#             overSold = CreateHorizontalLine(self.atr.index, -100, -100)
#             plt.plot(overSold.index, overSold, '--', label='Oversold', linewidth=1.0, color = '#169400')
#
#             # Signals plottting
#             if (self.buy is not None and self.buy.size):
#                 plt.plot(self.buy.index, self.buy, 'o', color = '#000000', ms=8)
#                 plt.plot(self.buy.index, self.buy, 'o', label='Buy', color = '#00FF00')
#             if (self.sell is not None and self.sell.size):
#                 plt.plot(self.sell.index, self.sell, 'o', color = '#000000', ms=8)
#                 plt.plot(self.sell.index, self.sell, 'o', label='Sell', color = '#FF0000')

        # Limits of plot
        # plt.ylim(top=100,bottom=-100)
