#!/usr/bin/python2.7
# append to a dataframe a.append(pd.DataFrame({'close':99.99},index=[datetime.datetime.now()])
import pandas as pd
import sys, os, argparse
import datetime
import numpy
import copy
from pandas_datareader import data
from numpy import NaN
from lib.CountryInfo import CountryInfo
from lib.DataOperations import *
from lib.Stock import *

def PlotSave(fig):
    global graphsCreated
    filePath=outputFilepath+str(fig.number)+outputExtension
    plt.figure(fig.number)
    plt.savefig(filePath)
    graphsCreated.append(filePath)
    print filePath 

# Save reports to file. Append text.
def ReportSave(filepath):
    global outputFilename
    global args
    global closePrice
    global closePriceTotal
    global volume
    global volumeTotal
    
    lastPrice      = closePriceTotal.values[0]
    maxPrice       = closePriceTotal.values.max()
    minPrice       = closePriceTotal.values.min()
    maxWindowPrice = closePrice.values.max()
    minWindowPrice = closePrice.values.min()
    lastPriceAsPercentOfMaxPrice = (lastPrice*100)/maxPrice
    growthChance    = (maxPrice*100)/lastPrice - 100
    lostChance      = 100-(minPrice*100)/lastPrice
    # Volume statistics
    volumeSubset    = GetSubsetByDates(volume, last2Weeks, today)
    volumeAvgChange = volumeSubset.median()

    with open(filepath, 'a+') as f:
        # Write statistics
        f.write("# Report for %s.\n" % (args.stockCode))
        f.write("1. Price **%2.2f%s** - (**%u%%** of history, \
                 growth chance <span style='color:green'>+%u%%</span>, \
                 lost chance <span style='color:red'>-%u%%</span>)\n" % 
                (lastPrice,currency,lastPriceAsPercentOfMaxPrice,growthChance,lostChance))
        f.write("    * Current - **%2.2f%s - %2.2f%s**\n" % (minWindowPrice,currency,maxWindowPrice,currency))
        f.write("    * History - **%2.2f%s - %2.2f%s**\n" % (minPrice,currency,maxPrice,currency))
        f.write("    * Volume chng. (2 weeks) - med. **%2.2f**, max **+%2.2f**, min **%2.2f**\n" % 
                (volumeSubset.median(), volumeSubset.max(),volumeSubset.min()))
        # Insert all created graphs
        f.write("\n")
        for path in graphsCreated:
            f.write("![Graph](%s)\n\n" % (os.path.basename(path)))
        f.write("\n")
        # Close file
        f.close()

# Const objects
# #####################################################
reportFile="plots/report.md"
currency="zl"
plotsPath="plots/"
outputExtension=".png"

# Arguments and config
# #####################################################
parser = argparse.ArgumentParser()
parser.add_argument("-n", "--stockCode", type=str, required=True, help="Stock name code")
parser.add_argument("-d", "--beginDate", type=str, required=False, help="Begin date")
parser.add_argument("-a", "--averageDays", type=int, required=False, help="Day to calc mean")
parser.add_argument("-Y", "--lastYear", action='store_true', required=False, help="Last Year")
parser.add_argument("-6M", "--last6Months", action='store_true', required=False, help="Last 6 Months")
parser.add_argument("-M", "--lastMonth", action='store_true', required=False, help="Last Month")
parser.add_argument("-W", "--lastWeek", action='store_true', required=False, help="Last Week")
parser.add_argument("-g", "--plotToFile", action='store_true', required=False, help="Plot to file")
parser.add_argument("-r", "--reports", action='store_true', required=False, help="Generate extra reports")
args = parser.parse_args()

#Assert
if (not args.stockCode):
    print "No stockCode!"
    sys.exit(1)

# Create Country Info
info = CountryInfo(args.stockCode)

if (not args.averageDays):
    args.averageDays=30

# Use non-interactive backend when plot to file used
if (args.plotToFile):
    import matplotlib
    matplotlib.use('Agg')
import matplotlib.pyplot as plt


# Dates
today       = datetime.datetime.now()
lastYear    = datetime.datetime.now() - datetime.timedelta(days=365)
last6Months = datetime.datetime.now() - datetime.timedelta(days=30*6)
lastMonth   = datetime.datetime.now() - datetime.timedelta(days=30)
last2Weeks  = datetime.datetime.now() - datetime.timedelta(days=14)
lastWeek    = datetime.datetime.now() - datetime.timedelta(days=7)
## End date
end_date    = today.strftime("%Y-%m-%d")
## Start date
if (args.beginDate):
    start_date  = args.beginDate
else:
    start_date  = '2010-01-01'
