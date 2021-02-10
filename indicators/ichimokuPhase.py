# Add import from parent directory possible
import matplotlib.pyplot as plt
from core.indicator import indicator
import pandas as pd
import numpy as np
from helpers.DataOperations import CreateHorizontalLine


class IchimokuPhase(indicator):

    def __init__(self, ichimoku, close):
        ''' Constructor '''
        indicator.__init__(self, 'IchimokuPhase', 'momentum', close.index)
        self.phaseLine = self.__initIchimokuPhase(ichimoku)

    def _isBuy(self, text):
        ''' True if buy text'''
        return (text is 'buy') or (text is 'buyweak') or (text is 'buystrong')

    def _isSell(self, text):
        ''' True if sell text'''
        return (text is 'sell') or (text is 'sellweak') or (text is 'sellstrong')

    def __initIchimokuPhase(self, ichimoku):
        ''' Create IchimokuPhase indicator '''
        # Get signals data copy and sort by index
        data = ichimoku.signals.sort_index()

        phaseLine = {}
        phaseValue = 0
        for index, signal in data.iterrows():
            # Calculate new value
            if (self._isBuy(signal['type'])):
                phaseValue = min(phaseValue+1, 3)
            elif (self._isSell(signal['type'])):
                phaseValue = max(phaseValue-1, -3)

            # Add to phase line
            phaseLine[index] = phaseValue

        return pd.Series(phaseLine)

    def ExportSignals(self, reportSignals):
        ''' No indicators to Export.'''

    def Plot(self, ax):
        ''' Plotting method.'''
        x_axis = self.toNumIndex(self.phaseLine)

        # Trend rising
        rising = CreateHorizontalLine(self.phaseLine.index, 2, 2, True)
        plt.plot(self.toNumIndex(rising), rising, '--',
                 label='Rising', color='#169400')
        plt.fill_between(x_axis, self.phaseLine, rising['value'],
                         where=self.phaseLine >= rising['value'], color='#b3ffb3')

        # Trend falling
        falling = CreateHorizontalLine(self.phaseLine.index, -2, -2, True)
        plt.plot(self.toNumIndex(falling), falling, '--',
                 label='Falling', color='#940006')
        plt.fill_between(x_axis, self.phaseLine, falling['value'],
                         where=self.phaseLine <= falling['value'], color='#ffb3b3')

        # Phase line
        ax.step(self.toNumIndex(self.phaseLine), self.phaseLine.values, linewidth=1.0,
                color='#000000', label=('IchimokuPhase'), where='post')

        # Limits
        ax.set_ylim([-4, 4])
        ax.set_yticks(np.arange(-4, 4, 1))
        # And a corresponding grid
        ax.grid(which='both')

        # Or if you want different settings for the grids:
        ax.grid(which='minor', alpha=0.2)
        ax.grid(which='major', alpha=0.5)
