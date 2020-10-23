# Add import from parent directory possible
import matplotlib.pyplot as plt
from lib.DataOperations import CreateMovingAverage, FindIntersections
from lib.indicator import indicator

# Creation of Williams for data


def CreateWilliamsAlligator(prices):
    return WilliamsAlligator(prices)

# Object with williams alligator


class WilliamsAlligator(indicator):

    def __init__(self, prices):
        indicator.__init__(self, 'Williams', 'trend', prices.index)
        self.jaw, self.teeth, self.lips = self.Init(prices)
        # Signals
        fromBottom, fromTop = FindIntersections(self.lips, self.jaw)
        self.sell = fromTop
        fromBottom, fromTop = FindIntersections(self.lips, self.teeth)
        self.buy = fromBottom

        # Signals
#             fromBottom,fromTop = FindIntersections(self.upperBand, prices)
#             self.sell = fromBottom
#             fromBottom,fromTop = FindIntersections(self.lowerBand, prices)
#             self.buy  = fromTop

    # Set Bollinger indicator
    def Init(self, price):
        jaw = CreateMovingAverage(price, 13, 8)
        teeth = CreateMovingAverage(price, 8, 5)
        lips = CreateMovingAverage(price, 5, 3)
        return jaw, teeth, lips

    # Export indicator signals to report
    def ExportSignals(self, reportSignals):
        reportSignals.AddDataframeSignals(self.buy, 'WilliamsAlligator', 'buy')
        reportSignals.AddDataframeSignals(
            self.sell, 'WilliamsAlligator', 'sell')

    # Plot method
    def Plot(self):
        plt.plot(self.jaw.index, self.jaw, '#0000FF',
                 label='Jaw', linewidth=.8)
        plt.plot(self.teeth.index, self.teeth,
                 '#FF0000', label='Teeth', linewidth=.8)
        plt.plot(self.lips.index, self.lips,
                 '#00FF00', label='Lips', linewidth=.8)
        # Signals plottting
        if (self.buy is not None and self.buy.size):
            plt.plot(self.buy.index, self.buy, 'o',
                     label='Horiz. Buy', color='#00FF00')
        if (self.sell is not None and self.sell.size):
            plt.plot(self.sell.index, self.sell, 'o',
                     label='Horiz. Sell', color='#FF0000')
