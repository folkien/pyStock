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
import matplotlib.dates as mdates
from core.indicator import indicator


class trend(indicator):

    def __init__(self, data, type='rising'):
        indicator.__init__(self, 'Trend', 'trend', data.index)
        self.type = type
        self.trends = self.Init(data)

    def Init(self, data):
        '''Init trend based on given data'''
        if (self.type == 'rising'):
            return self.FindUptrends(data)
        return self.FindDowntrends(data)

    @staticmethod
    def FindMaxPeaks(data, n=7):
        '''Return series of max points from given data'''
        maxs = data.iloc[signal.argrelextrema(
            data.values, numpy.greater_equal, order=n)[0]]
        return maxs

    @staticmethod
    def FindMinPeaks(data, n=7):
        '''Return series of min points from given data'''
        mins = data.iloc[signal.argrelextrema(
            data.values, numpy.less_equal, order=n)[0]]
        return mins

    @staticmethod
    def GetTrendDaysLength(trend):
        ''' Returns trend days length '''
        delta = trend.index[-1]-trend.index[0]
        return delta.days

    def FindUptrends(self, data, days=6, n=2):
        ''' Downtrend calculation is based on mins '''
        uptrends = []
        trend = pd.Series()
        mins = self.FindMinPeaks(data, n)

        # Find rising series. Start from end
        for i in range(len(mins.values) - 1):
            # If rising
            if (mins[i] <= mins[i + 1]):
                trend = trend.append(
                    pd.Series(mins.values[i], index=[mins.index[i]]))
                trend = trend.append(
                    pd.Series(mins.values[i + 1], index=[mins.index[i + 1]]))
            elif (trend.size > 0):
                trend = trend.loc[~trend.index.duplicated()]
                if (self.GetTrendDaysLength(trend) >= days):
                    uptrends.append(trend)
                trend = pd.Series()

        # Add last trend
        if (trend.size > 0):
            trend = trend.loc[~trend.index.duplicated()]
            if (self.GetTrendDaysLength(trend) >= days):
                uptrends.append(trend)

        # Calculate regression line most fitting.
        # If some point is far away from line then drop it.
        # Add to data.
        return uptrends

    def FindDowntrends(self, data, days=6, n=2):
        ''' Downtrend calculation is based on maxs '''
        downtrends = []
        trend = pd.Series()
        maxs = self.FindMaxPeaks(data, n)

        # Find falling series. Start from end
        for i in range(len(maxs.values) - 1):
            # If falling
            if (maxs[i] >= maxs[i + 1]):
                trend = trend.append(
                    pd.Series(maxs.values[i], index=[maxs.index[i]]))
                trend = trend.append(
                    pd.Series(maxs.values[i + 1], index=[maxs.index[i + 1]]))
            elif (trend.size > 0):
                trend = trend.loc[~trend.index.duplicated()]
                if (self.GetTrendDaysLength(trend) >= days):
                    downtrends.append(trend)
                trend = pd.Series()

        # Add last trend
        if (trend.size > 0):
            trend = trend.loc[~trend.index.duplicated()]
            if (self.GetTrendDaysLength(trend) >= days):
                downtrends.append(trend)

        return downtrends

    @staticmethod
    def ExtendedTrendForward(trend, days=7):
        # Delta of values
        dy = trend[-1] - trend[-2]
        # Time delta in days
        dt = trend.index[-1] - trend.index[-2]
        dt = dt.days
        # Append last element
        t = trend.index[-1] + datetime.timedelta(days=days)
        y = trend[-1] + days * (dy / dt)
        return trend.append(pd.Series(y, index=[t]))

    @staticmethod
    def GetDistances(t, y, a, b, posFactor=1, negFactor=1):
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

    def Plot(self, tColor='black', tName='rising', tLinewidth=0.8, annotate=False):
        ''' Plots all trends found trends '''
        iterator = 0
        lastIterator = len(self.trends)-2
        for trend in self.trends:
            # For only two dots plot direct line
            if (trend.size == 2):
                trend = self.ExtendedTrendForward(trend)
                plt.plot(self.toNumIndex(trend), trend, '--', color=tColor)
                # Calculate slope
                t = []
                deltas = (trend.index.date - trend.index.date.min())
                for i in range(len(deltas)):
                    t.append(deltas[i].days)
                y = trend.values
                a = (y[1]-y[0])/t[1]
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

                # Plot trend line on graph
                plt.plot(self.toNumIndex(trend), trend, '--',
                         color=tColor, linewidth=tLinewidth)

            # Add annotations
            if (iterator >= lastIterator) and (annotate == True):
                # Calc coordinates of annotation
                x = (self.toNumIndex(trend)[-1]+self.toNumIndex(trend)[0])/2
                y = (trend.values[-1]+trend.values[0])/2
                # week slope converted to int with rounding 2 decimal places
                weekSlope = int((a*7)*100)
                text = '%2.2f/w' % (a*7)

                if (weekSlope > 0):
                    bbox_props = dict(
                        boxstyle='larrow,pad=0.3', fc='g', ec='0.5', alpha=0.6)
                    plt.annotate(text, xy=(x, y),
                                 xytext=(0, -30), textcoords='offset points', fontsize=8, bbox=bbox_props, rotation=-45)
                elif (weekSlope == 0):
                    text = '%2.2f lvl' % (trend.values[0])
                    bbox_props = dict(
                        boxstyle='darrow,pad=0.3', fc='w', ec='0.5', alpha=0.6)
                    plt.annotate(text, xy=(x, y),
                                 xytext=(0, -30), textcoords='offset points', fontsize=8, bbox=bbox_props, rotation=-45)
                else:
                    bbox_props = dict(
                        boxstyle='larrow,pad=0.3', fc='r', ec='0.5', alpha=0.6)
                    plt.annotate(text, xy=(x, y),
                                 xytext=(0, 5), textcoords='offset points', fontsize=8, bbox=bbox_props, rotation=45)
            # Increment trend iterator
            iterator = iterator+1
