'''
Created on 4 lut 2020

@author: spasz
'''
from pandas_datareader import data
from DataOperations import *
import matplotlib.pyplot as plt

# Get DATA from URL
# User pandas_reader.data.DataReader to load the desired data. As simple as that.
def GetData(code,begin,end):
    receivedData = data.DataReader(code, 'stooq', begin, end)

    if len(receivedData) == 0:
        print "No Stooq data for entry!"
        sys.exit(1)

    return receivedData

# Creation of Williams indicator for data
def SetWilliamsIndicator(price):
    jaw   = CreateMovingAverage(price,  13, 8)
    teeth = CreateMovingAverage(price,   8, 5)
    lips  = CreateMovingAverage(price,   5, 3)

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
    zeroLine = CreateDataLine(macd.index, 0, 0)
    # Create Buy/Sell
    fromBottom,fromTop=FindIntersections(macd, signal)
    # Plot
    plt.plot(zeroLine.index,zeroLine,'--',color='#777777')
    plt.plot(macd.index, macd, label='AMD MACD', color = '#FF0000')
    plt.plot(signal.index, signal, label='Signal Line', color='#008800')
    plt.plot(fromBottom.index, fromBottom, 'ro', label='Buy')
    plt.plot(fromTop.index, fromTop, 'go', label='Sell')

# Set RSI indicator
# TODO :
def SetRSI(prices, n=14):
    deltas = numpy.diff(prices)
    seed = deltas[:n+1]
    up = seed[seed>=0].sum()/n
    down = -seed[seed<0].sum()/n
    rs = up/down
    rsi = numpy.zeros_like(prices)
    rsi[:n] = 100. - 100./(1.+rs)

    for i in range(n, len(prices)):
        delta = deltas[i-1] # cause the diff is 1 shorter

        if delta>0:
            upval = delta
            downval = 0.
        else:
            upval = 0.
            downval = -delta

        up = (up*(n-1) + upval)/n
        down = (down*(n-1) + downval)/n

        rs = up/down
        rsi[i] = 100. - 100./(1.+rs)

    return pd.DataFrame(data=rsi,index=prices.index)

def PlotRSI(rsi):
    plt.plot(rsi.index, rsi, label='RSI', color = '#FF0000')
    plt.ylim(top=100,bottom=0)
    #OverBought
    overBought = CreateDataLine(rsi.index, 70, 70)
    plt.plot(overBought.index, overBought, '--', label='Overbought', color = '#AAAAAA')
    #OverSold
    overSold = CreateDataLine(rsi.index, 30, 30)
    plt.plot(overSold.index, overSold, '--', label='Oversold', color = '#AAAAAA')
    return 0


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
