'''
Created on 14 paź 2020

@author: spasz
'''


def PointInBetween(a, b, c):
    ''' True if poin b is inside a and c.'''
    return ((a <= b <= c) or (a >= b >= c))
