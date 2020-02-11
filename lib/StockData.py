'''
Created on 5 lut 2020

@author: spasz
'''
from pandas_datareader import data
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
# Need tot go to python 3
import sys
from mpl_finance import candlestick2_ohlc
from mpl_finance import candlestick_ohlc
from lib.DataOperations import *

# StockData object which creates StockData data
class StockData:

        def __init__(self, stockCode, beginDate, endDate):
            self.data = self.FetchData(stockCode,beginDate,endDate)
            self.dataSubset = SetReindex(self.data,self.beginDate,self.endDate)

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

        # Plot stock data
        def PlotAsBackground(self):
            plt.plot(self.dataSubset['Close'].index, self.dataSubset['Close'],"--", color="#777777", 
                     label=self.stockCode, linewidth=0.5)
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
            
        def PlotCandle2(self,ax):     
            # TODO fix missing values
            widthBackground= 1.5
            widthOpenClose = 1
            widthHighLow   = 0.2
            minHeight      = 0.1
            
            pricesup=self.dataSubset[self.dataSubset['Close'] > self.dataSubset['Open']]
            pricesdown=self.dataSubset[self.dataSubset['Close'] <= self.dataSubset['Open']]

            # line with close price
            plt.plot(self.dataSubset['Close'].index, self.dataSubset['Close'],"--", color="#777777", label=self.stockCode, linewidth=0.6)
            
            # Rising(Close>Open) - Green bars, 
            plt.bar(pricesup.index, pricesup['Close']-pricesup['Open'], widthOpenClose, bottom=pricesup['Open'], color='g', edgecolor="k")
            plt.bar(pricesup.index, pricesup['High']-pricesup['Low'],   widthHighLow,   bottom=pricesup['Low'],  color='g')

            # Falling(Close<=Open) - Red bars
            plt.bar(pricesdown.index, pricesdown['Open']-pricesdown['Close'], widthOpenClose, bottom=pricesdown['Close'],color='r', edgecolor="k")
            plt.bar(pricesdown.index, pricesdown['High']-pricesdown['Low'],   widthHighLow,   bottom=pricesdown['Low'],  color='r')

        # Plot stock data
        def PlotCandle(self,ax):
            quotes = self.dataSubset
            ax.xaxis_date()
            # ax.xaxis.set_minor_formatter(dayFormatter)
            candlestick_ohlc(ax, zip(mdates.date2num(quotes.index.to_pydatetime()),
                                     quotes['Open'], quotes['High'],
                                     quotes['Low'], quotes['Close']),
                              width=0.6,
                              colorup='g',
                              colordown='r',
                              alpha=1)
            ax.autoscale_view()

