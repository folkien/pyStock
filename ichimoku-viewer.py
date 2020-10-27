#!/usr/bin/env python3
# append to a dataframe a.append(pd.DataFrame({'close':99.99},index=[datetime.datetime.now()])
import matplotlib.pyplot as plt
import sys
import os
import argparse
import datetime
from filelock import Timeout, FileLock
from matplotlib import gridspec
from core.CountryInfo import CountryInfo
from helpers.DataOperations import *
from core.ReportSignals import *
from core.TimeInterval import *
from core.assets import StockAssets, ReportAsset
from indicators.StockData import StockData
from helpers.data import toNumIndex
import matplotlib.dates as mdates
from indicators.ichimoku import Ichimoku
from indicators.candlestickpatterns import CandlestickPatterns
from indicators.zigzag import ZigZag

# Create plot figures file


def PlotSave(fig):
    global graphsCreated
    #     emf, eps, pdf, png, ps, raw, rgba, svg, svgz
    #     for ext in [ ".png", ".jpeg", ".svg", ".eps", ".raw"]:
    #         filePath = outputFilepath + str(fig.number) + ext
    #         plt.figure(fig.number)
    #         plt.savefig(filePath)
    filePath = outputFilepath + str(fig.number) + outputExtension
    plt.figure(fig.number)
    plt.savefig(filePath)
    graphsCreated.append(filePath)
    print('Created plot %s.' % (filePath))

# remove all created plots


def PlotsRemove():
    global graphsCreated
    for filepath in graphsCreated:
        os.system('rm -rf %s' % (filepath))
        print('Removed %s.' % (filepath))


def ReportGraphs(f):
    # Insert all created graphs
    f.write('## Graphs\n\n')
    for path in graphsCreated:
        f.write('![Graph](%s)\n\n' % (os.path.basename(path)))
    f.write('\n')


# Const objects
# #####################################################
lockTimeout = 5 * 60
executionIntervals = ['monthly', 'weekly', 'daily']
reportFile = 'output/report.md'
plotsPath = 'output/'
outputExtension = '.svg'

# Varaables
# #####################################################

# Arguments and config
# #####################################################
parser = argparse.ArgumentParser()
parser.add_argument('-n', '--stockCode', type=str,
                    required=True, help='Stock name code')
parser.add_argument('-d', '--beginDate', type=str,
                    required=False, help='Begin date')
parser.add_argument('-Y', '--lastYear', action='store_true',
                    required=False, help='Last Year')
parser.add_argument('-9M', '--last9Months', action='store_true',
                    required=False, help='Last 9 Months')
parser.add_argument('-6M', '--last6Months', action='store_true',
                    required=False, help='Last 6 Months')
parser.add_argument('-3M', '--last3Months', action='store_true',
                    required=False, help='Last 3 Months')
parser.add_argument('-M', '--lastMonth', action='store_true',
                    required=False, help='Last Month')
parser.add_argument('-W', '--lastWeek', action='store_true',
                    required=False, help='Last Week')
parser.add_argument('-g', '--plotToFile', action='store_true',
                    required=False, help='Plot to file')
parser.add_argument('-r', '--reports', action='store_true',
                    required=False, help='Generate extra reports')
parser.add_argument('-ri', '--reportsInterval', type=str,
                    required=False, help='Interval of extra reports')
args = parser.parse_args()

# Assert
if (not args.stockCode):
    print('No stockCode!')
    sys.exit(1)

# Assert
if (args.reportsInterval is not None):
    if (args.reportsInterval not in executionIntervals):
        print('Wrong execution interval!')
        sys.exit(1)

# Create Country Info
info = CountryInfo(args.stockCode)

# Use non-interactive backend when plot to file used
if (args.plotToFile):
    import matplotlib
    matplotlib.use('Agg')

# Dates
today = datetime.datetime.now()
# End date
end_date = today.strftime('%Y-%m-%d')
# Start date
if (args.beginDate):
    start_date = args.beginDate
else:
    start_date = '2010-01-01'
# Check last year
if (args.lastYear):
    tmpDate = datetime.datetime.now() - datetime.timedelta(days=365)
    start_date = tmpDate.strftime('%Y-%m-%d')
