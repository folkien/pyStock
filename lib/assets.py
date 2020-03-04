'''
Created on 29 lut 2020
@author: spasz
'''
import json
import os
import datetime
import random
from filelock import Timeout, FileLock
from lib.jsonModule import *
from lib.StockData import *
from locale import currency

def PlotAsset(ax,asset):
    dt = datetime.datetime.strptime(asset["date"], "%d-%m-%Y")
    if (asset['operation'] == "buy"):
        ax.plot_date(dt,asset["price"],"o",color="k",ms=10)
        ax.plot_date(dt,asset["price"],"o",color="w",ms=8)
        ax.plot_date(dt,asset["price"],"v",color="g",label='Asset in')
    else:
        ax.plot_date(dt,asset["price"],"s",color="k",ms=10)
        ax.plot_date(dt,asset["price"],"s",color="w",ms=8)
        ax.plot_date(dt,asset["price"],"^",color="r",label='Asset out')

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
    file.write(" from **%d%s** (%dj x %d%s) \n" % (originalValue, currencySymbol, asset['number'], asset['price'], currencySymbol))

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

    #
    def IsReportable(self):
        if (self.data['opened'] == False) and (self.data['operation'] == "buy"):
            return False
        return True

    #
    def GetOriginalValue(self):
        return self.originalValue

    # Returns current value 
    def GetCurrentValue(self):
        return self.currentValue

    # Return percent change
    def GetIncome(self):
        return self.income
        
    # Return percent change
    def GetChange(self):
        return self.change

    def Report(self,file,currencySymbol):
        file.write("* %s *\"%s\"* - " % (self.data["code"],self.data["name"]))
        # Income 
        if (self.change >= 0):
            file.write("<span style='color:green'>+%2.2f%% +%2.2f%s</span> " % (self.change, self.income, currencySymbol)) 
        else:
            file.write("<span style='color:red'>%2.2f%% %2.2f%s</span> " % (self.change, self.income, currencySymbol)) 
        # Current value
        file.write("**%d%s** (%dj x %2.2f%s) " % (self.currentValue, currencySymbol, self.data['number'], self.currentPrice, currencySymbol))
        # Original value
        file.write("from **%d%s** (%dj x %2.2f%s) \n" % (self.originalValue, currencySymbol, self.data['number'], self.data['price'], currencySymbol))


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
        with FileLock(self.filepath+".lock",timeout=self.lockTimeout):
            self.data = jsonRead(self.filepath)

    def WriteAssets(self):
        with FileLock(self.filepath+".lock",timeout=self.lockTimeout):
            jsonWrite(self.filepath,self.data)
            self.isModified = False
        
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

    def GetAssetsForStockCode(self,stockCode,onlyOpened=False,onlyBuy=False,onlySell=False):
        findAssets = []
        for entry in self.data:
            if ( (entry["code"] == stockCode) and
                ((onlyOpened == False) or (onlyOpened==True) and (entry["opened"] == True)) and
                ((onlyBuy == False) or (onlyBuy==True) and (entry["operation"] == "buy")) and
                ((onlySell == False) or (onlySell==True) and (entry["operation"] == "sell")) ):
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
        totalInvested = 0
        totalValue    = 0
        self.CreateAssetObjects()

        if (len(self.assets)>0):
            file.write("## Assets\n\n")
            for entry in self.assets:
                if (entry.IsReportable()):
                    entry.Report(file, currencySymbol)
                    totalInvested += entry.GetOriginalValue()
                    totalValue    += entry.GetCurrentValue()

            income = totalValue - totalInvested
            change = (income*100)/totalInvested

            file.write("\n**Total income** ")

            # Income in percents
            if (income>=0):
                file.write("<span style='color:green'>+%2.2f%% %2.2f%s</span> " % (change,income,currencySymbol))
            else:
                file.write("<span style='color:red'>%2.2f%% %2.2f%s</span> " % (change,income,currencySymbol))

            # Income in currency
            file.write("**%d%s** from **%d%s**.\n" % (totalValue,currencySymbol,totalInvested,currencySymbol))
            file.write("\n")

    # Report
    def ReportForCode(self, stockCode, file, currencySymbol):
        totalInvested = 0
        totalValue    = 0
        self.CreateAssetObjects()

        if (len(self.assets)>0):
            file.write("## Assets\n\n")
            for entry in self.assets:
                if (entry.data['code'] == stockCode) and (entry.IsReportable()):
                    entry.Report(file, currencySymbol)
                    totalInvested += entry.GetOriginalValue()
                    totalValue    += entry.GetCurrentValue()

            income = totalValue - totalInvested
            change = (income*100)/totalInvested

            file.write("\n**Total income** : ")

            # Income in percents
            if (income>=0):
                file.write("<span style='color:green'>+%2.2f%%</span>" % (change))
            else:
                file.write("<span style='color:red'>%2.2f%%</span>" % (change))

            # Income in currency
            if (income>=0):
                file.write("<span style='color:green'>+%d%s %d%s</span> from %d%s.\n" % (income,currencySymbol,totalValue,currencySymbol,totalInvested,currencySymbol))
            else:
                file.write("<span style='color:red'>%d%s %d%s</span> from %d%s.\n" % (income,currencySymbol,totalValue,currencySymbol,totalInvested,currencySymbol))
            file.write("\n")



