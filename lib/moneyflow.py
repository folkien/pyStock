# Add import from parent directory possible
import sys
import pandas as pd
import numpy
import matplotlib.pyplot as plt
from lib.DataOperations import *
from lib.ReportSignals import *
from lib.Stock import *

# Creates MoneyFlow object
def CreateMoneyFlow(high,low,close,volume,n = 14):
    return MoneyFlow(high,low,close,volume,n)


# MoneyFlow object which creates MoneyFlow data
class MoneyFlow:

        def __init__(self, high, low, close, volume, n=14):
            self.n              = n
            self.typicalPrice   = (high+low+close )/3
            self.MoneyFlow    = self.InitMoneyFlow(self.typicalPrice, volume, n)

            # Signals
#             fromBottom,fromTop=FindIntersections(self.MoneyFlow,-100)
#             self.buy  = fromBottom
#             fromBottom,fromTop=FindIntersections(self.MoneyFlow,100)
#             self.sell = fromTop

        # returns AverageTrueRange
        def GetMoneyFlow(self):
            return self.MoneyFlow

        # Set MoneyFlow indicator
        def InitMoneyFlow(self, tp, volume, n):
            moneyFlow = tp * volume
            posFlow = [moneyFlow[idx] if moneyFlow[idx] else 0 for idx in range(0, len(moneyFlow))]
            negFlow = [moneyFlow[idx] if not moneyFlow[idx] else 0 for idx in range(0, len(moneyFlow))]
            # TODO add rolling over pos and neg flow
            moneyRatio = 0
            moneyFlowIndex = 100 - (100/(1+moneyRatio))
            return moneyFlow

        # Export indicator signals to report
        def ExportSignals(self, reportSignals):
            return 0
#             reportSignals.AddDataframeSignals(self.buy,"MoneyFlow","buy")
#             reportSignals.AddDataframeSignals(self.sell,"MoneyFlow","sell")

        # Plot method
        def Plot(self):
            # MoneyFlow
            plt.plot(self.MoneyFlow.index, self.MoneyFlow, label='MoneyFlow' + str(self.n), linewidth=1.0, color = '#000000')

            #OverBought
            overBought = CreateDataLine(self.MoneyFlow.index, 80, 80)
            plt.plot(overBought.index, overBought, '--', label='Overbought', linewidth=1.0, color = '#940006')
            #OverSold
            overSold = CreateDataLine(self.MoneyFlow.index, 20, 20)
            plt.plot(overSold.index, overSold, '--', label='Oversold', linewidth=1.0, color = '#169400')

#             # Signals plottting
#             if (self.buy is not None and self.buy.size):
#                 plt.plot(self.buy.index, self.buy, 'o', color = '#000000', ms=8)
#                 plt.plot(self.buy.index, self.buy, 'o', label='Buy', color = '#00FF00')
#             if (self.sell is not None and self.sell.size):
#                 plt.plot(self.sell.index, self.sell, 'o', color = '#000000', ms=8)
#                 plt.plot(self.sell.index, self.sell, 'o', label='Sell', color = '#FF0000')

            # Limits of plot
            plt.ylim(top=100,bottom=0)

