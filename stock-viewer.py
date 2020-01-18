#!/usr/bin/python2.7
# append to a dataframe a.append(pd.DataFrame({'close':99.99},index=[datetime.datetime.now()])
import pandas as pd
import sys, argparse
import datetime
import numpy
import copy
from pandas_datareader import data
from numpy import NaN

# Get DATA from URL
# User pandas_reader.data.DataReader to load the desired data. As simple as that.
def GetData(code,begin,end):
    receivedData = data.DataReader(code, 'stooq', begin, end)

    if len(receivedData) == 0:
        print "No Stooq data for entry!"
        sys.exit(1)

    return receivedData

# Reindex weekly data
def SetReindex(data,start_date,end_date,fillna=True):
    # Getting all weekdays between 01/01/2000 and 12/31/2016
    all_weekdays = pd.date_range(start=start_date, end=end_date, freq='B')

    # How do we align the existing prices in adj_close with our new set of dates?
    # All we need to do is reindex close using all_weekdays as the new index
    data = data.reindex(all_weekdays)

    # Reindexing will insert missing values (NaN) for the dates that were not present
    # in the original set. To cope with this, we can fill the missing by replacing them
    # with the latest available price for each instrument.
    if (fillna == True):
        data = data.fillna(method='ffill')
        data = data.dropna()

    return data

# Reindex weekly data
def GetSubsetByDates(inputData,start_date,end_date,fillna=True):
    subset=pd.DataFrame()
    
    for i in range(len(inputData.values)):
        if ((inputData.index[i]>=start_date) and (inputData.index[i]<=end_date)):
            subset = subset.append(pd.DataFrame({'close':inputData.values[i]},
                                                index=[inputData.index[i]]))
    
    return subset

# Creation of moving average with specific window and shift
def SetMovingAverage(data, window, shiftPeriods = 0):
    average = data.rolling(window=int(window),min_periods=1).mean()
    average.shift(periods=shiftPeriods)

    return average

# Creation of Williams indicator for data
def SetWilliamsIndicator(price):
    jaw   = SetMovingAverage(price,  13, 8)
    teeth = SetMovingAverage(price,   8, 5)
    lips  = SetMovingAverage(price,   5, 3)

    return jaw, teeth, lips

def PlotWilliamsIndicator(jaw,teeth,lips):
    plt.plot(jaw.index, jaw, "#0000FF", label="Jaw", linewidth=1.0)
    plt.plot(teeth.index, teeth, "#FF0000", label="Teeth", linewidth=1.0)
    plt.plot(lips.index, lips, "#00FF00", label="Lips", linewidth=1.0)

## MACD
def SetMACD(price):
    exp1 = price.ewm(span=12, adjust=False).mean()
    exp2 = price.ewm(span=26, adjust=False).mean()
    
    macdLine = exp1-exp2
    signalLine = macdLine.ewm(span=9, adjust=False).mean()

    return macdLine, signalLine

def PlotMACD(macd,signal):
    #Create ZeroLine
    zeroLine=pd.DataFrame()
    zeroLine=zeroLine.append(pd.DataFrame({'close':0},
                                          index=[macd.index[0]]))
    zeroLine=zeroLine.append(pd.DataFrame({'close':0},
                                          index=[macd.index[-1]]))
    # Create Buy/Sell
    fromBottom,fromTop=FindIntersections(macd, signal)
    # Plot
    plt.plot(zeroLine.index,zeroLine,'--',color='#777777')
    plt.plot(macd.index, macd, label='AMD MACD', color = '#FF0000')
    plt.plot(signal.index, signal, label='Signal Line', color='#008800')
    plt.plot(fromBottom.index, fromBottom, 'ro', label='Buy')
    plt.plot(fromTop.index, fromTop, 'go', label='Sell')

# Calculate diff
def Diffrentiate(dataset):
    diff=numpy.diff(dataset).tolist()
    diff.append(0,0)
    return diff

# Change volumeTotal to neg/pos value
def SetVolumeWithTrend(price,volumeTotal):
    lastPrice=price.values[-1]

    # We start from end because data from Stooq is reversed
    for i in reversed(range(1,len(price.values))):
        # If price drop then volumeTotal wih minus value
        if (lastPrice > price.values[i]):
            volumeTotal.values[i]=-volumeTotal.values[i]

        lastPrice=price.values[i]


# Calculate OBV index thanks to the volumeTotal
def SetOBV(price,volumeTotal):
    lastOBV=0
    obvTotal=copy.deepcopy(volumeTotal)

    for i in reversed(range(len(volumeTotal.values))):
        lastOBV+=volumeTotal.values[i]
        obvTotal.values[i] = lastOBV

    return obvTotal

# Find zeroes and zero cuts
def FindZeroes(data):
    zeroes=pd.DataFrame()
    
    zero_cross = numpy.where(numpy.diff(numpy.sign(data.values)))[0]
    for i in range(len(zero_cross)):
        indexPos = zero_cross[i]
        zeroes = zeroes.append(pd.DataFrame({'close':data.values[indexPos]},index=[data.index[indexPos]]))
    
    return zeroes

