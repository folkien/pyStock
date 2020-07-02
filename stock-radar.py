#!/usr/bin/python3
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
    DebugSave('table.html', table)
    data = pd.read_html(table, thousands=' ', decimal='.',
                        displayed_only=False)[0]
    # Remove separator lines
    data = data[data.ROE != 'ROE']
    data = data.reset_index()
    data = data.rename(columns={'Cena / Wartość księgowa': 'C/WK',
                                'Cena / Przychody ze sprzedaży': 'C/P',
                                'Aktualny kurs': 'Kurs',
                                'Średni obrót z 5 sesji [zł]': 'Obrot',
                                'Piotroski F-Score': 'Piotroski',
                                })
    # Convert string values to float/int values
    for i in (range(len(data['Profil']))):
        data['ROE'][i] = float(data['ROE'][i].strip('%'))
        data['ROA'][i] = float(data['ROA'][i].strip('%'))
        data['C/WK'][i] = float(data['C/WK'][i])
        data['C/P'][i] = float(data['C/P'][i])
        data['Kurs'][i] = float(data['Kurs'][i])
        data['Obrot'][i] = int(data['Obrot'][i])
        data['Piotroski'][i] = int(data['Piotroski'][i])

    return data


def Filter(stocks):
    ''' Filter and sort stocks from pandas dataframe'''
    stocks = stocks.sort_values(by=['Piotroski'], ascending=False)
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
        print(stocks)
