# Add import from parent directory possible
import sys
import pandas as pd
import numpy
import matplotlib.pyplot as plt
from lib.DataOperations import *
from numpy.core.defchararray import lower

# Creates  object
def CreateBollinger(prices,n = 20, k=2):
    return Bollinger(prices,n,k)

# Bollinger object which creates Bollinger data
class Bollinger:

        def __init__(self, prices, n=20, k=2):
            self.n     = n
            self.k     = k
            self.mavg, self.upperBand, self.lowerBand  = self.InitBollinger(prices, self.n, self.k)
        
        # Set Bollinger indicator
        def InitBollinger(self,prices,n=20,k=2):
            mavg = prices.rolling(window=n,min_periods=1).mean()
            std  = prices.rolling(window=n,min_periods=1).std()
            upperBand = mavg + (std * 2)
            lowerBand = mavg - (std * 2)
            # TODO : Find consolidation
            # TODO : Find zmienność and buy sell signals 
            return mavg, upperBand, lowerBand

        # Plot method
        def Plot(self):
            # Get index values for the X axis for facebook DataFrame
            x_axis = self.upperBand.index.get_level_values(0)

            # Plot shaded 21 Day Bollinger Band for Facebook
            plt.fill_between(x_axis, self.upperBand, self.lowerBand, color='#BBBBBB')
            plt.plot(self.upperBand.index, self.upperBand, '--', linewidth=1.0, color = '#333333', label="Bol.Upper")
            plt.plot(self.lowerBand.index, self.lowerBand, '--', linewidth=1.0, color = '#333333', label="Bol.Lower")
            plt.plot(self.mavg.index, self.mavg, '--', linewidth=1.0, color = '#0000FF',label=("MA %s days" % self.n))
            

