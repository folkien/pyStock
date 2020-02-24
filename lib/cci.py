# Add import from parent directory possible
import sys
import pandas as pd
import numpy
import matplotlib.pyplot as plt
from lib.DataOperations import *
from lib.ReportSignals import *

# Creates CCI object
def CreateCCI(high,low,close,n = 14):
    return CCI(high,low,close,n)


# CCI object which creates CCI data
class CCI:

        def __init__(self, high, low, close, n=14):
            self.n     = n
            self.factor = 0.015
            self.overBoughtLvl = 70
            self.overSellLvl   = 30
            self.cci  = self.InitCCI(high, low, close)
            self.fromBottom50,self.fromTop50=FindIntersections(self.cci,50)

        # Set CCI indicator
        def InitCCI(self,high, low, close):
            TP = (high + low + close) / 3
            data = pd.Series((TP - pd.rolling_mean(TP, self.n)) / (self.factor * pd.rolling_std(TP, self.n)), name = 'CCI_' + str(n))
            return data

        # Export indicator signals to report
        def ExportSignals(self, reportSignals):
            a=1


        # Plot method
        def Plot(self):
            # CCI
            plt.plot(self.cci.index, self.cci, label='CCI', color = '#000000')
            # Buy line
            overBought = CreateDataLine(self.cci.index, 100, 100)
            plt.plot(overBought.index, overBought, '--',  color = '#AAAAAA')
            # Sell line
            overSold = CreateDataLine(self.cci.index, -100, -100)
            plt.plot(overSold.index, overSold, '--', color = '#AAAAAA')

            # Buy
            if (self.notSellSignal.size):
                plt.plot(self.notSellSignal.index, self.notSellSignal, 'x', label='NotSell', color = '#00FF00')
            # Sell
            if (self.notBuySignal.size):
                plt.plot(self.notBuySignal.index, self.notBuySignal, '*', label='NotBuy', color = '#FF0000')

            # Limits of plot
            plt.ylim(top=100,bottom=-100)