# Find both signals intersections
def FindIntersections(x,y):
    diffrence=x.subtract(y)

    fromBottom=pd.DataFrame()
    fromTop=pd.DataFrame()
    
    zero_cross = numpy.where(numpy.diff(numpy.sign(diffrence.values)))[0]
    for i in range(len(zero_cross)):
        indexPos = zero_cross[i]
        if ((indexPos!=0) and (diffrence[indexPos-1] > 0)):
            fromTop = fromTop.append(pd.DataFrame({'close':x.values[indexPos]},index=[diffrence.index[indexPos]]))
        else:
            fromBottom = fromBottom.append(pd.DataFrame({'close':x.values[indexPos]},index=[diffrence.index[indexPos]]))
    
    return fromBottom, fromTop


def FindPeaks(data, delta):
    maxs=pd.DataFrame()
    mins=pd.DataFrame()

    # Loop max iterations
    MaxLoopIteration=10
    # Loop iteration
    loopIteration = 0

    while ((loopIteration<MaxLoopIteration) and (maxs.empty or mins.empty)):
        # Algorithm data
        last_max = data.values[0]
        last_min = data.values[0]
        last_max_pos = 0
        last_min_pos = 0
        search_max = True
        
        # Algorithm loop - Find max/min in loop
        for i in range(len(data.values)):
            current = data.values[i]
            # Save last max
            if (current > last_max):
                last_max = current
                last_max_pos = i
            # Save last min
            if (current < last_min):
                last_min = current
                last_min_pos = i

            if (search_max == True):
                # Save last max value
                if (current < (last_max-delta)):
                    maxs = maxs.append(pd.DataFrame({'close':last_max},index=[data.index[last_max_pos]]))
                    #maxs.values[last_max_pos] = last_max
                    last_max = current
                    last_max_pos = i
                    search_max = False
            else:
                # Save last min value
                if (current > (last_min+delta)):
                    mins = mins.append(pd.DataFrame({'close':last_min},index=[data.index[last_min_pos]]))
                    last_min = current
                    last_min_pos = i
                    search_max = True
        # Adjust delta for another loop search if min/max not found
        delta = (delta*80)/100
        loopIteration+=1

    return mins, maxs

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
        f.write("1. Price **%2.2f**%s - (%u%% of history, growth chance +%u%%, lost chance -%u%%)\n" % 
                (lastPrice,currency,lastPriceAsPercentOfMaxPrice,growthChance,lostChance))
        f.write("    * Current -  %2.2f%s - %2.2f%s\n" % (minWindowPrice,currency,maxWindowPrice,currency))
        f.write("    * History - %2.2f%s - %2.2f%s\n" % (minPrice,currency,maxPrice,currency))
        f.write("    * Volume chng. (2 weeks) - med. %2.2f, max +%2.2f, min %2.2f\n" % 
                (volumeSubset.median(), volumeSubset.max(),volumeSubset.min()))
        # Insert all created graphs
        f.write("\n")
        for path in graphsCreated:
            f.write("![Graph](%s)\n\n" % (path))
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
panel_data  = GetData(args.stockCode, start_date, end_date)

# Get Close price and average
closePriceTotal  = panel_data['Close']
closePrice       = SetReindex(panel_data['Close'],start_date,end_date)
jaw, teeth, lips = SetWilliamsIndicator(closePrice)
macdLine, macdSignal = SetMACD(closePrice)

# Get STD deviation
stdTotal = closePriceTotal.rolling(window=int(5),min_periods=1).std()

# Find max and mins
PriceRange=closePrice.max()-closePrice.min()
print("ClosePrice Pk-Pk change %2.2f.\n" % (PriceRange))
mins, maxs       = FindPeaks(closePrice, PriceRange/10)

# Volume
SetVolumeWithTrend(panel_data['Close'], panel_data['Volume'])
obvTotal    = SetOBV(panel_data['Close'], panel_data['Volume'])
volumeTotal = panel_data['Volume']
volume      = SetReindex(panel_data['Volume'],start_date,end_date)
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
plt.ylabel('Price (zl)')
plt.grid()
plt.title("Cena")
plt.legend()

# Total close price
plot2=plt.subplot(222)
plt.plot(closePriceTotal.index, closePriceTotal, "#000000", label=args.stockCode)
plt.plot(closePrice.index, closePrice, 'r', label="")
plt.ylabel('Price (zl)')
plt.grid()
plt.legend()

# Volume
# #####################################################
plot3=plt.subplot(223, sharex=plot1)
plt.plot(obv.index, obv, label="Volume")
plt.ylabel('Volume')
plt.grid()
plt.title("Vol. i OBV")
plt.legend()

# OBV
plot4=plt.subplot(224, sharex=plot2)
plt.plot(obvTotal.index, obvTotal, label="OBV")
plt.plot(obv.index, obv, 'r', label="")
plt.ylabel('OBV')
plt.grid()
plt.legend()

# Plot to file
if (args.plotToFile):
    PlotSave(fig)

### Show Standard deviatio
fig = plt.figure(figsize=(16.0, 9.0))

# Total close price
plot5=plt.subplot(211)
plt.plot(closePrice.index, closePrice, "#000000", label=args.stockCode)
plt.ylabel('Price (zl)')
plt.grid()
plt.legend()

# Total close price
plot6=plt.subplot(212, sharex=plot5)
PlotMACD(macdLine, macdSignal)
# plt.plot(stdTotal.index, stdTotal, "#000000", label=args.stockCode)
plt.ylabel('Price (zl)')
plt.grid()
plt.legend()

# Plot to file or show
if (args.plotToFile):
    PlotSave(fig)

# Create reports
if (args.reports):
    ReportSave(reportFile)
    
# Show all plots
if (not args.plotToFile):
    plt.show()

