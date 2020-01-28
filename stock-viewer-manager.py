#!/usr/bin/python2.7
import pandas as pd
import sys, argparse
import datetime
import json
import os
from jsonModule import *
from htmlModule import *

configFile="config/viewer.json"
recipientsFile="config/recipients.json"
reportFile="plots/report.md"
entries=[]
recipients=[]
dataIsChanged=False
recipientsIsChanged=False

# Html fetcher default data - configured for bankier.pl
defaultHtmlElement="div"
defaultHtmlElementClasses="box300 boxGrey border3 right"

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
def entryAdd(arguments,url,element,classes):
    global entries
    entries.append({"arguments":arguments, "url":url, "htmlElement":element, "htmlClasses":classes })

def entryRemove(arguments, url, element, classes):
    global entries
    try:
        entries.remove({"arguments":arguments, "url":url, "htmlElement":element, "htmlClasses":classes})
    except ValueError:
        pass

def entryPrint(entry):
    print entry

def entryExecute(entry):
    os.system("stock-viewer "+entry["arguments"]+" -g -r")
    # Use HTML fetcher to fetch additional data
    if (entry["url"] != ""):
        fetcher = htmlFetcher(entry["url"],entry["htmlElement"],entry["htmlClasses"])
        ReportsAppend(reportFile, fetcher.Process())
    return False

# Appends data to reports file
def ReportsAppend(filepath, data):
    if os.path.isfile(filepath):
        with open(filepath, 'w') as f:
            f.write(data)
            f.close()

# Save reports to file. Append text.
def ReportsClean(filepath):
    os.system("rm -rf plots/*.png")
    if os.path.isfile(filepath):
        with open(filepath, 'w') as f:
            f.write("")
            f.close()

# Save reports to file. Append text.
def ReportsToHTML(filepath):
    os.system("make -C plots/ html")
    # Replace images with embedded imaces code
    os.system("sed -i 's/img src=\"/img src=\"cid:/g' %s" % (reportFile))
    
def ReportsMail(recipient, reportFile):
    if os.path.isfile(reportFile):
        print("Mail to %s." % (recipient))
        currentDate = datetime.date.today()
        # Send email with attamchents through mutt smtp
        os.system("mutt -e 'set content_type=text/html' -s '[Stock] Report for %s' -a plots/*.png -- %s < %s" % 
                  (currentDate.strftime("%d/%m/%Y"), recipient, reportFile))
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
    entryRemove(args.arguments, args.url, defaultHtmlElement, defaultHtmlElementClasses)
    entryAdd(args.arguments, args.url, defaultHtmlElement, defaultHtmlElementClasses)
    dataIsChanged = True
    
if (args.addRecipient is not None):
    recipientsRemove(args.addRecipient)
    recipientsAdd(args.addRecipient)

# 1. Removing entries
# #####################################################33
if (args.delete):
    entryRemove(args.arguments, args.url, defaultHtmlElement, defaultHtmlElementClasses)
    dataIsChanged = True

# 2. Checking entries
# #####################################################33
for i in range(len(entries)):
    entry = entries[i]

    if (args.show):
        entryPrint(entry)

    if (args.execute):
        entryExecute(entry)


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

