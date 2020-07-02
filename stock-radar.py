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
from pandas_datareader import data
from numpy import NaN
from matplotlib import gridspec
from bs4 import BeautifulSoup


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
    print(table)


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


# Open input HTML file
filepath = args.input
if os.path.isfile(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
        BiznesRadarParse(content)