# Check last 9 month
if (args.last9Months):
    tmpDate = datetime.datetime.now() - datetime.timedelta(days=30 * 9)
    start_date = tmpDate.strftime('%Y-%m-%d')
# Check last 6 month
if (args.last6Months):
    tmpDate = datetime.datetime.now() - datetime.timedelta(days=30 * 6)
    start_date = tmpDate.strftime('%Y-%m-%d')
# Check last 3 month
if (args.last3Months):
    tmpDate = datetime.datetime.now() - datetime.timedelta(days=30 * 3)
    start_date = tmpDate.strftime('%Y-%m-%d')
# Check last month
if (args.lastMonth):
    tmpDate = datetime.datetime.now() - datetime.timedelta(days=30)
    start_date = tmpDate.strftime('%Y-%m-%d')
# Check last Week
if (args.lastWeek):
    tmpDate = datetime.datetime.now() - datetime.timedelta(days=7)
    start_date = tmpDate.strftime('%Y-%m-%d')


# Dynamic variables
# #####################################################
outputFilename = args.stockCode + '_' + end_date + '_'
outputFilepath = plotsPath + outputFilename
graphsCreated = []
reportSignals = CreateReportSignals()
executionInterval = 'weekly'

# Update - execution Interval
if (args.reportsInterval is not None):
    executionInterval = args.reportsInterval

reportSignals.SetBeginTimestamp(GetIntervalBegin(executionInterval))
reportSignals.SetStockCode(args.stockCode)


# Get stock data
# #####################################################
stockAssets = StockAssets()
stockData = StockData(args.stockCode, start_date, end_date)
stockData.SetAssets(stockAssets)
stockData.SetCurrencySymbol(info.GetCurrency())

# Create oscillators/indicators
# #####################################################
closePriceTotal = stockData.GetAllData('Close')
closePrice = stockData.GetData('Close')
ichimoku = Ichimoku(stockData.GetData('Open'),
                    stockData.GetData('High'),
                    stockData.GetData('Low'),
                    stockData.GetData('Close')
                    )
zigzag = ZigZag(stockData.GetData('Open'),
                stockData.GetData('High'),
                stockData.GetData('Low'),
                stockData.GetData('Close')
                )
candlepatterns = CandlestickPatterns(stockData.GetData())

# PLOT 5
# #####################################################
# #####################################################
fig = plt.figure(figsize=(16.0, 9.0))

plot9 = plt.subplot(1, 1, 1)
stockData.PlotAssets()
ichimoku.Plot(plot9)
stockData.PlotCandle(plot9)
candlepatterns.Plot(plot9)
# zigzag.Plot(plot9)
plt.ylabel('Price (%s)' % (info.GetCurrency()))
plt.title('%s - page 2' % stockData.GetStockCode())
plt.legend(loc='upper left')
plt.minorticks_on()
plt.grid(b=True, which='major', axis='both', color='k')
plt.grid(b=True, which='minor', axis='both')
# Add return rates axle
stockData.AddReturnRatesAxle(plot9)


# Plot to file or show
if (args.plotToFile):
    PlotSave(fig)

# Create reports
if (args.reports):
    reportAllSignalTypes = False

    # If there are opened assets then report all signals
    if (len(stockAssets.GetAssetsForStockCode(args.stockCode, onlyOpened=True)) != 0):
        reportAllSignalTypes = True

    # Daily report
    if (executionInterval == 'daily'):
        reportSignals.Report(reportFile, reportAllSignalTypes)

        # If signals reported
        if (reportSignals.reportedAnything == True) or (True):
            with open(reportFile, 'a+') as f:
                stockData.Report(f, executionInterval)
                stockData.ReportAssets(f)
                ReportGraphs(f)
        # remove plots if nothing reported
        else:
            PlotsRemove()
    # Weekly report
    else:
        with open(reportFile, 'a+') as f:
            stockData.Report(f, executionInterval)
        reportSignals.Report(reportFile, reportAllSignalTypes)
        with open(reportFile, 'a+') as f:
            stockData.ReportAssets(f)
            ReportGraphs(f)

# Show all plots
if (not args.plotToFile):
    plt.show()
