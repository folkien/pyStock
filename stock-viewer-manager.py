#!/usr/bin/python2.7
import pandas as pd
import sys, argparse
import datetime
import json
import os
from jsonModule import *

configFile="config/viewer.json"
reportFile="plots/report.md"
dataIsChanged=False
entries=[]

# Entry handling
def entryAdd(arguments,url):
    global entries
    entries.append({"arguments":arguments, "url":url })

def entryRemove(arguments, url):
    global entries
    try:
        entries.remove({"arguments":arguments, "url":url })
    except ValueError:
        pass

def entryPrint(entry):
    print entry

def entryExecute(arguments, url):
    os.system("stock-viewer "+arguments+" -g -r")
    return False

# Save reports to file. Append text.
def ReportsClean(filepath):
    with open(filepath, 'w') as f:
        f.write("")
        f.close()


parser = argparse.ArgumentParser()
parser.add_argument("-a", "--add",    action='store_true', required=False, help="Adds given")
parser.add_argument("-d", "--delete", action='store_true', required=False, help="Remove")
parser.add_argument("-e", "--execute", action='store_true', required=False, help="Execute")
parser.add_argument("-s", "--show", action='store_true', required=False, help="Print")
parser.add_argument("-an", "--arguments", type=str, required=False, help="Arguments")
parser.add_argument("-au", "--url", type=str, required=False, help="Bankier URL")
args = parser.parse_args()

#Assert
if (not args.add and not args.execute and not args.delete and not args.show):
    print "Missing event"
    sys.exit(1)

ReportsClean(reportFile)
entries = jsonRead(configFile)

# 0. Adding entries
# #####################################################33
if (args.add):
    entryRemove(args.arguments, args.url)
    entryAdd(args.arguments, args.url)
    dataIsChanged = True

# 1. Removing entries
# #####################################################33
if (args.delete):
    entryRemove(args.arguments, args.url)
    dataIsChanged = True

# 2. Checking entries
# #####################################################33
for i in range(len(entries)):
    entry = entries[i]

    if (args.show):
        entryPrint(entry)

    if (args.execute):
        entryExecute(entry['arguments'], entry['url'])
        print "No Stooq data for entry!"


# 4. Write entries if were changed
# #####################################################33
if (dataIsChanged == True):
    jsonWrite(configFile, entries)


