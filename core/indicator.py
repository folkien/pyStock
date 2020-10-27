'''
Created on 12 maj 2020

@author: spasz
@brief: Base indicator class for all indicators
'''
from helpers.data import toNumIndex


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
        return toNumIndex(self.index, df)

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
