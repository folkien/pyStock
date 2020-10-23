# Add import from parent directory possible
import matplotlib.pyplot as plt
from lib.DataOperations import FindIntersections, CreateHorizontalLine
from lib.indicator import indicator
from lib.trend import trend


def CreateStoch(high, low, close, n=14, d_n=3):
    # Creates Stoch object
    return Stoch(high, low, close, n, d_n)


class Stoch(indicator):
    """Stochastic Oscillator
    Developed in the late 1950s by George Lane. The stochastic
    oscillator presents the location of the closing price of a
    stock in relation to the high and low range of the price
    of a stock over a period of time, typically a 14-day period.
    https://school.stockcharts.com/doku.php?id=technical_indicators:stochastic_oscillator_fast_slow_and_full
    Args:
        close(pandas.Series): dataset 'Close' column.
        high(pandas.Series): dataset 'High' column.
        low(pandas.Series): dataset 'Low' column.
        n(int): n period.
        d_n(int): sma period over stoch_k.
        fillna(bool): if True, fill nan values.
    """

    def __init__(self, high, low, close, n=14, d_n=3):
        indicator.__init__(self, 'Stoch%u' % n, 'momentum', close.index)
        self.n = n
        self.d_n = n
        self.overBoughtLvl = 80
        self.overSellLvl = 20
        self.k, self.d = self.InitStoch(high, low, close)

        # Signals for stoch
        self.buy, self.sell = FindIntersections(self.k, self.d)

    # Set Stoch indicator
    def InitStoch(self, high, low, close):
        smin = low.rolling(self.n, min_periods=0).min()
        smax = high.rolling(self.n, min_periods=0).max()
        k = 100 * (close - smin) / (smax - smin)
        d = k.rolling(self.d_n, min_periods=0).mean()
        return k, d

    # Export indicator signals to report
    def ExportSignals(self, reportSignals):
        reportSignals.AddDataframeSignals(self.buy, 'Stoch', 'buy')
        reportSignals.AddDataframeSignals(self.sell, 'Stoch', 'sell')

    # retunrs -100...100 value
    def GetUnifiedValue(self):
        return (self.k[-1] - 50) * 2

    # Plot method
    def Plot(self):
        # Stoch %K and %D
        plt.plot(self.toNumIndex(self.k), self.k, label='%K'
                 + str(self.n), linewidth=1.0, color='blue')
        plt.plot(self.toNumIndex(self.d), self.d, label='%D'
                 + str(self.d_n), linewidth=1.0, color='red')
        x_axis = self.toNumIndex(self.k)

        # OverBought
        overBought = CreateHorizontalLine(
            self.k.index, self.overBoughtLvl, self.overBoughtLvl, True)
        plt.plot(self.toNumIndex(overBought), overBought, '--',
                 label='Overbought', color='#940006')
        plt.fill_between(x_axis, self.k, overBought['value'],
                         where=self.k >= overBought['value'], color='#ffb3b3')
        # OverSold
        overSold = CreateHorizontalLine(
            self.k.index, self.overSellLvl, self.overSellLvl, True)
        plt.plot(self.toNumIndex(overSold), overSold, '--',
                 label='Oversold', color='#169400')
        plt.fill_between(x_axis, self.k, overSold['value'],
                         where=self.k <= overSold['value'], color='#b3ffb3')

        # Signals plottting
        if (self.buy is not None and self.buy.size):
            plt.plot(self.toNumIndex(self.buy), self.buy,
                     'o', color='#000000', ms=8)
            plt.plot(self.toNumIndex(self.buy), self.buy, 'o',
                     label='Buy', color='#00FF00')
        if (self.sell is not None and self.sell.size):
            plt.plot(self.toNumIndex(self.sell),
                     self.sell, 'o', color='#000000', ms=8)
            plt.plot(self.toNumIndex(self.sell), self.sell, 'o',
                     label='Sell', color='#FF0000')

        # Plot trend lines
        upTrends = trend(self.k, 'rising')
        downTrends = trend(self.k, 'falling')
        upTrends.Plot('green', 'rising', 0.6)
        downTrends.Plot('red', 'falling', 0.6)

        plt.ylim(top=100, bottom=0)
