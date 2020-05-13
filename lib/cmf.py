# https://www.tradingview.com/wiki/Chaikin_Money_Flow_(CMF)
# Chaikin money flow
# Chaikin believed that buying and selling pressures could be determined by where a period closes in relation to its high/low range. If the period closes in the upper half of the range, then buying pressure is higher and if the period closes in the lower half of the range, then selling pressure is higher. This is what the Money Flow Multiplier determines (step 1 in the calculation above). The Money Flow Multiplier is what determines The Money Flow Volume and therefore, ultimately Chaikin Money Flow (CMF).
# Chaikin's Money Flow's value fluctuates between 1 and -1. The basic interpretation is:
#     When CMF is closer to 1, buying pressure is higher.
#     When CMF is closer to -1, selling pressure is higher.
# Buying and Selling Pressure can be a good way to confirm an ongoing trend. This can give the trader an added level of confidence that the current trend is likely to continue.
# During a Bullish Trend, continuous Buying Pressure (Chaikin Money Flow values above 0) can indicate that prices will continue to rise.
# During a Bearish Trend, continuous Selling Pressure (Chaikin Money Flow values below 0) can indicate that prices will continue to fall.
# When Chaikin Money Flow crosses the Zero Line, this can be an indication that there is an impending trend reversal.
# Bullish Crosses occur when Chaikin Money Flow crosses from below the Zero Line to above the Zero Line. Price then rises.
# Bearish Crosses occur when Chaikin Money Flow crosses from above the Zero Line to below the Zero Line. Price then falls.
# It should be noted that brief crosses can occur resulting in false signals. The best way to avoid these false signals is by examining past performance for the particular security that is being analyzed and even adjusting the thresholds accordingly. For example, instead of a Zero Line Cross, a technical analyst may use two separate lines such as .05 and -.05.
# Chaikin Money Flow does have a shortfall in its calculation. The shortfall is that the Money Flow Multiplier, which plays into determining Money Flow Volume and therefore Chaikin Money Flow values, does not take into account the change in trading range between periods. This means that if there is any type of gap in price, it won’t be picked up on and therefore Chaikin Money Flow and price will become out of synch.

# https://www.investopedia.com/terms/c/chaikinoscillator.asp
# Example of How to Use the Chaikin Oscillator
# The purpose of the Chaikin oscillator is to identify underlying momentum during fluctuations in accumulation-distribution.
# Specifically, it applies the MACD indicator to accumulation-distribution rather than closing prices.
# For example, a trader wants to determine whether a stock price is more likely to go up or to fall and MACD is trending higher.
# Bullish/Bearish
# The Chaikin oscillator generates a bullish divergence when it crosses above a baseline. The baseline is called the
# accumulation-distribution line. A cross above that line indicates that traders are accumulating, which is typically bullish.
# Buy/Sell
# The Chaikin oscillator utilizes two primary buy and sell signals. First, a positive divergence is confirmed with a center-line
# crossover above the accumulation-distribution line. signaling a potential buying opportunity.. Second, a negative divergence
# is confirmed with a center-line crossover below the accumulation-distribution line., signaling a potential selling opportunity
# A positive divergence signals a stock price is likely to rise, given the increase in accumulation. A negative divergence
# signals a stock price is likely to fall, given the increase in distribution.

# Add import from parent directory possible
import sys
import pandas as pd
import numpy
import matplotlib.pyplot as plt
from lib.DataOperations import *
from lib.ReportSignals import *
from lib.Stock import *
from lib.indicator import indicator

# Creates ChaikinMoneyFlow object


def CreateChaikinMoneyFlow(high, low, close, volume, info, n=21):
    return ChaikinMoneyFlow(high, low, close, volume, info, n)


# ChaikinMoneyFlow object which creates ChaikinMoneyFlow data
class ChaikinMoneyFlow(indicator):

    def __init__(self, high, low, close, volume, info, n=21):
        indicator.__init__(self, 'CMF', 'trend')
        self.n = n
        self.info = info
        self.cmf, self.cosc = self.Init(high, low, close, volume, n)

        # Signals Chaikin Oscillator Bullish/Bearish. Crossings.
        self.toRise, self.toFall = FindIntersections(self.cosc, 0)

    # Set Chaikin MoneyFlow and Chaikin oscillator
    def Init(self, high, low, close, volume, n):
        # Money flow Volume
        N = ((close - low) - (high - close)) / (high - low)
        M = N * abs(volume)

        # Create Chaikin money flow
        Msum = M.rolling(window=n, min_periods=1).sum()
        Vsum = abs(volume).rolling(window=n, min_periods=1).sum()
        cmf = Msum / Vsum

        # Create Chaikin oscillator based on AD (Accumulation/Distribution)
        AD = M.cumsum()
        cosc = AD.ewm(span=3, adjust=False).mean() - \
            AD.ewm(span=10, adjust=False).mean()

        return cmf, cosc

    # Export indicator signals to report
    def ExportSignals(self, reportSignals):
        return 0
#             reportSignals.AddDataframeSignals(self.buy, "MFI","buy")
#             reportSignals.AddDataframeSignals(self.sell,"MFI","sell")
#             reportSignals.AddDataframeSignals(self.buyStrong, "MFI","buyStrong")
#             reportSignals.AddDataframeSignals(self.sellStrong,"MFI","sellStrong")

    # returns -100...100 value
    def GetUnifiedValue(self):
        absmax = max(self.cosc.values.max(), abs(self.cosc.values.min()))
        return (self.cosc.values[-1]*100/absmax)

    # Plot Chaikin money flow
    def PlotChaikinMoneyFlow(self):
        plt.plot(self.cmf.index, self.cmf, label='CMF'
                 + str(self.n), linewidth=1.0, color='#000000')
        x_axis = self.cmf.index.get_level_values(0)

        # over > 0 is rising/bullish
        lineZero = CreateHorizontalLine(self.cmf.index, 0, 0, True)
        plt.fill_between(x_axis, self.cmf, lineZero['value'],
                         where=self.cmf > 0, color='#b3ffb3')
        # over > 0 is falling/bearish
        plt.fill_between(x_axis, self.cmf, lineZero['value'],
                         where=self.cmf < 0, color='#ffb3b3')


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
        plt.ylim(top=1, bottom=-1)

    # Plot chaikin oscillator
    def PlotChaikinOscillator(self):
        #
        plt.plot(self.cosc.index, self.cosc, label='CHAIKIN'
                 + str(self.n), linewidth=1.0, color='#000000')
        x_axis = self.cosc.index.get_level_values(0)

        # over > 0 is rising/bullish
        lineZero = CreateHorizontalLine(self.cosc.index, 0, 0, True)
        plt.fill_between(x_axis, self.cosc, lineZero['value'],
                         where=self.cosc > 0, color='#b3ffb3')
        # Crossings trend change, to Rise
        if (self.toRise.size):
            plt.plot(self.toRise.index, self.toRise,
                     's', color='#000000', ms=8)
            plt.plot(self.toRise.index, self.toRise, 's',
                     label='ToRise', color='#00ff00')

        # under < 0 is falling/bearish
        plt.fill_between(x_axis, self.cosc, lineZero['value'],
                         where=self.cosc < 0, color='#ffb3b3')
        # Crossings trend change, to Fall
        if (self.toFall.size):
            plt.plot(self.toFall.index, self.toFall,
                     's', color='#000000', ms=8)
            plt.plot(self.toFall.index, self.toFall, 's',
                     label='ToFall', color='#ff0000')


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
