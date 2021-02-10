# Add import from parent directory possible
import matplotlib.pyplot as plt
from core.indicator import indicator
import pandas as pd


class IchimokuPhase(indicator):

    def __init__(self, ichimoku, close):
        ''' Constructor '''
        indicator.__init__(self, 'IchimokuPhase', 'momentum', close)
        self.phaseLine = self.__initIchimokuPhase(ichimoku)

    def _isBuy(self, text):
        ''' True if buy text'''
        return (text is 'buy') or (text is 'buyweak') or (text is 'buystrong')

    def _isSell(self, text):
        ''' True if sell text'''
        return (text is 'buy') or (text is 'buyweak') or (text is 'buystrong')

    def __initIchimokuPhase(self, ichimoku):
        ''' Create IchimokuPhase indicator '''
        phaseLine = {}
        phaseValue = 0
        for index, signal in ichimoku.signals.iterrows():
            # Calculate new value
            if (self._isBuy(signal['type'])):
                phaseValue = max(phaseValue+1, 12)
            elif (self._isSell(signal['type'])):
                phaseValue = min(phaseValue-1, -12)

            # Add to phase line
            phaseLine[index] = [phaseValue]

        return pd.DataFrame.from_dict(phaseLine, orient='index')

    def ExportSignals(self, reportSignals):
        ''' No indicators to Export.'''

    def Plot(self, ax):
        ''' Plotting method.'''
        ax.plot(self.toNumIndex(self.phaseLine), self.phaseLine.values, '--', linewidth=1.0,
                color='#000000', label=('IchimokuPhase'))
