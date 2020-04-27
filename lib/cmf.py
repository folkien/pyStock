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

#             # Signals
#             fromBottom,fromTop=FindIntersections(self.mfi,20)
#             self.buy  = fromBottom
#             fromBottom,fromTop=FindIntersections(self.mfi,80)
#             self.sell = fromTop
#             # TrenToFall / TrendToRise
#             fromBottom,fromTop=FindIntersections(self.mfi,10)
#             self.buyStrong  = fromBottom
#             fromBottom,fromTop=FindIntersections(self.mfi,90)
#             self.sellStrong = fromTop

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
#         def ExportSignals(self, reportSignals):
#             reportSignals.AddDataframeSignals(self.buy, "MFI","buy")
#             reportSignals.AddDataframeSignals(self.sell,"MFI","sell")
#             reportSignals.AddDataframeSignals(self.buyStrong, "MFI","buyStrong")
#             reportSignals.AddDataframeSignals(self.sellStrong,"MFI","sellStrong")

        # Plot Chaikin money flow 
        def PlotChaikinMoneyFlow(self):
            plt.plot(self.cmf.index, self.cmf, label='CMF' + str(self.n), linewidth=1.0, color = '#000000')
            x_axis = self.cmf.index.get_level_values(0)

            # over > 0 is rising/bullish
            lineZero = CreateHorizontalLine(self.cmf.index, 0, 0, True)
            plt.fill_between(x_axis, self.cmf, lineZero['value'], 
                             where=self.cmf>0,color='#b3ffb3')
            # over > 0 is falling/bearish
            plt.fill_between(x_axis, self.cmf, lineZero['value'], 
                             where=self.cmf<0,color='#ffb3b3')


# #             # Signals plottting
#             if (self.buy is not None and self.buy.size):
#                 plt.plot(self.buy.index, self.buy, 'o', color = '#000000', ms=8)
#                 plt.plot(self.buy.index, self.buy, 'o', label='Buy', color = '#00FF00')
#             if (self.buyStrong is not None and self.buyStrong.size):
#                 plt.plot(self.buyStrong.index, self.buyStrong, 's', color = '#000000', ms=8)
#                 plt.plot(self.buyStrong.index, self.buyStrong, 's', label='BuyStrong', color = '#00FF00')
#             if (self.sell is not None and self.sell.size):
#                 plt.plot(self.sell.index, self.sell, 'o', color = '#000000', ms=8)
#                 plt.plot(self.sell.index, self.sell, 'o', label='Sell', color = '#FF0000')
#             if (self.sellStrong is not None and self.sellStrong.size):
#                 plt.plot(self.sellStrong.index, self.sellStrong, 's', color = '#000000', ms=8)
#                 plt.plot(self.sellStrong.index, self.sellStrong, 's', label='SellStrong', color = '#FF0000')

            # Limits of plot
            plt.ylim(top=1,bottom=-1)

        # Plot chaikin oscillator
        def PlotChaikinOscillator(self):
            # 
            plt.plot(self.cosc.index, self.cosc, label='CHAIKIN' + str(self.n), linewidth=1.0, color = '#000000')
            x_axis = self.cosc.index.get_level_values(0)

            # over > 0 is rising/bullish
            lineZero = CreateHorizontalLine(self.cosc.index, 0, 0, True)
            plt.fill_between(x_axis, self.cosc, lineZero['value'], 
                             where=self.cosc>0,color='#b3ffb3')
            # over > 0 is falling/bearish
            plt.fill_between(x_axis, self.cosc, lineZero['value'], 
                             where=self.cosc<0,color='#ffb3b3')


#             # Signals plottting
#             if (self.buy is not None and self.buy.size):
#                 plt.plot(self.buy.index, self.buy, 'o', color = '#000000', ms=8)
#                 plt.plot(self.buy.index, self.buy, 'o', label='Buy', color = '#00FF00')
#             if (self.buyStrong is not None and self.buyStrong.size):
#                 plt.plot(self.buyStrong.index, self.buyStrong, 's', color = '#000000', ms=8)
#                 plt.plot(self.buyStrong.index, self.buyStrong, 's', label='BuyStrong', color = '#00FF00')
#             if (self.sell is not None and self.sell.size):
#                 plt.plot(self.sell.index, self.sell, 'o', color = '#000000', ms=8)
#                 plt.plot(self.sell.index, self.sell, 'o', label='Sell', color = '#FF0000')
#             if (self.sellStrong is not None and self.sellStrong.size):
#                 plt.plot(self.sellStrong.index, self.sellStrong, 's', color = '#000000', ms=8)
#                 plt.plot(self.sellStrong.index, self.sellStrong, 's', label='SellStrong', color = '#FF0000')

            # Limits of plot
#             plt.ylim(top=100,bottom=0)

