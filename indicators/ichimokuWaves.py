# Add import from parent directory possible
import matplotlib.pyplot as plt
from core.indicator import indicator


class IchimokuWaves(indicator):

    def __init__(self, zigzag):
        ''' Constructor '''
        indicator.__init__(self, 'IchimokuWaves', 'momentum')
        self.zigzag = self.__initIchimokuWaves(open, zigzag)

    @staticmethod
    def __initIchimokuWaves(zigzag):
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
