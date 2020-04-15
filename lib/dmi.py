# Add import from parent directory possible
import sys
import pandas as pd
import numpy
import matplotlib.pyplot as plt
from lib.DataOperations import *
from lib.ReportSignals import *

# Creates DMI object
def CreateDMI(high,low,atr,n = 14):
    return DMI(high,low,atr,n)


# DMI object which creates DMI data
class DMI:

        def __init__(self, high, low, atr, n=14):
            self.n      = n
            self.dip, self.din, self.adx = self.InitDMI(high, low, atr)

            # Signals
            fromBottom,fromTop=FindIntersections(self.dip,self.din)
            self.buy  = fromBottom
            self.sell = fromTop

        # Set DMI indicator
        def InitDMI(self,high, low, atr):
            DMp = pd.DataFrame()
            DMn = pd.DataFrame()

            for i in range(1,len(high.values)):
                moveUp   = high.values[i]-high.values[i-1]
                moveDown = low.values[i-1]-low.values[i]
                # DM+
                if (moveUp>moveDown) and (moveUp>0):
                    DMp = DMp.append(pd.DataFrame({'value':moveUp},
                                                        index=[high.index[i]]))
                else:
                    DMp = DMp.append(pd.DataFrame({'value':0},
                                                        index=[high.index[i]]))
                # DM-
                if (moveDown>moveUp) and (moveDown>0):
                    DMn = DMn.append(pd.DataFrame({'value':moveDown},
                                                        index=[high.index[i]]))
                else:
                    DMn = DMn.append(pd.DataFrame({'value':0},
                                                        index=[high.index[i]]))

            DIp = 100*CreateMovingAverage(DMp,self.n)/atr
            DIn = 100*CreateMovingAverage(DMn,self.n)/atr
            ADX = 100*abs(DIp-DIn)/abs(DIp+DIn)
            return DIp, DIn, ADX

        # Export indicator signals to report
        def ExportSignals(self, reportSignals):
            return 0
#             reportSignals.AddDataframeSignals(self.buy,"DMI","buy")
#             reportSignals.AddDataframeSignals(self.sell,"DMI","sell")

        # Plot method
        def Plot(self):
            # Strong trend line ADX > 20
            line20 = CreateHorizontalLine(self.adx.index, 25, 25, True)
            plt.plot(line20.index, line20, '--', label='ADX>20', 
                     linewidth=1.0, color = '#333333')

            # Plot backgrounds
            x_axis = self.dip.index.get_level_values(0)
            plt.fill_between(x_axis, self.adx['value'], line20['value'], 
                             where=self.adx['value']>line20['value'],color='#b3b3ff')
            plt.fill_between(x_axis, self.dip['value'], self.din['value'], 
                             where=self.dip['value']>self.din['value'],color='#b3ffb3')
            plt.fill_between(x_axis, self.dip['value'], self.din['value'], 
                             where=self.dip['value']<=self.din['value'],color='#ffb3b3')
            
            # DI+ DI- and ADX
            plt.plot(self.dip.index, self.dip, 
                     label='DI+' + str(self.n), 
                     linewidth=1.0, color = 'green')
            plt.plot(self.din.index, self.din, 
                     label='DI-' + str(self.n), 
                     linewidth=1.0, color = 'red')
            plt.plot(self.adx.index, self.adx, 
                     label='ADX' + str(self.n), 
                     linewidth=1.0, color = 'blue')

 
            # Signals plottting
            if (self.buy is not None and self.buy.size):
                plt.plot(self.buy.index, self.buy, 'o', color = '#000000', ms=8)
                plt.plot(self.buy.index, self.buy, 'o', label='Buy/Uptrend', color = '#00FF00')
            if (self.sell is not None and self.sell.size):
                plt.plot(self.sell.index, self.sell, 'o', color = '#000000', ms=8)
                plt.plot(self.sell.index, self.sell, 'o', label='Sell/Downtrend', color = '#FF0000')
 
            # Limits of plot
            plt.ylim(top=100,bottom=0)

