#!/usr/bin/python2.7
import pandas as pd
import sys, argparse
import datetime
import json
import os
from jsonModule import *

configFile="config/viewer.json"
recipientsFile="config/recipients.json"
reportFile="plots/report.md"
entries=[]
recipients=[]
dataIsChanged=False
recipientsIsChanged=False

# Entry handling
def recipientsAdd(address):
    global recipients
    global recipientsIsChanged
    recipients.append({"address":address})
    recipientsIsChanged=True

def recipientsRemove(address):
    global recipients
    global recipientsIsChanged
    try:
        recipients.remove({"address":address})
        recipientsIsChanged=True
    except ValueError:
        pass

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
    os.system("rm -rf plots/*.png")
    with open(filepath, 'w') as f:
        f.write("")
        f.close()

# Save reports to file. Append text.
def ReportsToHTML(filepath):
    os.system("make -C plots/ html")
    
def ReportsMail(recipient, reportFile):
    if os.path.isfile(reportFile):
        print("Mail to %s." % (recipient))
        os.system("mutt -e 'set content_type=text/html' -s '[Stock] Viewer' -a plots/*.png -- %s < %s" % (recipient, reportFile))
    else:
        print("File to send via mail not exists!")

parser = argparse.ArgumentParser()
parser.add_argument("-a", "--add",    action='store_true', required=False, help="Adds given")
parser.add_argument("-d", "--delete", action='store_true', required=False, help="Remove")
parser.add_argument("-e", "--execute", action='store_true', required=False, help="Execute")
parser.add_argument("-s", "--show", action='store_true', required=False, help="Print")
parser.add_argument("-ar", "--addRecipient", type=str, required=False, help="Add email recipient")
parser.add_argument("-an", "--arguments", type=str, required=False, help="Arguments")
parser.add_argument("-au", "--url", type=str, required=False, help="Bankier URL")
args = parser.parse_args()

#Assert
if (not args.add and 
    not args.execute and 
    not args.delete and
    not args.addRecipient and 
    not args.show):
    print "Missing event"
    sys.exit(1)

ReportsClean(reportFile)
entries = jsonRead(configFile)
recipients = jsonRead(recipientsFile)

# 0. Adding entries
# #####################################################33
if (args.add):
    entryRemove(args.arguments, args.url)
    entryAdd(args.arguments, args.url)
    dataIsChanged = True
    
if (args.addRecipient is not None):
    recipientsRemove(args.addRecipient)
    recipientsAdd(args.addRecipient)

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


# 4. Write entries if were changed
# #####################################################33
if (dataIsChanged == True):
    jsonWrite(configFile, entries)

if (recipientsIsChanged == True):
    jsonWrite(recipientsFile, recipients)

# 5. Finish execution
if (args.execute):
    ReportsToHTML(reportFile)
    # Send emails to all recipients
    for i in range(len(recipients)):
        ReportsMail(recipients[i]['address'], reportFile+".html")

