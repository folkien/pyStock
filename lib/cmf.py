# Add import from parent directory possible
import sys
import pandas as pd
import numpy
import matplotlib.pyplot as plt
from lib.DataOperations import *
from lib.ReportSignals import *
from lib.Stock import *

# Creates ChaikinMoneyFlow object
def CreateChaikinMoneyFlow(high,low,close,volume,info,n = 21):
    return ChaikinMoneyFlow(high,low,close,volume,info,n)


# ChaikinMoneyFlow object which creates ChaikinMoneyFlow data
class ChaikinMoneyFlow:

        def __init__(self, high, low, close, volume, info, n=21):
            self.n = n
            self.info = info
            self.cmf, self.cosc = self.Init(high, low, close, volume, n)

            # Signals
            fromBottom,fromTop=FindIntersections(self.mfi,20)
            self.buy  = fromBottom
            fromBottom,fromTop=FindIntersections(self.mfi,80)
            self.sell = fromTop
            # TrenToFall / TrendToRise
            fromBottom,fromTop=FindIntersections(self.mfi,10)
            self.buyStrong  = fromBottom
            fromBottom,fromTop=FindIntersections(self.mfi,90)
            self.sellStrong = fromTop

        # returns AverageTrueRange
        def GetMoneyFlow(self):
            return self.MoneyFlow

        # Set Chaikin MoneyFlow and Chaikin oscillator
        def Init(self, high, low, close, volume, n):
            # Money flow Volume
            N = ((close-low)-(high-close))/(high-low)
            M = N * abs(volume)
            
            # Create Chaikin money flow
            Msum = M.rolling(window=n,min_periods=1).sum()
            Vsum = abs(volume).rolling(window=n,min_periods=1).sum()
            cmf = Msum / Vsum
            
            # Create Chaikin oscillator based on AD (Accumulation/Distribution)
            AD = M.cumsum()
            cosc = AD.ewm(span=3, adjust=False).mean() - AD.ewm(span=10, adjust=False).mean()

            return cmf, cosc 

        # Export indicator signals to report
        def ExportSignals(self, reportSignals):
            reportSignals.AddDataframeSignals(self.buy, "MFI","buy")
            reportSignals.AddDataframeSignals(self.sell,"MFI","sell")
            reportSignals.AddDataframeSignals(self.buyStrong, "MFI","buyStrong")
            reportSignals.AddDataframeSignals(self.sellStrong,"MFI","sellStrong")

        # Plot method
        def Plot(self):
            # MoneyFlowIndex
            plt.plot(self.mfi.index, self.mfi, label='MFI' + str(self.n), linewidth=1.0, color = '#000000')
            x_axis = self.mfi.index.get_level_values(0)

            #OverBought
            overBought = CreateHorizontalLine(self.mfi.index, 80, 80, True)
            plt.plot(overBought.index, overBought, '--', label='Overbought', linewidth=1.0, color = '#940006')
#             plt.fill_between(x_axis, self.mfi, overBought['value'], 
#                              where=self.mfi>overBought.values,color='#ffb3b3')
            # OverBought - Gene Quong and Avrum Soudack
            overBought = CreateHorizontalLine(self.mfi.index, 90, 90)
            plt.plot(overBought.index, overBought, '--', linewidth=0.6, color = '#940006')

            #OverSold
            overSold = CreateHorizontalLine(self.mfi.index, 20, 20, True)
            plt.plot(overSold.index, overSold, '--', label='Oversold', linewidth=1.0, color = '#169400')
#             plt.fill_between(x_axis, self.mfi, overSold['value'], 
#                              where=self.mfi<overSold.values,color='#b3ffb3')
            # OverSold - Gene Quong and Avrum Soudack
            overSold = CreateHorizontalLine(self.mfi.index, 10, 10)
            plt.plot(overSold.index, overSold, '--', linewidth=0.6, color = '#169400')

#             # Signals plottting
            if (self.buy is not None and self.buy.size):
                plt.plot(self.buy.index, self.buy, 'o', color = '#000000', ms=8)
                plt.plot(self.buy.index, self.buy, 'o', label='Buy', color = '#00FF00')
            if (self.buyStrong is not None and self.buyStrong.size):
                plt.plot(self.buyStrong.index, self.buyStrong, 's', color = '#000000', ms=8)
                plt.plot(self.buyStrong.index, self.buyStrong, 's', label='BuyStrong', color = '#00FF00')
            if (self.sell is not None and self.sell.size):
                plt.plot(self.sell.index, self.sell, 'o', color = '#000000', ms=8)
                plt.plot(self.sell.index, self.sell, 'o', label='Sell', color = '#FF0000')
            if (self.sellStrong is not None and self.sellStrong.size):
                plt.plot(self.sellStrong.index, self.sellStrong, 's', color = '#000000', ms=8)
                plt.plot(self.sellStrong.index, self.sellStrong, 's', label='SellStrong', color = '#FF0000')

            # Limits of plot
            plt.ylim(top=100,bottom=0)

