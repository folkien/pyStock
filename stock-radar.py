#!/usr/bin/env python3
# append to a dataframe a.append(pd.DataFrame({'close':99.99},index=[datetime.datetime.now()])
import matplotlib.pyplot as plt
import pandas as pd
import sys
import os
import argparse
import datetime
import numpy
from filelock import Timeout, FileLock
import pandas as pd
from pandas_datareader import data
from numpy import NaN
from matplotlib import gridspec
from bs4 import BeautifulSoup

# Lock timeout is 5 minutes
lockTimeout = 5 * 60


def DebugSave(filepath, data):
    with FileLock(filepath + '.lock', timeout=lockTimeout):
        with open(filepath, 'w+') as f:
            f.write(data)


def GetHTMLElement(content, element, elementClasses):
    ''' Get HTML element from data.'''
    soup = BeautifulSoup(content, 'lxml')
    selectionText = str(
        soup.find(element, class_=elementClasses))
    # Correct selection links to add basename
#     selectionText = re.sub("href=\"\/", "href=\"%s/" %
#                            (self.hostname), selectionText)
    return selectionText


def BiznesRadarParse(content):
    ''' Parse file HTML content to get stocks table '''
    table = GetHTMLElement(content, 'table', 'qTableFull')
    #DebugSave('table.html', table)
    data = pd.read_html(table, thousands=' ', decimal='.',
                        displayed_only=False)[0]
    # Remove separator lines
    data = data[data.ROE != 'ROE']
    data = data.reset_index()
    data = data.rename(columns={'Cena / Wartość księgowa': 'C/WK',
                                'Cena / Przychody ze sprzedaży': 'C/P',
                                'Cena / Zysk': 'C/Z',
                                'Aktualny kurs': 'Kurs',
                                'Średni obrót z 5 sesji [zł]': 'Obrot',
                                'Piotroski F-Score': 'Piotroski',
                                'Trend 6m': 'T6M',
                                'Trend 12m': 'T12M',
                                'Trend 24m': 'T24M',
                                'Zmiana kursu 3m [%]': 'Z3',
                                'Zmiana kursu 6m [%]': 'Z6',
                                'Zmiana kursu 12m [%]': 'Z12'
                                })
    # Convert string values to float/int values
    for i in (range(len(data['Profil']))):
        data['ROE'][i] = float(data['ROE'][i].replace(' ', '').strip('%'))
        data['ROA'][i] = float(data['ROA'][i].replace(' ', '').strip('%'))
        data['C/WK'][i] = float(data['C/WK'][i])
        data['C/P'][i] = float(data['C/P'][i])
        data['C/Z'][i] = float(data['C/Z'][i])
        data['Kurs'][i] = float(data['Kurs'][i])
        data['Obrot'][i] = int(data['Obrot'][i])
        data['Piotroski'][i] = int(data['Piotroski'][i])
        data['Z3'][i] = float(data['Z3'][i].replace(' ', '').strip('%'))
        data['Z6'][i] = float(data['Z6'][i].replace(' ', '').strip('%'))
        data['Z12'][i] = float(data['Z12'][i].replace(' ', '').strip('%'))

    return data


def Filter(stocks):
    '''
        Filter and sort stocks from pandas dataframe.

        Each rating is scaled to 0..100% and sumed up.
        Each commentary could be :
        - worst,
        - bad,
        - good,
        - great,
    '''
    ratings = []
    comments = []

    # Add column with spasz value
    for i in (range(len(stocks['Profil']))):
        commentary = ''
        rating = 0

        if 'ROE' in stocks:
            # Normalize
            if (stocks['ROE'][i] > 100):
                stocks['ROE'][i] = 100

            rating += stocks['ROE'][i]*1.5

        if 'ROA' in stocks:
            # Normalize
            if (stocks['ROA'][i] > 100):
                stocks['ROA'][i] = 100

            rating += stocks['ROA'][i]*1.5

        if 'Piotroski' in stocks:
            rating += ((stocks['Piotroski'][i]*100)/9)

        # C/P
        if 'C/P' in stocks:
            value = stocks['C/P'][i]
            if (value < 1):
                rating += 100 - 25*value
            elif (value < 10):
                rating += 80 - 5*value
            elif (value < 100):
                rating += 33.3 - 0.33*value
            else:
                rating += 0

        # C/Z
        if 'C/Z' in stocks:
            value = stocks['C/Z'][i]
            if (value < 1):
                commentary += 'great C/Z,'
                rating += 100 - 25*value
            elif (value < 10):
                commentary += 'good C/Z,'
                rating += 80 - 5*value
            elif (value < 100):
                commentary += 'bad C/Z,'
                rating += 33.3 - 0.33*value
            else:
                commentary += 'worst C/Z,'
                rating += 0

        # C/WK
        if 'C/WK' in stocks:
            c_wk = stocks['C/WK'][i]
            if (c_wk < 1):
                rating += 100 - 25*c_wk
            elif (c_wk < 10):
                rating += 80 - 5*c_wk
            elif (c_wk < 100):
                rating += 33.3 - 0.33*c_wk
            else:
                rating += 0

        # Obrot
        if 'Obrot' in stocks:
            obrot = stocks['Obrot'][i]
            if (obrot < 1000):
                commentary += 'worst Obrot,'
                rating += 0
            elif (obrot < 10000):
                commentary += 'bad Obrot,'
                rating += 20
            elif (obrot < 100000):
                commentary += 'good Obrot,'
                rating += 60
            else:
                commentary += 'great Obrot,'
                rating += 100

        # Zmiany
        if 'Z3' in stocks:
            change = stocks['Z3'][i]
            if (change > 100):
                change = 100
            rating += change * 0.33
        if 'Z6' in stocks:
            change = stocks['Z6'][i]
            if (change > 100):
                change = 100
            rating += change * 0.33
        if 'Z12' in stocks:
            change = stocks['Z12'][i]
            if (change > 100):
                change = 100
            rating += change * 0.33

        ratings.append(rating)
        comments.append(commentary)

    stocks['Rating'] = ratings
    stocks['Comments'] = comments
    stocks = stocks.sort_values(by=['Rating'], ascending=False)
    return stocks


# Const objects
# #####################################################
# Varaables
# #####################################################
# Arguments and config
# #####################################################
parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', type=str,
                    required=True, help='Input HTML file')
parser.add_argument('-o', '--output', type=str,
                    required=False, help='Output xlsx file')
parser.add_argument('-u', '--url', type=str,
                    required=False, help='URL to fetch. Not implemented!')
parser.add_argument('-g', '--plotToFile', action='store_true',
                    required=False, help='Plot to file')
args = parser.parse_args()

# TODO :
# - find kwartał
# - move at the end previous kwartał values


# Open input HTML file
filepath = args.input
if os.path.isfile(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
        stocks = BiznesRadarParse(content)
        stocks = Filter(stocks)

        # show data
        print(stocks)
        if (args.output is not None):
            stocks.to_excel(args.output)