# Check last year
if (args.lastYear):
    tmpDate = datetime.datetime.now() - datetime.timedelta(days=365)
    start_date  =  tmpDate.strftime("%Y-%m-%d")
# Check last month
if (args.last6Months):
    tmpDate = datetime.datetime.now() - datetime.timedelta(days=30*6)
    start_date  =  tmpDate.strftime("%Y-%m-%d")
# Check last month
if (args.lastMonth):
    tmpDate = datetime.datetime.now() - datetime.timedelta(days=30)
    start_date  =  tmpDate.strftime("%Y-%m-%d")
# Check last Week
if (args.lastWeek):
    tmpDate = datetime.datetime.now() - datetime.timedelta(days=7)
    start_date  =  tmpDate.strftime("%Y-%m-%d")


# Dynamic variables
# #####################################################
outputFilename=args.stockCode+"_"+end_date+"_"
outputFilepath=plotsPath+outputFilename
graphsCreated=[]

# 1. Get DATA from URL
# #####################################################
stockData   = StockData(args.stockCode, start_date, end_date)

# Get Close price and average
closePriceTotal  = stockData.GetAllData('Close')
closePrice       = stockData.GetData('Close')
jaw, teeth, lips = SetWilliamsIndicator(closePrice)
macd             = CreateMACD(closePrice)
rsi              = CreateRSI(closePrice)

# Get STD deviation
stdTotal = closePriceTotal.rolling(window=int(5),min_periods=1).std()

# Find max and mins
PriceRange=closePrice.max()-closePrice.min()
print("ClosePrice Pk-Pk change %2.2f.\n" % (PriceRange))
mins, maxs       = FindPeaks(closePrice, PriceRange/10)

# Volume
SetVolumeWithTrend(stockData.GetAllData('Close'), stockData.GetAllData('Volume'))
obvTotal    = SetOBV(stockData.GetAllData('Close'), stockData.GetAllData('Volume'))
volumeTotal = stockData.GetAllData('Volume')
volume      = stockData.GetData('Volume')
obv         = SetReindex(obvTotal,start_date,end_date)


# 3. Plot data
# #####################################################
fig = plt.figure(figsize=(16.0, 9.0))


# Price
# #####################################################
plot1=plt.subplot(221)
plt.plot(closePrice.index, closePrice, "#000000", label=args.stockCode)
plt.plot(maxs.index,maxs,'go', label="Maxs")
plt.plot(mins.index,mins,'ro', label="Mins")
PlotWilliamsIndicator(jaw, teeth, lips)
plt.ylabel('Price (%s)' % (info.GetCurrency()))
plt.grid()
plt.title("Price and Volume in period")
plt.legend(loc='upper left')

# Total close price
plot2=plt.subplot(222)
plt.plot(closePriceTotal.index, closePriceTotal, "#000000", label=args.stockCode)
plt.plot(closePrice.index, closePrice, 'r', label="")
plt.ylabel('Price (%s)' % (info.GetCurrency()))
plt.grid()
plt.title("Price and Volume - alltime")
plt.legend(loc='upper left')

# Volume
# #####################################################
plot3=plt.subplot(223, sharex=plot1)
plt.plot(obv.index, obv, label="Volume")
plt.ylabel('Volume')
plt.grid()
plt.title("Vol. i OBV")
plt.legend(loc='upper left')

# OBV
plot4=plt.subplot(224, sharex=plot2)
plt.plot(obvTotal.index, obvTotal, label="OBV")
plt.plot(obv.index, obv, 'r', label="")
plt.ylabel('OBV')
plt.grid()
plt.legend(loc='upper left')

# Plot to file
if (args.plotToFile):
    PlotSave(fig)

### Show Standard deviatio
fig = plt.figure(figsize=(16.0, 9.0))

# Total close price
plot5=plt.subplot(411)
stockData.Plot()
stockData.PlotCandle()
plt.ylabel('Price (%s)' % (info.GetCurrency()))
plt.grid()
plt.title("Price and oscillators - period")
plt.legend(loc='upper left')

# MACD
plot6=plt.subplot(412, sharex=plot5)
macd.Plot()
plt.ylabel('Value')
plt.grid()
plt.legend(loc='upper left')

# MACD hist
plot7=plt.subplot(413, sharex=plot5)
macd.Histogram()
plt.ylabel('Value')
plt.grid()
plt.legend(loc='upper left')

# RSI
plot8=plt.subplot(414, sharex=plot5)
PlotRSI(rsi)
plt.ylabel('RSI')
plt.grid()
plt.legend(loc='upper left')

# Plot to file or show
if (args.plotToFile):
    PlotSave(fig)

# Create reports
if (args.reports):
    ReportSave(reportFile)
    
# Show all plots
if (not args.plotToFile):
    plt.show()

