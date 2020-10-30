# Add import from parent directory possible
from helpers.data import TimeShift
import matplotlib.pyplot as plt
import pandas as pd
from helpers.DataOperations import FindIntersections, CreateVerticalLine
from core.indicator import indicator
import datetime


# Ichimoku object which creates Ichimoku data
class Ichimoku(indicator):

    def __init__(self, open, high, low, close):
        indicator.__init__(self, 'Ichimoku', 'momentum',
                           close.index)
        self.tenkanSen, self.kijunSen, self.chikouSpan, self.senkouSpanA, self.senkouSpanB = self.__initIchimoku(
            open, high, low, close)
        self.low = low
        self.signals = pd.DataFrame(columns=['value', 'type', 'name'])

        # Range
        self.pmax = close.max()
        self.pmin = close.min()

        # Signals
        self.buy = None
        self.sell = None

        # Tenkan sen and kijun sen
        fromBottom, fromTop = FindIntersections(self.tenkanSen, self.kijunSen)
        self.__filterAppendSignals('TenKij', 1, fromBottom, fromTop)

        # ClosePrice and kijun sen
        fromBottom, fromTop = FindIntersections(close, self.kijunSen)
        self.__filterAppendSignals('CloseKij', 0, fromBottom, fromTop)

        # Senkou Span cross
        fromBottom, fromTop = FindIntersections(
            self.senkouSpanA, self.senkouSpanB, dropna=False)
        self.__filterAppendSignals(
            'KumoChg', 4, fromBottom.shift(-26).dropna(), fromTop.shift(-26).dropna())

        # Chikou Span cross
        fromBottom, fromTop = FindIntersections(
            self.chikouSpan, close, dropna=False)
        self.__filterAppendSignals('ChiClose', 2, fromBottom.shift(
            26).dropna(), fromTop.shift(26).dropna())

        # Kumo Breakout
        kumoTop = pd.concat([self.senkouSpanA, self.senkouSpanB]).max(level=0)
        kumoBottom = pd.concat(
            [self.senkouSpanA, self.senkouSpanB]).min(level=0)
        fromBottom, fromTop = FindIntersections(close, kumoTop)
        self.__appendSignals('KumoBr', 'buy', 3, fromBottom)
        fromBottom, fromTop = FindIntersections(close, kumoBottom)
        self.__appendSignals('KumoBr', 'sell', 3, fromTop)

    def __appendSignals(self, name, type, level, df):
        ''' Append signals to self signals dataframe.'''
        df['type'] = type
        df['name'] = name
        df['level'] = level
        self.signals = self.signals.append(df)

    def __filterSignalsByKumo(self, signals):
        ''' Filter signals with position based on Kumo'''
        low = pd.DataFrame()
        middle = pd.DataFrame()
        high = pd.DataFrame()

        # Kumo range
        rangeBeg = self.senkouSpanA.index[0]
        rangeEnd = self.senkouSpanA.index[-1]

        for i in range(len(signals)):
            index = signals.index[i]
            # Saturday
            if (index.weekday() == 5):
                index += datetime.timedelta(days=-1)
            # Sunday
            if (index.weekday() == 6):
                index += datetime.timedelta(days=-2)
            index_str = index.strftime('%Y-%m-%d')
            value = signals.values[i]

            # If signal time is in Kumo range
            if (index >= rangeBeg) and (index <= rangeEnd):
                # If signal is lower
                if (value <= self.senkouSpanA[index_str]) and (value <= self.senkouSpanB[index_str]):
                    low = low.append(pd.DataFrame(
                        {'value': value}, index=[index]))
                # If signal is upper
                elif (value >= self.senkouSpanA[index_str]) and (value >= self.senkouSpanB[index_str]):
                    high = high.append(pd.DataFrame(
                        {'value': value}, index=[index]))
                # else signal is inside
                else:
                    middle = middle.append(pd.DataFrame(
                        {'value': value}, index=[index]))
            # Default lower
            else:
                low = low.append(pd.DataFrame({'value': value}, index=[index]))

        return low, middle, high

    def __filterAppendSignals(self, name, level, sigbuy, sigsell):
        ''' Append signals to self signals dataframe.'''
        buyweak, buy, buystrong = self.__filterSignalsByKumo(sigbuy)
        self.__appendSignals(name, 'buyweak', level, buyweak)
        self.__appendSignals(name, 'buy', level,  buy)
        self.__appendSignals(name, 'buystrong', level,  buystrong)
        sellweak, sell, sellstrong = self.__filterSignalsByKumo(sigsell)
        self.__appendSignals(name, 'sellweak', level,  sellweak)
        self.__appendSignals(name, 'sell', level,  sell)
        self.__appendSignals(name, 'sellstrong', level,  sellstrong)

    def __initIchimoku(self, open, high, low, close):
        ''' Create Ichimoku indicator '''
        n9high = high.rolling(window=9, min_periods=0).max()
        n9low = low.rolling(window=9, min_periods=0).min()
        n26high = high.rolling(window=26, min_periods=0).max()
        n26low = low.rolling(window=26, min_periods=0).min()
        n52high = high.rolling(window=52, min_periods=0).max()
        n52low = low.rolling(window=52, min_periods=0).min()

        #  Tenkan sen line
        tenkanSen = (n9high+n9low)/2
        #  Kijun sen line
        kijunSen = (n26high+n26low)/2
        # Chikou Span
        chikouSpan = TimeShift(close, -26)
        # Senkou Span A
        senkouSpanA = TimeShift((tenkanSen+kijunSen)/2, 26)
        # Senkou Span B
        senkouSpanB = TimeShift((n52high+n52low)/2, 26)
        # Kumo
        return tenkanSen, kijunSen, chikouSpan, senkouSpanA, senkouSpanB

    # Export indicator signals to report
    def ExportSignals(self, reportSignals):
        reportSignals.AddDataframeSignals(self.buy, 'Ichimoku', 'buy')
        reportSignals.AddDataframeSignals(self.sell, 'Ichimoku', 'sell')

    def __plotDayLine(self, ax, days):
        '''
         price - dataframe/series with price values and indexes,
        '''
        line = CreateVerticalLine(
            self.tenkanSen.index[-1-days], self.pmin, self.low.values[-1-days])
        ax.plot(self.toNumIndex(line), line, '--',
                linewidth=1.0, color='black')

        bbox_props = dict(boxstyle='larrow,pad=0.3',
                          fc='w', ec='0.5', alpha=0.6)
        ax.annotate('%d' % days, xy=(self.toNumIndex(line)[0], line.values[0]),
                    xytext=(15, -3), textcoords='offset points', bbox=bbox_props)

    def __plotSignal(self, pname, ptype, level, dt, value):
        ''' Plot pattern.'''
        # Set color
        color = 'w'
        alpha = 0.3
        if (ptype == 'buyweak'):
            color = 'g'
            alpha = 0.3
        elif (ptype == 'buy'):
            color = 'g'
            alpha = 0.6
        elif (ptype == 'buystrong'):
            color = 'g'
            alpha = 1
        elif (ptype == 'sellweak'):
            color = 'r'
            alpha = 0.3
        elif (ptype == 'sell'):
            color = 'r'
            alpha = 0.6
        elif (ptype == 'sellstrong'):
            color = 'r'
            alpha = 1
        # Set position
        x = self.toNumIndex(dt)
        y = value
        y_low = self.tenkanSen.values.min()
        # Set text
        text = '%s' % (pname)
        # Draw
        bbox_props = dict(boxstyle='circle,pad=0.3',
                          fc=color, ec='0.1', alpha=alpha)
        plt.annotate('%u' % level, xy=(x, y), xycoords='data',
                     xytext=(0, 0), textcoords='offset points', fontsize=8,
                     bbox=bbox_props, rotation=0)
        plt.axvline(x=x, ymax=0.3, color=color, alpha=alpha, linewidth=1)

        bbox_props = dict(boxstyle='round,pad=0.1',
                          fc=color, ec='0.1', alpha=alpha)
        plt.annotate(text, xy=(x, y_low), xycoords='data',
                     xytext=(0, 0), textcoords='offset points', fontsize=8,
                     bbox=bbox_props, rotation=-90)

    def Plot(self, ax):
        ''' Plot method.'''
        # Lines
        plt.plot(self.toNumIndex(self.tenkanSen), self.tenkanSen, linewidth=1.2,
                 color='#FF0000', label=('Tenkan(9d) - 1.Resistance'))
        plt.plot(self.toNumIndex(self.kijunSen), self.kijunSen, linewidth=1.2,
                 color='#0000FF', label=('Kijun(26d) - 2.Resistance'))
        plt.plot(self.toNumIndex(self.chikouSpan), self.chikouSpan,  linewidth=2.0,
                 color='#556B2F', label=('Chikou'))

        # Days before
        line = CreateVerticalLine(
            self.tenkanSen.index[-1], self.pmin, self.low.values[-1])
        plt.plot(self.toNumIndex(line), line, '--',
                 linewidth=1.0, color='black')
        self.__plotDayLine(plt, 9)
        self.__plotDayLine(plt, 26)
        self.__plotDayLine(plt, 52)

        # Kumo
        # Get index values for the X axis for facebook DataFrame
        x_axis = self.toNumIndex(self.senkouSpanA)
        # Plot between
        plt.fill_between(x_axis, self.senkouSpanA,
                         self.senkouSpanB, where=self.senkouSpanA >= self.senkouSpanB, color='#b3ffb3')
        plt.fill_between(x_axis, self.senkouSpanA,
                         self.senkouSpanB, where=self.senkouSpanA < self.senkouSpanB, color='#ffb3b3')
        plt.plot(self.toNumIndex(self.senkouSpanA), self.senkouSpanA,
                 linewidth=1.0, color='#80A4AE', label='Senkou A')
        plt.plot(self.toNumIndex(self.senkouSpanB), self.senkouSpanB,
                 linewidth=1.0, color='#91CC13', label='Senkou B(52d)')

        # Signals plottting
        for i in range(len(self.signals)):
            self.__plotSignal(self.signals['name'][i],
                              self.signals['type'][i],
                              self.signals['level'][i],
                              self.signals.index[i],
                              self.signals['value'][i])
