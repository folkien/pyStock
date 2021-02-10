# Add import from parent directory possible
import matplotlib.pyplot as plt
from core.indicator import indicator
import pandas as pd
from numpy import NaN


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
        ax.plot(self.toNumIndex(self.phaseLine), self.phaseLine.values, '--', linewidth=1.0,
                color='#000000', label=('IchimokuPhase'))
