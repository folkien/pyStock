#!/usr/bin/python2.7
import matplotlib.pyplot as plt
import pandas as pd
import sys, argparse
import datetime
from pandas_datareader import data

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

# User pandas_reader.data.DataReader to load the desired data. As simple as that.
panel_data = data.DataReader(args.stockCode, 'stooq', start_date, end_date)

if len(panel_data) == 0:
    print "No Stooq data for entry!"
    sys.exit(1)

# Getting just the adjusted closing prices. This will return a Pandas DataFrame
# The index in this DataFrame is the major index of the panel_data.
close = panel_data['Close']

# Getting all weekdays between 01/01/2000 and 12/31/2016
all_weekdays = pd.date_range(start=start_date, end=end_date, freq='B')

# How do we align the existing prices in adj_close with our new set of dates?
# All we need to do is reindex close using all_weekdays as the new index
close = close.reindex(all_weekdays)

# Reindexing will insert missing values (NaN) for the dates that were not present
# in the original set. To cope with this, we can fill the missing by replacing them
# with the latest available price for each instrument.
close = close.fillna(method='ffill')

# Get the MSFT timeseries. This now returns a Pandas Series object indexed by date.
msft = close

# Calculate the days moving averages
average = msft.rolling(window=int(args.averageDays),min_periods=1).mean()


plt.plot(msft.index, msft, label=args.stockCode)
plt.plot(average.index, average, label=str(args.averageDays)+' days mean')
plt.xlabel('Date')
plt.ylabel('Closing price (zl)')
plt.grid()
plt.legend()
if (args.plotToFile):
    plt.savefig("plots/"+args.stockCode+"."+end_date+"plot.png")
plt.show()

