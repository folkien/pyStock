'''
Created on 27 kwi 2020

@author: spasz
'''
import pickle
import os
import datetime
import time
from filelock import Timeout, FileLock

# Lock timeout is 5 minutes
lockTimeout = 5*60


class StockDatabase(object):

    def __init__(self):
        self.directory = "database/"

    # Store object in database
    def Save(self, objectName, object):
        filepath = self.directory+objectName+".bin"
        with FileLock(filepath+".lock", timeout=lockTimeout):
            with open(filepath, 'wb') as f:
                pickle.dump(object, f)
                print("Saved %s.bin." % (objectName))

    # Load object in database
    def Load(self, objectName):
        object = None
        filepath = self.directory+objectName+".bin"
        with FileLock(filepath+".lock", timeout=lockTimeout):
            if os.path.isfile(filepath):
                with open(filepath, 'rb') as f:
                    object = pickle.load(f)
                    print("Loaded %s.bin." % (objectName))

        return object

    # True if exists in database
    def IsExists(self, objectName):
        filepath = self.directory+objectName+".bin"
        if os.path.isfile(filepath):
            return True
        return False

    # True if exists and is of today
    def IsOfToday(self, objectName):
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        filepath = self.directory+objectName+".bin"
        if os.path.isfile(filepath):
            fileutime = time.strftime(
                "%Y-%m-%d", time.localtime(os.path.getmtime(filepath)))
            if (today == fileutime):
                return True
        return False
