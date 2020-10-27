# Add import from parent directory possible
import matplotlib.pyplot as plt
from core.indicator import indicator
from indicators.candlestick import candlestick


class CandlestickPatterns(indicator):

    def __init__(self, dataframe):
        ''' Constructor '''
        indicator.__init__(self, 'CandlestickPatterns',
                           'momentum', dataframe['Close'].index)
        self.patterns = []
        self.__init(dataframe)

    def __init(self, dataframe):
        ''' Create CandlestickPatterns indicator '''
        self.patterns.append(candlestick.bearish_engulfing(
            dataframe, target='result'))
        self.patterns.append(candlestick.bearish_harami(
            dataframe, target='result'))
        self.patterns.append(candlestick.bullish_engulfing(
            dataframe, target='result'))
        self.patterns.append(candlestick.bullish_harami(
            dataframe, target='result'))
        self.patterns.append(candlestick.dark_cloud_cover(
            dataframe, target='result'))
        self.patterns.append(candlestick.doji_star(dataframe, target='result'))
        self.patterns.append(candlestick.doji(dataframe, target='result'))
        self.patterns.append(candlestick.dragonfly_doji(
            dataframe, target='result'))
#         self.patterns.append(candlestick.evening_star_doji(dataframe, target='result'))
#         self.patterns.append(candlestick.evening_star(dataframe, target='result'))
        self.patterns.append(candlestick.gravestone_doji(
            dataframe, target='result'))
        self.patterns.append(candlestick.hammer(dataframe, target='result'))
        self.patterns.append(candlestick.hanging_man(
            dataframe, target='result'))
        self.patterns.append(candlestick.inverted_hammer(
            dataframe, target='result'))
        self.patterns.append(candlestick.morning_star_doji(
            dataframe, target='result'))
        self.patterns.append(candlestick.morning_star(
            dataframe, target='result'))
        self.patterns.append(candlestick.piercing_pattern(
            dataframe, target='result'))
        self.patterns.append(candlestick.rain_drop_doji(
            dataframe, target='result'))
        self.patterns.append(candlestick.rain_drop(dataframe, target='result'))
        self.patterns.append(candlestick.shooting_star(
            dataframe, target='result'))
        self.patterns.append(candlestick.star(dataframe, target='result'))

    def ExportSignals(self, reportSignals):
        ''' No indicators to Export.'''

    def __plotPattern(self, pname, ptype, dt, value):
        ''' Plot pattern.'''
        x = self.toNumIndex(dt)
        y = value
        text = '%s.%s' % (ptype, pname)
        bbox_props = dict(boxstyle='larrow,pad=0.3',
                          fc='w', ec='0.5', alpha=0.6)
        plt.annotate(text, xy=(x, y), xytext=(
            0, -30), textcoords='offset points', fontsize=8, bbox=bbox_props, rotation=-90)

    def Plot(self, ax):
        ''' Plotting method.'''
        for pattern in self.patterns:
            for i in range(len(pattern['data'])):
                self.__plotPattern(
                    pattern['name'], pattern['type'], pattern['data'].index[i], pattern['data'].values[i])
