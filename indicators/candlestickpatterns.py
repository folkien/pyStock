# Add import from parent directory possible
import matplotlib.pyplot as plt
from core.indicator import indicator
from indicators.candlestick import candlestick


class CandlestickPatterns(indicator):

    def __init__(self, datframe):
        ''' Constructor '''
        indicator.__init__(self, 'CandlestickPatterns', 'momentum')

    def __init(self, dataframe):
        ''' Create CandlestickPatterns indicator '''

    def ExportSignals(self, reportSignals):
        ''' No indicators to Export.'''

    def Plot(self, ax):
        ''' Plotting method.'''
