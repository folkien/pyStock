#!/usr/bin/python2.7
import matplotlib.pyplot as plt
import pandas as pd
import sys, argparse
import datetime
import numpy
from pandas_datareader import data


# Get DATA from URL
# User pandas_reader.data.DataReader to load the desired data. As simple as that.
def GetData(code,begin,end):
    receivedData = data.DataReader(code, 'stooq', begin, end)

    if len(receivedData) == 0:
        print "No Stooq data for entry!"
        sys.exit(1)

    return receivedData

# Reindex weekly data
def SetReindex(data,start_date,end_date):
    # Getting all weekdays between 01/01/2000 and 12/31/2016
    all_weekdays = pd.date_range(start=start_date, end=end_date, freq='B')

    # How do we align the existing prices in adj_close with our new set of dates?
    # All we need to do is reindex close using all_weekdays as the new index
    data = data.reindex(all_weekdays)

    # Reindexing will insert missing values (NaN) for the dates that were not present
    # in the original set. To cope with this, we can fill the missing by replacing them
    # with the latest available price for each instrument.
    data = data.fillna(method='ffill')

    return data

def SetAverage(data, averageDays):
    # Get the MSFT timeseries. This now returns a Pandas Series object indexed by date.
    msft = data

    # Calculate the days moving averages
    average = msft.rolling(window=int(averageDays),min_periods=1).mean()

    return average

# Calculate diff
def Diffrentiate(dataset):
    diff=numpy.diff(dataset).tolist()
    diff.append(0,0)
    return diff

# Calculate OBV index thanks to the volume
def SetOBV(price,volume):
    lastOBV=volume.values[1]
    lastPrice=price.values[1]
    obv=volume

    for i in range(1, len(price.values)):
        # If price drop then volume wih minus value
        if (lastPrice > price.values[i]):
            lastOBV-=volume.values[i]
        # If price rise then volume with positiive
        else:
            lastOBV+=volume.values[i]

        obv.values[i] = lastOBV
        lastPrice=price.values[i]

    return obv



# Arguments and config
# #####################################################
parser = argparse.ArgumentParser()
parser.add_argument("-n", "--stockCode", type=str, required=True, help="Stock name code")
parser.add_argument("-d", "--beginDate", type=str, required=False, help="Begin date")
parser.add_argument("-a", "--averageDays", type=int, required=False, help="Day to calc mean")
parser.add_argument("-Y", "--lastYear", action='store_true', required=False, help="Last Year")
parser.add_argument("-M", "--lastMonth", action='store_true', required=False, help="Last Month")
parser.add_argument("-W", "--lastWeek", action='store_true', required=False, help="Last Week")
parser.add_argument("-g", "--plotToFile", action='store_true', required=False, help="Plot to file")
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
if (args.lastMonth):
    tmpDate = datetime.datetime.now() - datetime.timedelta(days=30)
    start_date  =  tmpDate.strftime("%Y-%m-%d")
# Check last Week
if (args.lastWeek):
    tmpDate = datetime.datetime.now() - datetime.timedelta(days=7)
    start_date  =  tmpDate.strftime("%Y-%m-%d")

# #####################################################

# 1. Get DATA from URL
# #####################################################
panel_data  = GetData(args.stockCode, start_date, end_date)

# Get Close price and average
closePrice     = SetReindex(panel_data['Close'],start_date,end_date)
avgClosePrice  = SetAverage(closePrice,args.averageDays)
# Volume
volume = SetReindex(panel_data['Volume'],start_date,end_date)
obv = SetOBV(panel_data['Close'], panel_data['Volume'])
obv= SetReindex(obv,start_date,end_date)
print obv


# 3. Plot data
# #####################################################33
# Price
plot1=plt.subplot(211)
plt.plot(closePrice.index, closePrice, label=args.stockCode)
plt.plot(avgClosePrice.index, avgClosePrice, label=str(args.averageDays)+' days mean')
plt.xlabel('Date')
plt.ylabel('Closing price (zl)')
plt.grid()
plt.legend()

# Volume
plot3=plt.subplot(212, sharex=plot1)
plt.plot(volume.index, obv, label="OBV")
plt.plot(volume.index, volume, label="Volume")
plt.xlabel('Date')
plt.ylabel('Jednostki')
plt.grid()
plt.legend()

# Plot to file or show
if (args.plotToFile):
    outputFilename="plots/"+args.stockCode+"."+end_date+"plot.png"
    plt.savefig(outputFilename)
    print outputFilename
else:
    plt.show()

