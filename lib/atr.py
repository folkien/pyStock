# Add import from parent directory possible
import matplotlib.pyplot as plt
import pandas as pd
from lib.DataOperations import CreateMovingAverage
from lib.indicator import indicator

# Creates ATR object


def CreateATR(high, low, close, n=14):
    return ATR(high, low, close, n)


# ATR object which creates ATR data
class ATR(indicator):

    def __init__(self, high, low, close, n=14):
        indicator.__init__(self, 'ATR%u' % n, 'trend', close.index)
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
        plt.plot(self.toNumIndex(self.atr), self.atr, label='ATR'
                 + str(self.n), linewidth=1.0, color='#000000')

        # Historic average
#             hAverage = CreateHorizontalLine(self.atr.index, 0, 0)
#             plt.plot(self.toNumIndex(hAverage), hAverage, '--', label='H.Average', linewidth=1.0, color = '#333333')
#             #OverBought
#             overBought = CreateHorizontalLine(self.atr.index, 100, 100)
#             plt.plot(self.toNumIndex(overBought), overBought, '--', label='Overbought', linewidth=1.0, color = '#940006')
#             #OverSold
#             overSold = CreateHorizontalLine(self.atr.index, -100, -100)
#             plt.plot(self.toNumIndex(overSold), overSold, '--', label='Oversold', linewidth=1.0, color = '#169400')
#
#             # Signals plottting
#             if (self.buy is not None and self.buy.size):
#                 plt.plot(self.toNumIndex(self.buy), self.buy, 'o', color = '#000000', ms=8)
#                 plt.plot(self.toNumIndex(self.buy), self.buy, 'o', label='Buy', color = '#00FF00')
#             if (self.sell is not None and self.sell.size):
#                 plt.plot(self.toNumIndex(self.sell), self.sell, 'o', color = '#000000', ms=8)
#                 plt.plot(self.toNumIndex(self.sell), self.sell, 'o', label='Sell', color = '#FF0000')

        # Limits of plot
        # plt.ylim(top=100,bottom=-100)
