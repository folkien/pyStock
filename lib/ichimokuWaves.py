# Add import from parent directory possible
import sys
import pandas as pd
import numpy
import matplotlib.pyplot as plt
from lib.DataOperations import *
from numpy.core.defchararray import lower
from lib.ReportSignals import *
from lib.indicator import indicator
from helpers.algebra import PointInBetween


class IchimokuWaves(indicator):

    def __init__(self, zigzag):
        ''' Constructor '''
        indicator.__init__(self, 'IchimokuWaves', 'momentum')
        self.zigzag = self.__initIchimokuWaves(open, zigzag)

    def __initIchimokuWaves(self, zigzag):
        ''' Create IchimokuWaves indicator '''
#         highPt = CreateIchimokuWavesPoints(high, slopes=[1])
#         lowPt = CreateIchimokuWavesPoints(low, slopes=[-1])
#         zigzag = highPt.append(lowPt).sort_index().drop(['Dir'], axis=1)
        return zigzag

    def ExportSignals(self, reportSignals):
        ''' No indicators to Export.'''

    def Plot(self, ax):
        ''' Plotting method.'''
        # Lines
        plt.plot(self.zigzag.index, self.zigzag, '--', linewidth=1.0,
                 color='#000000', label=('IchimokuWaves'))
