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
from lib.assets import *

# StockData object which creates StockData data
class StockData:

        def __init__(self, stockCode, beginDate="1990-01-01", endDate=datetime.datetime.now().strftime("%Y-%m-%d")):
            self.assets      = []
            self.symbol      = "zł"
            self.data        = self.FetchData(stockCode,beginDate,endDate)
            self.volumeP, self.volumeN = self.InitVolume(self.data['Close'], self.data['Volume'])
            self.dataSubset  = SetReindex(self.data,beginDate,endDate)
            self.volumeSubsetP = SetReindex(self.volumeP,beginDate,endDate,False) 
            self.volumeSubsetN = SetReindex(self.volumeN,beginDate,endDate,False) 
            self.stockCode   = stockCode
            self.beginDate   = datetime.datetime.strptime(beginDate, "%Y-%m-%d")
            self.endDate     = datetime.datetime.strptime(endDate, "%Y-%m-%d")
            self.currentPrice= self.data['Close'][0]

        # Change volumeTotal to neg/pos value
        def InitVolume(self, price, volume):
            # Assert condition
            if (price.size != volume.size):
                return

            # Create volume objects
            volumePositive=pd.Series()
            volumeNegative=pd.Series()

            lastPrice=price.values[-1]
            # We start from end because data from Stooq is reversed
            for i in reversed(range(1,len(price.values))):
                # If price drop then volume wih minus value
                if (lastPrice > price.values[i]):
                    volumeNegative = volumeNegative.append(
                        pd.Series(volume.values[i],index=[volume.index[i]]))
                    volume.values[i]=-volume.values[i]
                else:
                    volumePositive = volumePositive.append(
                        pd.Series(volume.values[i],index=[volume.index[i]]))

                lastPrice=price.values[i]
            
            return volumePositive, volumeNegative

        # Returns current close price
        def GetCurrentPrice(self):
            return self.currentPrice

        # Returns current close price
        def GetStockCode(self):
            return self.stockCode

        # Set assets
        def SetAssets(self,stockAssets):
            self.assets =  stockAssets.GetAssetsForStockCode(self.stockCode)

        # SEt currency symbol
        def SetCurrencySymbol(self,symbol):
            self.symbol = symbol

        # Get DATA from URL
        # User pandas_reader.data.DataReader to load the desired data. As simple as that.
        def FetchData(self,stockCode,beginDate,endDate):
            receivedData = data.DataReader(stockCode, 'stooq', beginDate, endDate)

            if len(receivedData) == 0:
                print("No Stooq data for entry %s!" % (stockCode))
                sys.exit(1)

            return receivedData

        def Report(self,f,interval):
            if (interval=="daily"):
                f.write("    * **%2.2f**%% return rate for last 7 days.\n" % (GetReturnRates(self.Data['Close'], 1)))
            elif (interval=="weekly"):
                # Get last range date
                lastRangeDate  = self.endDate - datetime.timedelta(days=7)
                lastRangeDate  = lastRangeDate.strftime("%Y-%m-%d")
                # Get price, volume, subsets
                priceRange   = SetReindex(self.dataSubset,lastRangeDate,endDate)
                volumeRange  = SetReindex(self.dataSubset,lastRangeDate,endDate)
                # Calculate informations
                totalMaxPrice   = self.Data['High'].max()
                totalMinPrice   = self.Data['Low'].max()
                rangeMaxPrice   = priceRange.max()
                rangeMinPrice   = priceRange.max()

                currentPriceRelativeToMaxPrice = (self.currentPrice*100)/totalMaxPrice
                growthChance    = (totalMaxPrice*100)/self.currentPrice - 100
                lostChance      = 100-(totalMinPrice*100)/self.currentPrice

                # Write statistics
                f.write("# Report for %s.\n" % (self.stockCode))
                # weekly changes
                f.write("1. Price **%2.2f%s** - (**%u%%** of history, \
                        growth chance <span style='color:green'>+%u%%</span>, \
                        lost chance <span style='color:red'>-%u%%</span>)\n" %
                        (lastPrice,info.GetCurrency(),lastPriceAsPercentOfMaxPrice,growthChance,lostChance))
                # relative to historical changes
                f.write("1. Price **%2.2f%s** - (**%u%%** of history, \
                        growth chance <span style='color:green'>+%u%%</span>, \
                        lost chance <span style='color:red'>-%u%%</span>)\n" %
                        (lastPrice,info.GetCurrency(),lastPriceAsPercentOfMaxPrice,growthChance,lostChance))
                f.write("    * Current - **%2.2f%s - %2.2f%s**\n" % (minWindowPrice,info.GetCurrency(),maxWindowPrice,info.GetCurrency()))
                f.write("    * History - **%2.2f%s - %2.2f%s**\n" % (minPrice,info.GetCurrency(),maxPrice,info.GetCurrency()))
                f.write("    * Volume chng. med. **%2.2f**, max **+%2.2f**, min **%2.2f**\n" %
                        (volumeSubset.median(), volumeSubset.max(),volumeSubset.min()))
                f.write("\n")

        # Report current assets
        def ReportAssets(self,file):
            assets = self.GetAssets()
            if (len(assets)>0):
                file.write("## Assets\n\n")
                for asset in assets:
                    ReportAsset(file, asset, self.currentPrice, self.symbol)
                    
            return 0

        # Get named data
        def GetAllData(self,name):
            if (name in self.data.columns):
                return self.data[name]
            else:
                return CreateEmptyDataFrame()

        # Get named data
        def GetData(self,name):
            if (name in self.dataSubset.columns):
                return self.dataSubset[name]
            else:
                return CreateEmptyDataFrame()
        
        #Get all assets
        def GetAllAssets(self):
            return self.assets

        # Get subset assets
        def GetAssets(self):
            assets = []
            for asset in self.assets:
                dt = datetime.datetime.strptime(asset["date"], "%d-%M-%Y")
                if ((dt>=self.beginDate) and (dt<=self.endDate)):
                    assets.append(asset)
            return assets
        
        # True if volume exists
        def hasVolume(self):
            if ('Volume' in self.data.columns):
                return True
            return False
            

        # Plot all stock data
        def PlotAll(self):
            plt.plot(self.data['Close'].index, self.data['Close'], "#000000", label=self.stockCode)
            return 0

        # Plot stock data
        def Plot(self):
            plt.plot(self.dataSubset['Close'].index, self.dataSubset['Close'], "#000000", label=self.stockCode)
            return 0

        # Plot assets 
        def PlotAllAssets(self):
            for asset in self.assets:
                PlotAsset(plt, asset)
        
        # Plot assets 
        def PlotAssets(self):
            for asset in self.assets:
                dt = datetime.datetime.strptime(asset["date"], "%d-%M-%Y")
                if ((dt>=self.beginDate) and (dt<=self.endDate)):
                    PlotAsset(plt, asset)

        # Plot stock data
        def PlotAsBackground(self):
            plt.plot(self.dataSubset['Close'].index, self.dataSubset['Close'],"--", color="#777777", 
                     label=self.stockCode, linewidth=0.5)
            return 0
        
        # Plot volume as bars
        def PlotVolume(self, ax):
            ax2 = ax.twinx()
            ax2.bar(self.volumeSubsetP.index, self.volumeSubsetP, color="green",label="")
            ax2.bar(self.volumeSubsetN.index, self.volumeSubsetN,color="red",label="")
            ax2.tick_params(axis='y', labelcolor='tab:red')
        
        # Plot volume as bars
        def PlotVolumeAll(self, ax):
            ax2 = ax.twinx()
            ax2.bar(self.volumeP.index, self.volumeP, color="green",label="")
            ax2.bar(self.volumeN.index, self.volumeN, color="red",label="")
            ax2.tick_params(axis='y', labelcolor='tab:red')

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
                              width=0.8,
                              colorup='g',
                              colordown='r',
                              alpha=1)
            ax.autoscale_view()

