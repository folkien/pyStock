'''
Created on 19 maj 2020
@author: spasz
@brief: Trend inidicator. Rising/Falling, based on given data by an argument.

'''
from scipy import signal
import numpy
import datetime
import pandas as pd
import matplotlib.pyplot as plt
from lib.indicator import indicator


class trend(indicator):

    def __init__(self, data, type='rising'):
        indicator.__init__(self, 'Trend', 'trend')
        self.type = type
        self.trends = self.Init(data)

    def Init(self, data):
        '''Init trend based on given data'''
        if (self.type == 'rising'):
            return self.FindUptrends(data)
        else:
            return self.FindDowntrends(data)

    def FindMaxPeaks(self, data, n=7):
        '''Return series of max points from given data'''
        maxs = data.iloc[signal.argrelextrema(
            data.values, numpy.greater_equal, order=n)[0]]
        return maxs

    def FindMinPeaks(self, data, n=7):
        '''Return series of min points from given data'''
        mins = data.iloc[signal.argrelextrema(
            data.values, numpy.less_equal, order=n)[0]]
        return mins

    def FindUptrends(self, data, days=6, n=2):
        ''' Downtrend calculation is based on mins '''
        timeDelta = datetime.timedelta(days=days)
        uptrends = []
        trend = pd.Series()
        mins = self.FindMinPeaks(data, n)

        # Find rising series. Start from end
        for i in range(len(mins.values) - 1):
            # If rising
            if (mins[i] <= mins[i + 1]):
                # If more than time delta
                if (mins.index[i] + timeDelta < mins.index[i + 1]):
                    trend = trend.append(
                        pd.Series(mins.values[i], index=[mins.index[i]]))
                    trend = trend.append(
                        pd.Series(mins.values[i + 1], index=[mins.index[i + 1]]))
            elif (trend.size > 0):
                trend = trend.loc[~trend.index.duplicated()]
                uptrends.append(trend)
                trend = pd.Series()

        # Add last trend
        if (trend.size > 0):
            trend = trend.loc[~trend.index.duplicated()]
            uptrends.append(trend)

        # Calculate regression line most fitting.
        # If some point is far away from line then drop it.
        # Add to data.
        return uptrends

    def FindDowntrends(self, data, days=6, n=2):
        ''' Downtrend calculation is based on maxs '''
        timeDelta = datetime.timedelta(days=days)
        downtrends = []
        trend = pd.Series()
        maxs = self.FindMaxPeaks(data, n)

        # Find falling series. Start from end
        for i in range(len(maxs.values) - 1):
            # If falling
            if (maxs[i] >= maxs[i + 1]):
                # If more than time delta
                if (maxs.index[i] + timeDelta < maxs.index[i + 1]):
                    trend = trend.append(
                        pd.Series(maxs.values[i], index=[maxs.index[i]]))
                    trend = trend.append(
                        pd.Series(maxs.values[i + 1], index=[maxs.index[i + 1]]))
            elif (trend.size > 0):
                trend = trend.loc[~trend.index.duplicated()]
                downtrends.append(trend)
                trend = pd.Series()

        # Add last trend
        if (trend.size > 0):
            trend = trend.loc[~trend.index.duplicated()]
            downtrends.append(trend)

        return downtrends

    def ExtendedTrendForward(self, trend, days=7):
        # Delta of values
        dy = trend[-1] - trend[-2]
        # Time delta in days
        dt = trend.index[-1] - trend.index[-2]
        dt = dt.days
        # Append last element
        t = trend.index[-1] + datetime.timedelta(days=days)
        y = trend[-1] + days * (dy / dt)
        return trend.append(pd.Series(y, index=[t]))

    def GetDistances(self, t, y, a, b, posFactor=1, negFactor=1):
        '''
         Calculates sum of distances between line(at+b) and set of values(t,y)
         Positive/negative factors could be used to diffrent calculate points
         below/above line.
        '''
        sum = 0
        for i in range(0, len(t)):
            liney = a*t[i] + b
            delta = (y[i]-liney)
            if (delta >= 0):
                sum += posFactor*abs(delta)
            else:
                sum += negFactor*abs(delta)
        return sum

    def Plot(self, tColor='black', tName='rising', tLinewidth=0.8):
        ''' Plots all trends found trends '''
        for trend in self.trends:
            # For only two dots plot direct line
            if (trend.size == 2):
                trend = self.ExtendedTrendForward(trend)
                plt.plot(trend.index, trend, '--', color=tColor)
            # For more dots, calculate regression line
            else:
                # Remember datetime of first and last point
                dt0 = trend.index[0]
                dt1 = trend.index[-1]
                # Convert trend to (t,y)
                t = []
                y = trend.values
                deltas = (trend.index.date - trend.index.date.min())
                for i in range(len(deltas)):
                    t.append(deltas[i].days)

                # Set distance calculation factors for
                # data above/below line.
                if (tName == 'rising'):
                    # For rising trend
                    pFactor = 1
                    nFactor = 3
                else:
                    # For falling trend
                    pFactor = 3
                    nFactor = 1

                # Check all possible lines and find line
                # with smallest overall distances from y points.
                a = (y[1]-y[0])/t[1]
                b = y[0]
                bestIndex = 1
                lowestDistances = self.GetDistances(
                    t, y, a, b, pFactor, nFactor)
                for i in range(2, len(t)):
                    a = (y[i]-y[0])/t[i]
                    distances = self.GetDistances(t, y, a, b, pFactor, nFactor)
                    if (lowestDistances > distances):
                        bestIndex = i
                        lowestDistances = distances

                # Calculate bestIndex a slop factor
                a = (y[bestIndex]-y[0])/t[bestIndex]
                # Create line from bestIndex ax+b
                trend = pd.Series()
                y0 = a * t[0] + b
                y1 = a * t[-1] + b
                trend = trend.append(pd.Series(y0, index=[dt0]))
                trend = trend.append(pd.Series(y1, index=[dt1]))
                trend = self.ExtendedTrendForward(trend)
                plt.plot(trend.index, trend, '--',
                         color=tColor, linewidth=tLinewidth)
