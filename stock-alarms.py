#!/usr/bin/python2.7
import matplotlib.pyplot as plt
import pandas as pd
import sys, argparse
import datetime
import json
import os
from pandas_datareader import data
from enum import Enum

class AlarmState(Enum):
    Inactive = 0
    Active = 1

alarmsConfigFile="config/alarms.json"
alarmsIsChanged=False
alarms=[]

def alarmsRead():
    global alarmsConfigFile
    global alarms
    if os.path.isfile(alarmsConfigFile):
        with open(alarmsConfigFile, 'r') as f:
            alarms = json.load(f)

def alarmsWrite():
    global alarmsConfigFile
    global alarms
    with open(alarmsConfigFile, 'w') as f:
        json.dump(alarms, f)

def alarmsShow():
    global alarmsConfigFile
    global alarms
    for alarm in alarms:
        print alarm

def alarmsAdd(name,reference,alarmType,value,state):
    global alarms
    alarms.append({"name":name, "reference":reference,
                   "type":alarmType, "value":value, "state":state})

parser = argparse.ArgumentParser()
parser.add_argument("-a", "--addAlarm", action='store_true', required=False, help="")
parser.add_argument("-d", "--deleteAlarm", action='store_true', required=False, help="")
parser.add_argument("-c", "--checkAlarms", action='store_true', required=False, help="")
parser.add_argument("-n", "--stockCode", type=str, required=False, help="")
parser.add_argument("-r", "--referencePrice", type=int, required=False, help="")
parser.add_argument("-t", "--type", type=str, required=False, help="")
parser.add_argument("-v", "--value", type=int, required=False, help="")
parser.add_argument("-W", "--lastWeek", action='store_true', required=False, help="Last Week")
args = parser.parse_args()

#Assert
if (not args.addAlarm and not args.checkAlarms):
    print "Missing event"
    sys.exit(1)

if (args.addAlarm):
    if (not args.stockCode or not args.referencePrice or not args.type or not args.value):
        print "Missing arguments for adding."
        sys.exit(1)


## End date
currentDateTime = datetime.datetime.now()
end_date    =  currentDateTime.strftime("%Y-%m-%d")
# Check last month
tmpDate = datetime.datetime.now() - datetime.timedelta(days=30)
start_date  =  tmpDate.strftime("%Y-%m-%d")

alarmsRead()

# 0. Adding alarms
# #####################################################33
if (args.addAlarm):
    alarmsAdd(args.stockCode,args.referencePrice,args.type,args.value,AlarmState.Active)
    alarmsIsChanged = True

# 1. Removing alarms
# #####################################################33

# 2. Checking alarms
# #####################################################33
for i in range(len(alarms)):
    alarm = alarms[i]
    if (alarm['state'] == AlarmState.Active):
        # User pandas_reader.data.DataReader to load the desired data. As simple as that.
        panel_data = data.DataReader(alarm['name'], 'stooq', start_date, end_date)

        if len(panel_data) != 0:
            # Getting just the adjusted closing prices. This will return a Pandas DataFrame
            # The index in this DataFrame is the major index of the panel_data.
            close = panel_data['Close']
            price = close[-1]
            print "Check of "+str(price)+"with "+str(alarm['reference'])
            if alarm['type'] == "percent":
                valueChange=(alarm['reference']*alarm['value'])/100
                if abs(close[-1] - alarm['reference'])>valueChange:
                    print "Alarm for "+str(alarm['name'])+", price "+str(price)+"!"
                    alarms[i]['state'] = AlarmState.Inactive
                    alarmsIsChanged = True
            else:
                if abs(close[-1] - alarm['reference'])>alarm['value']:
                    print "Alarm for "+str(alarm['name'])+", price "+str(price)+"!"
                    alarms[i]['state'] = AlarmState.Inactive
                    alarmsIsChanged = True
        else:
            print "No Stooq data for entry!"

# 4. Write alarms if were changed
# #####################################################33
if (alarmsIsChanged == True):
    alarmsWrite()


