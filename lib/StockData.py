'''
Created on 5 lut 2020

@author: spasz
'''
from pandas_datareader import data
import matplotlib.pyplot as plt
# Need tot go to python 3
import mpl_finance
import sys
from mpl_finance import candlestick2_ohlc
from lib.DataOperations import *

# StockData object which creates StockData data
class StockData:

        def __init__(self, stockCode, beginDate, endDate):
            self.dataSubset = {'Open' : 0, 'High' :0, 'Low' : 0, 'Close' : 0, 'Volume' : 0}
            self.data = self.FetchData(stockCode,beginDate,endDate)
            self.dataSubset['Open']   =  SetReindex(self.data['Open'],self.beginDate,self.endDate)
            self.dataSubset['High']   =  SetReindex(self.data['High'],self.beginDate,self.endDate)
            self.dataSubset['Low']    =  SetReindex(self.data['Low'],self.beginDate,self.endDate)
            self.dataSubset['Close']  =  SetReindex(self.data['Close'],self.beginDate,self.endDate)
            self.dataSubset['Volume'] =  SetReindex(self.data['Volume'],self.beginDate,self.endDate)

        # Get DATA from URL
        # User pandas_reader.data.DataReader to load the desired data. As simple as that.
        def FetchData(self,stockCode,beginDate,endDate):
            self.stockCode = stockCode
            self.beginDate = beginDate
            self.endDate   = endDate

            receivedData = data.DataReader(self.stockCode, 'stooq', self.beginDate, self.endDate)

            if len(receivedData) == 0:
                print("No Stooq data for entry %s!" % (stockCode))
                sys.exit(1)

            return receivedData

        # Get named data
        def GetAllData(self,name):
            return self.data[name]

        # Get named data
        def GetData(self,name):
            return self.dataSubset[name]

        # Plot all stock data
        def PlotAll(self):
            plt.plot(self.data['Close'].index, self.data['Close'], "#000000", label=self.stockCode)
            return 0

        # Plot stock data
        def Plot(self):
            plt.plot(self.dataSubset['Close'].index, self.dataSubset['Close'], "#000000", label=self.stockCode)
            return 0

        # Plot all stock data
        def PlotCandleAll(self):
            candlestick2_ohlc(ax,
                              self.data['Open'].values,
                              self.data['High'].values,
                              self.data['Low'].values,
                              self.data['Close'].values,
                              width=0.6,
                              colorup='g',
                              colordown='r',
                              alpha=1)

        # Plot stock data
        def PlotCandle(self,ax):
            candlestick2_ohlc(ax,
                              self.dataSubset['Open'].values,
                              self.dataSubset['High'].values,
                              self.dataSubset['Low'].values,
                              self.dataSubset['Close'].values,
                              width=0.6,
                              colorup='g',
                              colordown='r',
                              alpha=1)

