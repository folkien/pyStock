'''
Created on 12 maj 2020

@author: spasz
@brief: Base indicator class for all indicators
'''
from builtins import type
import pandas as pd


class indicator(object):
    '''
    classdocs
    '''

    def __init__(self, name, itype, index=None):
        '''
        Constructor
        '''
        # Set indicator type
        self.types = ['momentum', 'trend']
        assert(itype in self.types)
        self.type = itype
        # Set indicator name
        assert(len(name) > 0)
        self.name = name
        # Set base datetime index
        self.index = index

    def toNumIndex(self, df):
        ''' Changed df index to numbers index
            calculated from base DateTime
        '''
        indexBegin = min(self.index.min(), df.index.min())
        indexEnd = max(self.index.max(), df.index.max())
        wideindex = pd.bdate_range(indexBegin, indexEnd)
        result = [wideindex.get_loc(i) for i in df.index]
        # subtract beginging offset
        if (self.index.min() > indexBegin):
            offset = len(pd.bdate_range(indexBegin, self.index.min())) - 1
            result = [(r - offset) for r in result]
        return result

    def GetName(self):
        '''
         Returns type of object
        '''
        return self.name

    def GetType(self):
        '''
         Returns type of object
        '''
        return self.type

    def GetUnifiedValue(self):
        '''
         Returns unified indicator value.
         To implement in indicator.
        '''
        return 0
