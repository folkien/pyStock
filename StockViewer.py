#!/usr/bin/python2.7
import matplotlib.pyplot as plt
import pandas as pd
import sys, argparse
import datetime
from pandas_datareader import data

parser = argparse.ArgumentParser()
parser.add_argument("-n", "--stockCode", type=str, required=True, help="Stock name code")
parser.add_argument("-g", "--plotToFile", action='store_true', required=False, help="Plot to file")
args = parser.parse_args()

#Assert
if (not args.stockCode):
    print "No stockCode!"
    sys.exit(1)


# Dates
currentDateTime = datetime.datetime.now()
start_date  = '2010-01-01'
end_date    =  currentDateTime.strftime("%Y-%m-%d")

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

# Calculate the 20 and 100 days moving averages of the closing prices
short_rolling_msft = msft.rolling(window=20).mean()
long_rolling_msft = msft.rolling(window=100).mean()

# Plot everything by leveraging the very powerful matplotlib package
fig, ax = plt.subplots(figsize=(16,9))

ax.plot(msft.index, msft, label=args.stockCode)
ax.plot(short_rolling_msft.index, short_rolling_msft, label='20 days rolling')
ax.plot(long_rolling_msft.index, long_rolling_msft, label='100 days rolling')

ax.set_xlabel('Date')
ax.set_ylabel('Adjusted closing price (zl)')
ax.grid()
ax.legend()

plt.show()

