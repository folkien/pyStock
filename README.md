pyStock - repository of stock analyze, alarm and follow tools.
-------------
pyStock is a bunch of tools used for stock market analyze, follow, and alarms.
* stock-alarms - tool for setting stock alarms and notifiyng user about alarms.
* stock-viewer - tool for generating stock plots and text reports for given stock code. Diffrent plot options, volume, MACD, Williams indicator or RSI.
* stock-viewer-manager - tool manager which can send emails with stock reports, generates reports and plots using stock-viewer. Configurable via json settings files.

# Installation 
(Linux) To install all commands and systemd timers and services run script.
```
./install.sh
```

(Other OS) No installation tool provided.

# Usage

## Stock viewer.

Features :
* Generates plots (closePrice, Volume, Williams indicator, RSI, MACD),
* Save plots to files \*.png
* Generates/Appends report.md with some usefull informations,

```bash
usage: stock-viewer.py [-h] -n STOCKCODE [-d BEGINDATE] [-a AVERAGEDAYS] [-Y]
                       [-6M] [-M] [-W] [-g] [-r]

optional arguments:
  -h, --help            show this help message and exit
  -n STOCKCODE, --stockCode STOCKCODE
                        Stock name code
  -d BEGINDATE, --beginDate BEGINDATE
                        Begin date
  -a AVERAGEDAYS, --averageDays AVERAGEDAYS
                        Day to calc mean
  -Y, --lastYear        Last Year
  -6M, --last6Months    Last 6 Months
  -M, --lastMonth       Last Month
  -W, --lastWeek        Last Week
  -g, --plotToFile      Plot to file
  -r, --reports         Generate extra reports
```

Last year of apple with markdown reports into report.md
```bash
./stock-viewer.py -n AAPL.US -Y -r
```

Plot Apple last 6M to file
```bash
./stock-viewer.py -n AAPL.US -6M -g
```

Example CD Projekt Red plot
```bash
 ./stock-viewer.py -n CDR.pl -6M -g
```
![CDPR image](doc/CDR.2020-01-02plot.png)


## Stock manager

Features :
* Generates plots(via stoc-viewer) for all configured stock codes
* Generates report for all configured stock codes with extra HTML informations about news,
* Sends emails to cofnigured recipents

```bash
usage: stock-viewer-manager.py [-h] [-a] [-d] [-e] [-s] [-ar ADDRECIPIENT]
                               [-an ARGUMENTS] [-au URL]

optional arguments:
  -h, --help            show this help message and exit
  -a, --add             Adds given
  -d, --delete          Remove
  -e, --execute         Execute
  -s, --show            Print
  -ar ADDRECIPIENT, --addRecipient ADDRECIPIENT
                        Add email recipient
  -an ARGUMENTS, --arguments ARGUMENTS
                        Arguments
  -au URL, --url URL    Bankier URL
```

## Stock alarms

```bash
usage: stock-alarms.py [-h] [-a] [-d] [-c] [-p] [-n STOCKCODE]
                       [-r REFERENCEPRICE] [-t TYPE] [-v VALUE] [-W]

optional arguments:
  -h, --help            show this help message and exit
  -a, --addAlarm        Adds given alarm
  -d, --deleteAlarm     Removes alarm
  -c, --checkAlarms     Check all alarms
  -p, --printAlarms     Print all alarms
  -n STOCKCODE, --stockCode STOCKCODE
  -r REFERENCEPRICE, --referencePrice REFERENCEPRICE
  -t TYPE, --type TYPE
  -v VALUE, --value VALUE
  -W, --lastWeek        Last Week
```


# Known Issues

# Problem with pandas_datareader
There was a problem with pandas_datareader
https://stackoverflow.com/questions/53097523/importing-data-from-stooq-with-pandas-datareader-returns-empty-dataframe-in-pyth

Problem was solved in new pandas version. Recommeneded to use newest version. With newest version `country codes` after stock code works. 
Example of polish CDPR
```bash
./stock-viewer.py -n CDR.pl -Y
```
or USA google alphabet
```bash
./stock-viewer.py -n GOOG.us -Y
```

# TODO - for developers

## TODO Viewer
- codzienne sprawdzanie stanu i wysyłanie erraty w przypadku zmian lub nowych wskaznikow
- config .json z aktywami,
- RSI
- Poprawić URL w linkach z HTML fetchera

## TODO Alarmy : 
 -- aktywny i nieaktywne alarmy,
 -- pokazywanie alarmów,
- Wysyłanie emaili,
- Sprawdzanie najnowszych raportów dla inwestorów,
- Monitorowanie trendów oraz alarmy z trendów,

