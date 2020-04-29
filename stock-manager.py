#!/usr/bin/python3
import pandas as pd
import sys
import argparse
import datetime
import json
import os
from filelock import Timeout, FileLock
from lib.jsonModule import *
from lib.htmlModule import *
from lib.assets import *

# Lock timeout is 5 minutes
lockTimeout = 5*60
executionIntervals = ["weekly", "daily"]
configFile = "config/viewer.json"
recipientsFile = "config/recipients.json"
# report file path
reportFile = "plots/report.md"
# Size of report file with no data or header data
reportFileEmptySize = 0
entries = []
recipients = []
dataIsChanged = False
recipientsIsChanged = False

# Html fetcher default data - configured for bankier.pl
defaultHtmlElement = "div"
defaultHtmlElementClasses = "box300 boxGrey border3 right"

# Locks creation
lockConfig = FileLock(configFile+".lock", timeout=lockTimeout)
lockRecipents = FileLock(recipientsFile+".lock", timeout=lockTimeout)

# Emergency ForceExit


def ForceExit(message, ErrorCode=1):
    global lockRecipents
    global lockConfig
    print("(Stock-manager) %s\n" % (message))
    lockRecipents.release()
    lockConfig.release()
    sys.exit(ErrorCode)

# Entry handling


def recipientsAdd(address):
    global recipients
    global recipientsIsChanged
    recipients.append({"address": address})
    recipientsIsChanged = True


def recipientsRemove(address):
    global recipients
    global recipientsIsChanged
    try:
        recipients.remove({"address": address})
        recipientsIsChanged = True
    except ValueError:
        pass

# Entry handling


def entryAdd(arguments, url, element, classes):
    global entries
    entries.append({"arguments": arguments, "url": url,
                    "htmlElement": element, "htmlClasses": classes})


def entryRemove(arguments, url, element, classes):
    global entries
    try:
        entries.remove({"arguments": arguments, "url": url,
                        "htmlElement": element, "htmlClasses": classes})
    except ValueError:
        pass


def entryPrint(entry):
    print(entry)


def entryExecute(entry, interval):

    # Execute stock-viewer
    if (os.system("stock-viewer "+entry["arguments"]+" -g -r -ri "+interval) != 0):
        print("Entry %s execution failed!\n" % (entry["arguments"]))
        return False

    # Use HTML fetcher to fetch additional data
    if (entry["url"] != "") and (interval == "weekly"):
        fetcher = htmlFetcher(
            entry["url"], entry["htmlElement"], entry["htmlClasses"])
        ReportsAppend(reportFile, fetcher.Process()+"\n")

    return True

# Appends data to reports file


def ReportAssets(filepath):
    with FileLock(filepath+".lock", timeout=lockTimeout):
        if os.path.isfile(filepath):
            with open(filepath, 'a+') as f:
                stockAssets.Report(f, "zl")

# Appends data to reports file


def ReportsAppend(filepath, data):
    with FileLock(filepath+".lock", timeout=lockTimeout):
        if os.path.isfile(filepath):
            with open(filepath, 'a+') as f:
                f.write(data)

# Save reports to file. Append text.


def ReportsClean(filepath):
    global reportFileEmptySize
    with FileLock(filepath+".lock", timeout=lockTimeout):
        os.system("rm -rf plots/report.md*")
        os.system("rm -rf plots/*.png")

        # Create file for reports with header
        with open(filepath, 'w') as f:
            f.write("%s report from <span style='color:blue'>%s</span> - file '%s'.\n" %
                    (args.execute, datetime.datetime.now().strftime("%d.%m.%Y %H:%M"), configFile))
            f.write("------------------\n")
            f.write("\n")
            f.close()
        # update empty file size after creation and header write
        reportFileEmptySize = os.path.getsize(reportFile)

# Save reports to file. Append text.


def ReportsIsAnyting(filepath):
    if (os.path.isfile(filepath)) and (os.path.getsize(filepath) > reportFileEmptySize):
        return True
    return False

# Save reports to file. Append text.


def ReportsToHTML(filepath):
    os.system("make -C plots/ html")
    # Replace images with embedded imaces code
    os.system("sed -i 's/img src=\"/img src=\"cid:/g' %s" % (reportFile))

# mail all reports


def ReportsMail(recipient, filepath):
    print("Mail %s to %s." % (filepath, recipient))
    currentDate = datetime.date.today()
    # Send email with attamchents through mutt smtp
    os.system("mutt -e 'set content_type=text/html' -s '[Stock] Report %s for %s' -a plots/*.png -- %s < %s" %
              (args.execute, currentDate.strftime("%d/%m/%Y"), recipient, filepath))


parser = argparse.ArgumentParser()
parser.add_argument("-a", "--add",    action='store_true',
                    required=False, help="Adds given")
parser.add_argument("-d", "--delete", action='store_true',
                    required=False, help="Remove")
parser.add_argument("-e", "--execute", type=str,
                    required=False, help="Execute")
parser.add_argument("-s", "--show", action='store_true',
                    required=False, help="Print")
parser.add_argument("-ar", "--addRecipient", type=str,
                    required=False, help="Add email recipient")
parser.add_argument("-an", "--arguments", type=str,
                    required=False, help="Arguments")
parser.add_argument("-au", "--url", type=str,
                    required=False, help="Bankier URL")
args = parser.parse_args()

# Assert
if (not args.add and
    not args.execute and
    not args.delete and
    not args.addRecipient and
        not args.show):
    print("Missing event")
    sys.exit(1)

# Assert of execution parameter
if (args.execute is None) or (args.execute not in executionIntervals):
    print("Wrong or missing execution interval.")
    sys.exit(1)

# Assert - get locks
lockConfig.acquire()
lockRecipents.acquire()

stockAssets = StockAssets()
ReportsClean(reportFile)
entries = jsonRead(configFile)
recipients = jsonRead(recipientsFile)

# 0. Adding entries
# #####################################################33
if (args.add):
    entryRemove(args.arguments, args.url, defaultHtmlElement,
                defaultHtmlElementClasses)
    entryAdd(args.arguments, args.url, defaultHtmlElement,
             defaultHtmlElementClasses)
    dataIsChanged = True

if (args.addRecipient is not None):
    recipientsRemove(args.addRecipient)
    recipientsAdd(args.addRecipient)

# 1. Removing entries
# #####################################################33
if (args.delete):
    entryRemove(args.arguments, args.url, defaultHtmlElement,
                defaultHtmlElementClasses)
    dataIsChanged = True

# 2. Checking entries
# #####################################################33
for i in range(len(entries)):
    entry = entries[i]

    if (args.show):
        entryPrint(entry)

    if (args.execute is not None):
        if (entryExecute(entry, args.execute) != True):
            ForceExit("Execution failed!")

# 4. Write entries if were changed
# #####################################################33
if (dataIsChanged == True):
    jsonWrite(configFile, entries)

if (recipientsIsChanged == True):
    jsonWrite(recipientsFile, recipients)

# 5. Finish execution
if (args.execute is not None):
    # If report has something
    if (ReportsIsAnyting(reportFile)):
        # Report also assets
        ReportAssets(reportFile)
        # Generate HTML
        ReportsToHTML(reportFile)
        # Send emails to all recipients
        for i in range(len(recipients)):
            ReportsMail(recipients[i]['address'], reportFile+".html")

lockRecipents.release()
lockConfig.release()
