'''
Created on 27 kwi 2020

@author: spasz
'''
import pickle
import os
import datetime
import time
from filelock import FileLock

# Lock timeout is 5 minutes
lockTimeout = 5 * 60


class StockDatabase(object):

    def __init__(self):
        self.directory = 'database/'

    # Store object in database
    def Save(self, objectName, object):
        filepath = self.directory + objectName + '.bin'
        with FileLock(filepath + '.lock', timeout=lockTimeout):
            with open(filepath, 'wb') as f:
                pickle.dump(object, f)
                print('Saved %s.bin.' % (objectName))

    # Load object in database
    def Load(self, objectName):
        object = None
        filepath = self.directory + objectName + '.bin'
        with FileLock(filepath + '.lock', timeout=lockTimeout):
            if os.path.isfile(filepath):
                with open(filepath, 'rb') as f:
                    object = pickle.load(f)
                    print('Loaded %s.bin.' % (objectName))

        return object

    # True if exists in database
    def IsExists(self, objectName):
        filepath = self.directory + objectName + '.bin'
        if os.path.isfile(filepath):
            return True
        return False

    # True if exists and is of today
    def IsOfTodaySession(self, objectName):
        currentDay = datetime.datetime.now().strftime('%Y-%m-%d')
        currentHour = int(datetime.datetime.now().strftime('%H'))
        filepath = self.directory + objectName + '.bin'
        if os.path.isfile(filepath):
            fileDate = time.strftime(
                '%Y-%m-%d', time.localtime(os.path.getmtime(filepath)))
            fileHour = int(time.strftime(
                '%H', time.localtime(os.path.getmtime(filepath))))
            # if is of today
            if (currentDay == fileDate):
                # if session ended then check if file is after session
                if (currentHour >= 18):
                    return (fileHour >= 18)
                return True

        return False
