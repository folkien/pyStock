# Add import from parent directory possible
import sys
import pandas as pd
import numpy
import matplotlib.pyplot as plt
from lib.DataOperations import *

# Creates MACD object
def CreateMACD(prices):
    return MACD(prices)

# Plots MACD object
def PlotMACD(rsi):
    rsi.Plot()

# MACD object which creates MACD data
class MACD:

        def __init__(self, prices):
            self.macd, self.signal = self.InitMACD(prices)
            self.buy, self.sell    = FindIntersections(self.macd, self.signal)
            # Create histogram
            histogram = self.macd.subtract(self.signal)
            self.hplus = CreateSubsetByValues(histogram, 0, 100)
            self.hminus = CreateSubsetByValues(histogram, -100, 0)
        
        # Initializes MACD
        def InitMACD(self,price):
            exp1 = price.ewm(span=12, adjust=False).mean()
            exp2 = price.ewm(span=26, adjust=False).mean()
            
            macdLine = exp1-exp2
            signalLine = macdLine.ewm(span=9, adjust=False).mean()

            return macdLine, signalLine
        
        # Plot MACD
        def Plot(self):
            #Create ZeroLine
            zeroLine = CreateDataLine(self.macd.index, 0, 0)
            
            # Plot
            plt.plot(zeroLine.index,zeroLine,'--',color='#777777')
            plt.plot(self.macd.index, self.macd, label='AMD MACD', color = '#FF0000')
            plt.plot(self.signal.index, self.signal, label='Signal Line', color='#008800')
            plt.plot(self.buy.index, self.buy, 'go', label='Buy')
            plt.plot(self.sell.index, self.sell, 'ro', label='Sell')
            
        # Plot Histogram
        def Histogram(self):
            #Create ZeroLine
            zeroLine = CreateDataLine(self.macd.index, 0, 0)

            plt.plot(zeroLine.index,zeroLine,'--',color='#777777')
        #     hminus.plot.bar()
            plt.stem(self.hplus.index,self.hplus,linefmt='green',markerfmt='go', label="Trend +rise power")
            plt.stem(self.hminus.index,self.hminus,linefmt='red',markerfmt='ro', label="Trend -fall power")

