#!/usr/bin/python2.7
import matplotlib.pyplot as plt
import pandas as pd
import sys, argparse
import datetime
import numpy
import copy
from pandas_datareader import data
from numpy import NaN

reportFile="plots/report.md"

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

    return data

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

def FindPeaks(data, delta):
    maxs=copy.deepcopy(data)
    mins=copy.deepcopy(data)

    last_max = data.values[0]
    last_min = data.values[0]
    last_max_pos = 0
    last_min_pos = 0
    search_max = True

    # Find max/min in loop
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
                maxs.values[last_max_pos] = last_max
                last_max = current
                last_max_pos = i
                search_max = False
        else:
            # Save last min value
            if (current > (last_min+delta)):
                mins.values[last_min_pos] = last_min
                last_min = current
                last_min_pos = i
                search_max = True

        maxs.values[i] = NaN
        mins.values[i] = NaN

    return mins.dropna(), maxs.dropna()

# Save reports to file. Append text.
def ReportsSave(filepath):
    global outputFilename
    global args
    with open(filepath, 'a+') as f:
        f.write("# Report for %s.\n" % (args.stockCode))
        f.write("![Graph](%s)\n" % (outputFilename))
        f.close()
        

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


# Dates
currentDateTime = datetime.datetime.now()
## End date
end_date    =  currentDateTime.strftime("%Y-%m-%d")
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

plotsPath="plots/"
outputFilename=args.stockCode+"_"+end_date+".png"
outputFilepath=plotsPath+outputFilename
# #####################################################

# 1. Get DATA from URL
# #####################################################
panel_data  = GetData(args.stockCode, start_date, end_date)

# Get Close price and average
closePriceTotal  = panel_data['Close']
closePrice       = SetReindex(panel_data['Close'],start_date,end_date)
jaw, teeth, lips = SetWilliamsIndicator(closePrice)

# Find max and mins
PriceRange=closePrice.max()-closePrice.min()
print("ClosePrice Pk-Pk change %2.2f.\n" % (PriceRange))
mins, maxs       = FindPeaks(panel_data['Close'], PriceRange/10)
mins             = SetReindex(mins,start_date,end_date, False)
maxs             = SetReindex(maxs,start_date,end_date, False)
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

# Plot to file or show
if (args.plotToFile):
    plt.savefig(outputFilepath)
    print outputFilepath
else:
    plt.show()

if (args.reports):
    ReportsSave(reportFile)

