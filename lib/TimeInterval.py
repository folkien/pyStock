import datetime

executionIntervals = ['monthly', 'weekly', 'daily']


def GetIntervalBegin(intervalName):
    if (intervalName in executionIntervals):
        today = datetime.datetime.now()

        if (intervalName == 'monthly'):
            interval = today - datetime.timedelta(days=30)
        elif (intervalName == 'weekly'):
            interval = today - datetime.timedelta(days=7)
        else:
            interval = today - datetime.timedelta(days=1)

        return interval


class TimeInterval:

    def __init__(self):
        self.intervals = ['monthly', 'weekly', 'daily']
