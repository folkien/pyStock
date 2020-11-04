'''
Created on 5 lut 2020

@author: spasz
'''
import matplotlib.pyplot as plt
import sys
import datetime
import pandas as pd
import numpy
from helpers.DataOperations import SetReindex, CreateHorizontalLine, CreateVerticalLine
from mplfinance import plot as mpfplot
from core.database import StockDatabase
from helpers.data import toNumIndex, GenerateOHLCSawFunction, GenerateOHLCTrapezeFunction
from pandas_datareader import data
from core.assets import ReportAsset, PlotAsset

# StockData object which creates StockData data


class StockData():

    def __init__(self, stockCode, beginDate='1990-01-01', endDate=datetime.datetime.now().strftime('%Y-%m-%d')):
        self.specialStockCodes = ['#saw', '#trapeze']
        self.assets = []
        self.symbol = 'zł'
        self.stockCode = stockCode
        # Data fetch/create
        self.cache = StockDatabase()
        self.data = self.FetchData(stockCode, beginDate, endDate)
        self.currentPrice = self.data['Close'][0]
        # Typical price create
        self.data['Typical'] = (
            self.data['Close'] + self.data['High'] + self.data['Low']) / 3
        # Volumen parse/create if exists
        if (self.hasVolume()):
            self.data['VolumeP'], self.data['VolumeN'] = self.InitVolume(
                self.data['Close'], self.data['Volume'])
            # OBV create
            self.data['OBV'] = self.data.loc[::-1, 'Volume'].cumsum()[::-1]
            # Money on market create
            self.data['Money'] = self.data['Typical'] * self.data['Volume']
            self.data['Money'] = self.data.loc[::-1, 'Money'].cumsum()[::-1]

        # Create subset of data
        self.dataSubset = SetReindex(self.data, beginDate, endDate)
        # Change dates
        self.beginDate = datetime.datetime.strptime(beginDate, '%Y-%m-%d')
        self.endDate = datetime.datetime.strptime(endDate, '%Y-%m-%d')
        # Create place for indicators
        self.indicators = {}

    # Change volumeTotal to neg/pos value

    @staticmethod
    def InitVolume(price, volume):
        # Assert condition
        if (price.size != volume.size):
            return

        # Create volume objects
        volumePositive = pd.Series()
        volumeNegative = pd.Series()

        # Data starts from oldest to youngest
        for i in (range(0, len(price.values) - 1)):

            # If price dropped, then volume - sign
            if (price.values[i] < price.values[i + 1]):
                volumeNegative = volumeNegative.append(
                    pd.Series(volume.values[i], index=[volume.index[i]]))
                volume.values[i] = -volume.values[i]
            # If price rised, then volume + sign
            else:
                volumePositive = volumePositive.append(
                    pd.Series(volume.values[i], index=[volume.index[i]]))

        return volumePositive, volumeNegative

    # Returns value (float)
    def GetValue(self, column='Close', days=0):
        if (column is self.data.columns) and (days < len(self.data.index)):
            return self.data[column][days]
        return 0.0

    # Returns current close price
    def GetReturnRates(self, days=1, column='Close'):
        if (column is self.data.columns) and (days < len(self.data.index)):
            startPrice = self.data[column][days]
            endPrice = self.data[column][0]
            return ((endPrice - startPrice) * 100) / startPrice
        return 0

    # Returns current close price
    def GetStockCode(self):
        return self.stockCode

    # Set assets
    def SetAssets(self, stockAssets):
        self.assets = stockAssets.GetAssetsForStockCode(self.stockCode)

    # SEt currency symbol
    def SetCurrencySymbol(self, symbol):
        self.symbol = symbol

    # Add indicator
    def AddIndicator(self, indicator):
        if (indicator.GetType() in self.indicators):
            self.indicators[indicator.GetType()].append(indicator)
        else:
            self.indicators[indicator.GetType()] = [indicator]

    # Get data from URL/database
    def FetchData(self, stockCode, beginDate, endDate):
        rxData = ''

        # Check special codes
        if (self.__isSpecialStockCode(stockCode)):
            rxData = self.__getSpecialStock(stockCode, beginDate, endDate)

        # Read from database if exists today file
        if (len(rxData) == 0) and (self.cache.IsOfTodaySession(stockCode) == True):
            print('Restoring today cache...')
            rxData = self.cache.Load(stockCode)

        # User pandas_reader.data.DataReader to load the desired data. As simple as that.
        if (len(rxData) == 0):
            print('Fetching `%s` from stooq.' % (stockCode))
            rxData = data.DataReader(stockCode, 'stooq', beginDate, endDate)

        # Use old data if exists
        if (len(rxData) == 0) and (self.cache.IsExists(stockCode) == True):
            print('Restoring old data...')
            rxData = self.cache.Load(stockCode)

        # No data at all
        if (len(rxData) == 0):
            print("'No Stooq'/'Empty Database' data for entry %s!" % (stockCode))
            sys.exit(1)

        # If data is fetched well then store it inside database
        self.cache.Save(stockCode, rxData)

        return rxData

    def __isSpecialStockCode(self, stockCode):
        ''' Checks special code. '''
        return (stockCode in self.specialStockCodes)

    @staticmethod
    def __getSpecialStock(stockCode, beginDate, endDate):
        ''' Checks special code. '''
        if (stockCode == '#saw'):
            return GenerateOHLCSawFunction(pd.bdate_range(beginDate, endDate))
        if (stockCode == '#trapeze'):
            return GenerateOHLCTrapezeFunction(pd.bdate_range(beginDate, endDate))
        return None

    @staticmethod
    def Colorify(value):
        if type(value) in (float, numpy.float64):
            if (value >= 0):
                return "<span style='color:green'>**+%2.2f**</span>" % (value)
            return "<span style='color:red'>**%2.2f**</span>" % (value)
        elif type(value) in (int, numpy.int64):
            if (value >= 0):
                return "<span style='color:green'>**+%u**</span>" % (value)
            return "<span style='color:red'>**%u**</span>" % (value)

    @staticmethod
    def FormatNumInt(value):
        if (value >= 1000000):
            return ('%2.3fmln' % (value/1000000))
        if (value >= 1000):
            return ('%2.3fk' % (value/1000))
        return ('%u' % value)

    @staticmethod
    def FormatUnifiedIndicator(value, inverted=False):
        if ((inverted == True) and (value < 0)) or ((inverted == False) and (value > 0)):
            return "<div style='border:1px solid black;float:left;'><div style='width:100px;height:20px;float:left'></div><div style='background:black;width:5px;height:20px;float:left'></div><div style='background:green;width:%upx;height:20px;float:left'></div><div style='width:%upx;height:20px;float:left'></div></div><div style='clear:both'></div>" % (abs(value), 100-abs(value))
        return "<div style='border:1px solid black;float:left;'><div style='width:%upx;height:20px;float:left'></div><div style='background:red;width:%upx;height:20px;float:left'></div><div style='background:black;width:5px;height:20px;float:left'></div><div style='width:100px;height:20px;float:left'></div></div><div style='clear:both'></div>" % (100-abs(value), abs(value))

    def Report(self, f, interval):
        # select number of days in interval
        if (interval == 'daily'):
            period = 1
        elif(interval == 'weekly'):
            period = 7
        else:
            period = 28

        print('Report %s creation...' % interval)
        f.write('# %s report for %u days.\n' % (self.stockCode, period))
        # Price
        f.write('* %s%% **%2.2f%s** [%2.2f%s - %2.2f%s]\n' %
                (self.Colorify(self.GetReturnRates(period)),
                 self.GetValue(), self.symbol,
                 self.GetValue('High'), self.symbol,
                 self.GetValue('Low'), self.symbol
                 ))
        # Volumen
        if (self.hasVolume()):
            volumenChange = self.data['Volume'][0]
            f.write('* %sj vol.\n' % (self.Colorify(volumenChange)))

            # OBV
            obvReturnRate = self.GetReturnRates(period, 'OBV')
            f.write('* %s%% %s OBV\n' %
                    (self.Colorify(obvReturnRate),
                     self.FormatNumInt(self.GetValue('OBV'))
                     ))
            # Money on the market
            moneyReturnRate = self.GetReturnRates(period, 'Money')
            f.write('* %s%% %s %s\n\n' %
                    (self.Colorify(moneyReturnRate),
                     self.FormatNumInt(self.GetValue('Money')),
                     self.symbol)
                    )
        f.write('\n')

        # Stock return rates. Days no has to be *7.
        f.write('## Return rates.\nRevenues of close price across time.\n\n')
        f.write('* %s %s%% from **%2.2f%s** \n' %
                ('day',
                 self.Colorify(self.GetReturnRates(days=1)),
                 self.GetValue(days=1), self.symbol,
                 ))
        f.write('* %s %s%% from **%2.2f%s** \n' %
                ('week',
                 self.Colorify(self.GetReturnRates(days=7)),
                 self.GetValue(days=7), self.symbol,
                 ))
        f.write('* %s %s%% from **%2.2f%s** \n' %
                ('month',
                 self.Colorify(self.GetReturnRates(days=28)),
                 self.GetValue(days=28), self.symbol,
                 ))
        f.write('* %s %s%% from **%2.2f%s** \n' %
                ('year',
                 self.Colorify(self.GetReturnRates(days=371)),
                 self.GetValue(days=371), self.symbol,
                 ))
        f.write('\n')

        # Stock momentum indicators
        if ('momentum' in self.indicators):
            f.write(
                '## Momentum indicators.\nIf price is oversold or overbought. Range -100 to 100.\n\n')
            for indicator in self.indicators['momentum']:
                f.write('* %s %u %s.\n' % (indicator.GetName(),
                                           indicator.GetUnifiedValue(),
                                           self.FormatUnifiedIndicator(indicator.GetUnifiedValue(), True)))

            f.write('\n')

        # Stock trend indicators
        if ('trend' in self.indicators):
            f.write(
                '## Trend indicators.\nIf trend is rising or falling, strong or weak.\n\n')
            for indicator in self.indicators['trend']:
                f.write('* %s %u %s.\n' % (indicator.GetName(), indicator.GetUnifiedValue(),
                                           self.FormatUnifiedIndicator(indicator.GetUnifiedValue())))

            f.write('\n')

    # Report current assets
    def ReportAssets(self, file):
        assets = self.GetAssets()
        if (len(assets) > 0):
            file.write('## Assets\n\n')
            for asset in assets:
                ReportAsset(file, asset, self.currentPrice, self.symbol)
            file.write('\n')

        return 0

    # Get named data
    def GetAllData(self, name):
        if (name in self.data.columns):
            return self.data[name]
        return pd.DataFrame()

    # Get named data
    def GetData(self, name=None):
        if (name in self.dataSubset.columns):
            return self.dataSubset[name]
        return self.dataSubset

    # Get all assets
    def GetAllAssets(self):
        return self.assets

    # Get subset assets
    def GetAssets(self):
        assets = []
        for asset in self.assets:
            dt = datetime.datetime.strptime(asset['date'], '%d-%M-%Y')
            if ((dt >= self.beginDate) and (dt <= self.endDate)):
                assets.append(asset)
        return assets

    # True if volume exists
    def hasVolume(self):
        if ('Volume' in self.data.columns):
            return True
        return False

    # Plot all stock data

    def PlotAll(self, ax):
        mpfplot(self.dataSubset, ax=ax, type='line', linecolor='#000000')
        self.PlotPriceLine(plt.gca(), self.data['Close'])
        return 0

    # Plot stock data
    def Plot(self):
        mpfplot(self.dataSubset['Close'].index,
                self.dataSubset['Close'], '#000000', label=self.stockCode)
        self.PlotPriceLine(plt.gca(), self.dataSubset['Close'])

    # Plot assets
    def PlotAllAssets(self, ax):
        for asset in self.assets:
            dt = datetime.datetime.strptime(asset['date'], '%d-%M-%Y')
            if ((dt >= self.beginDate) and (dt <= self.endDate)):
                xpos = self.data['Close'].index.get_loc(asset['date'])
                PlotAsset(ax, xpos, asset)

    # Plot assets
    def PlotAssets(self):
        for asset in self.assets:
            dt = datetime.datetime.strptime(asset['date'], '%d-%M-%Y')
            if ((dt >= self.beginDate) and (dt <= self.endDate)):
                xpos = self.dataSubset['Close'].index.get_loc(asset['date'])
                PlotAsset(plt, xpos, asset)

    # Plot stock data
    def PlotAsBackground(self):
        plt.plot(self.dataSubset['Close'].index, self.dataSubset['Close'], '--', color='#777777',
                 label=self.stockCode, linewidth=0.5)
        return 0

    # Plot volume as bars
    def PlotVolume(self, ax):
        ax2 = ax.twinx()
        ax2.bar(self.dataSubset['VolumeP'].index,
                self.dataSubset['VolumeP'], color='green', label='')
        ax2.bar(self.dataSubset['VolumeN'].index,
                self.dataSubset['VolumeN'], color='red', label='')
        ax2.tick_params(axis='y', labelcolor='tab:red')

    # Plot volume as bars
    def PlotVolumeAll(self, ax):
        ax2 = ax.twinx()
        ax2.bar(self.data['VolumeP'].index,
                self.data['VolumeP'], color='green', label='')
        ax2.bar(self.data['VolumeN'].index,
                self.data['VolumeN'], color='red', label='')
        ax2.tick_params(axis='y', labelcolor='tab:red')

    # Plot money on the market
    def PlotMoneyOnMarket(self, ax):
        ax.plot(toNumIndex(self.dataSubset.index, self.dataSubset['Money']), self.dataSubset['Money'], '-.',
                label='Money on market', linewidth=1.2, color='#FF0000')

    # Plot money on the market
    def PlotMoneyOnMarketAll(self, ax):
        ax.plot(toNumIndex(self.dataSubset.index, self.data['Money']), self.data['Money'], '-.',
                label='Money on market', linewidth=1.2, color='#FF0000')

    # Plot stock data
    def PlotCandle(self, ax):
        quotes = self.dataSubset
        mpfplot(quotes, type='candle', ax=ax, style='yahoo')
        self.PlotPriceLine(ax, self.dataSubset['Close'])

    @staticmethod
    def PlotPriceLine(ax, price):
        '''
         price - dataframe/series with price values and indexes,
        '''
        pos = price.index.get_loc(price.index.max())
        # Draw line
        priceLine = CreateHorizontalLine(
            price.index, price.values[pos], price.values[pos])
        xindex = toNumIndex(price.index, priceLine)
        ax.plot(xindex, priceLine, '--', color='#000000',
                linewidth=1.0, alpha=0.6)
        # Draw annotation
        bbox_props = dict(boxstyle='larrow,pad=0.3',
                          fc='w', ec='0.5', alpha=0.6)
        ax.annotate('%2.2f' % price.values[pos], xy=(pos, price.values[pos]),
                    xytext=(15, -3), textcoords='offset points', bbox=bbox_props)

    def AddReturnRatesAxle(self, ax, data=None):
        '''
         Add another axle with return rates based on dataframe 'data'.
        '''
        # Checks
        if (data is None):
            data = self.dataSubset

        # Data creation
        price = data['Close'].values[-1]
        index = data['Close'].index[-1]
        maxPrice = data['High'].max()
        maxRRate = ((maxPrice-price)*100/price)
        minPrice = data['Low'].min()
        minRRate = -((price-minPrice)*100/price)
        data = CreateVerticalLine(index, minRRate, maxRRate)
        # Data display
        ax2 = ax.twinx()
        ax2.plot(range(data.shape[0]), data, '_',
                 color='#000000', linewidth=1.0, alpha=0.6)
        ax2.tick_params(axis='y', labelcolor='tab:red')
        plt.ylabel('%', color='red')
