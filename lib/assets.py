'''
Created on 29 lut 2020
@author: spasz
'''
import json
import os
import datetime
from filelock import Timeout, FileLock
from lib.jsonModule import *
import filelock
import random

def PlotAsset(ax,asset):
    dt = datetime.datetime.strptime(asset["date"], "%d-%M-%Y")
    if (asset['operation'] == "buy"):
        ax.plot(dt,asset["price"],"go")
    else:
        ax.plot(dt,asset["price"],"ro")
        
def ReportAsset(asset,currentClosePrice):
    text = "* %s %s - %d$ (%dj * %d) " % (asset["name"],asset["code"],
                                    asset["number"]*asset["price"],asset["number"],asset["price"])
    return text

# Stock Assets class 
class StockAssets(object):

    def __init__(self, filepath = "config/assets.json"):
        self.lockTimeout = 5*60
        self.isModified = False
        self.filepath = filepath 
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
            print(entry)

        # Save changes
        if (self.isModified == True):
            self.WriteAssets()
    
    def GetAssetsForStockCode(self,stockCode):
        findAssets = []
        for entry in self.data:
            if (entry["stockCode"] == stockCode):
                findAssets.append(entry)
        return findAssets
    
    def RemoveAsset(self,entry):
        try:
            self.data.remove({"id":entry["id"]})
        except ValueError:
            pass
        
        