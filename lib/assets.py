'''
Created on 29 lut 2020
@author: spasz
'''
import json
import os
import datetime
from filelock import Timeout, FileLock
from lib.jsonModule import *
from lib.StockData import *
import filelock
import random
from locale import currency

def PlotAsset(ax,asset):
    dt = datetime.datetime.strptime(asset["date"], "%d-%m-%Y")
    if (asset['operation'] == "buy"):
        ax.plot_date(dt,asset["price"],"v",color="k",ms=8)
        ax.plot_date(dt,asset["price"],"v",color="g",label='Asset')
    else:
        ax.plot_date(dt,asset["price"],"^",color="k",ms=8)
        ax.plot_date(dt,asset["price"],"^",color="r",label='Asset')
        
def ReportAsset(file,asset,currentClosePrice,currencySymbol):
    originalValue = asset['price']*asset['number']
    currentValue  = currentClosePrice*asset['number']
    valueDelta    = currentValue - originalValue
    change        = (valueDelta*100)/originalValue

    file.write("* %s *\"%s\"* - " % (asset["code"],asset["name"]))
    if (change >= 0):
        file.write("<span style='color:green'>%d%s +%2.2f%% +%d%s </span> " % (currentValue, currencySymbol, change, valueDelta, currencySymbol)) 
    else:
        file.write("<span style='color:red'>**%d%s** %2.2f%% %d%s </span> " % (currentValue, currencySymbol, change, valueDelta, currencySymbol)) 
    file.write(" from **%d%s** (%dj*%d%s) \n" % (originalValue, currencySymbol, asset['number'], asset['price'], currencySymbol)) 
    
# Class with single asset
class Asset(object):
    
    def __init__(self, jsonData):
        self.data = jsonData
        self.isInitialized = False

    def Init(self):
        stock = StockData(self.data['code'])
        self.currentPrice = stock.GetCurrentPrice()
        self.originalValue = self.data['price']*self.data['number']
        self.currentValue  = self.currentPrice*self.data['number']
        # money change
        self.income        = self.currentValue - self.originalValue
        # percent chage
        self.change        = (self.income*100)/self.originalValue
        self.isInitialized = True

    # Return percent change
    def GetIncome(self):
        return self.income
        
    # Return percent change
    def GetChange(self):
        return self.change

    def Report(self,file,currencySymbol):
        file.write("* %s *\"%s\"* - " % (self.data["code"],self.data["name"]))
        if (self.change >= 0):
            file.write("<span style='color:green'>%d%s +%2.2f%% +%d%s </span> " % (self.currentValue, currencySymbol, self.change, self.income, self.currencySymbol)) 
        else:
            file.write("<span style='color:red'>**%d%s** %2.2f%% %d%s </span> " % (self.currentValue, currencySymbol, self.change, self.income, currencySymbol)) 
        file.write(" from **%d%s** (%dj*%d%s) \n" % (self.originalValue, currencySymbol, self.data['number'], self.data['price'], currencySymbol)) 


# Stock Assets class 
class StockAssets(object):

    def __init__(self, filepath = "config/assets.json", extraReportFile = "plots/assets.md"):
        self.assets = []
        self.lockTimeout = 5*60
        self.isModified = False
        self.filepath = filepath 
        self.extraReportFile = extraReportFile
        self.ReadAssets()
        self.Init()

    def ReadAssets(self):
        lock = FileLock(self.filepath+".lock",timeout=self.lockTimeout)
        lock.acquire()
        self.data = jsonRead(self.filepath)
        lock.release()

    def WriteAssets(self):
        lock = FileLock(self.filepath+".lock",timeout=self.lockTimeout)
        lock.acquire()
        jsonWrite(self.filepath,self.data)
        self.isModified = False
        lock.release()
        
    def GetRandomHash(self):
        hash = random.getrandbits(128)
        hash_str = "%032x" % hash
        return hash_str
        
    # TODO : 
    # - position is openede/closed
    # - get only opened positions
    def Init(self):
        # Loop all data and check if valid elements
        for entry in self.data:
            # if missing "id" field then generate it
            if ("id" in entry):
                if (len(entry["id"]) == 0):
                    entry["id"] = self.GetRandomHash()
                    self.isModified = True
            else:
                    entry["id"] = self.GetRandomHash()
                    self.isModified = True
            # if missing "opened" field then generate it
            if ("opened" not in entry):
                    entry["opened"] = True
                    self.isModified = True
        # TODO Find sells

        # Save changes
        if (self.isModified == True):
            self.WriteAssets()
    
    def GetAssetsForStockCode(self,stockCode):
        findAssets = []
        for entry in self.data:
            if (entry["code"] == stockCode):
                findAssets.append(entry)
        return findAssets
    
    def RemoveAsset(self,entry):
        try:
            self.data.remove({"id":entry["id"]})
        except ValueError:
            pass
    
    # Create asset objects from json
    def CreateAssetObjects(self):    
        if (len(self.assets) == 0):
            for entry in self.data:
                assetObject = Asset(entry)
                assetObject.Init()
                self.assets.append(assetObject)
    
    # Report
    def Report(self, file, currencySymbol):
        totalChange = 0
        totalIncome = 0
        self.CreateAssetObjects()
        if (len(self.assets)>0):
            file.write("## Assets\n\n")
            for entry in self.assets:
                entry.Report(file, currencySymbol)
                totalIncome += entry.GetIncome()
                totalChange += entry.GetChange()
            file.write("\n")
            file.write("Total income : %d%s\n" % (totalIncome,currencySymbol))
            file.write("Total change : %d%%\n" % (totalChange))
            file.write("\n")
        
        
        