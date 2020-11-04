import datetime

# One signal entry


class SignalEntry():

    def __init__(self, t, parentName, signalName):
        self.timestamp = t
        self.parentName = parentName
        self.signalName = signalName

    # report to file
    def Report(self, fileObject):
        fileObject.write("* **%s** %-20s - <span style='color:blue'>%s</span>\n" %
                         (self.timestamp.strftime('%d.%m'),
                             self.parentName,
                             self.signalName))


def CreateReportSignals():
    return ReportSignals()


# Report signals class
class ReportSignals():

    def __init__(self):
        self.signals = []
        self.stockCode = ''
        self.reportedAnything = False
        self.beginTimestamp = datetime.datetime.now() - datetime.timedelta(days=1)

    # set begin timestamp
    def SetBeginTimestamp(self, timestamp):
        if (type(timestamp) == datetime.datetime):
            self.beginTimestamp = timestamp

    # set stock Code for report
    def SetStockCode(self, code):
        self.stockCode = code

    # Add single signal
    def AddSignal(self, t, parentName, signalName):
        self.signals.append(SignalEntry(t, parentName, signalName))

    # Add dataframe with signals
    def AddDataframeSignals(self, data, parentName, signalName):
        if (data is not None and data.size):
            for i in range(len(data.values)):
                self.AddSignal(data.index[i], parentName, signalName)

    # Returns Allowed signals for no assets stock
    @staticmethod
    def GetAllSignalTypes():
        return ['buy', 'NotSell', 'MayBuy', 'NotBuy', 'sell']

    # Returns Allowed signals for no assets stock
    @staticmethod
    def GetBuySignalTypes():
        return ['buy', 'NotSell', 'MayBuy']

    # Report to file
    def Report(self, filepath, allSignalTypes=True):
        # Get allowed signals
        if (allSignalTypes == True):
            signalTypes = self.GetAllSignalTypes()
        else:
            signalTypes = self.GetBuySignalTypes()

        # If any signals exists
        if (len(self.signals) > 0):
            # Sort
            sortedSignals = sorted(
                self.signals, key=lambda x: x.timestamp, reverse=True)

            # Filter data by datetime & signalType
            filteredSignals = []
            for signal in sortedSignals:
                if (signal.timestamp > self.beginTimestamp) and (signal.signalName in signalTypes):
                    filteredSignals.append(signal)
                else:
                    break

            # Create report
            if (filteredSignals is not None and (len(filteredSignals) > 0)):
                with open(filepath, 'a+') as f:
                    f.write('## Signals for %s :\n' % (self.stockCode))
                    for signal in filteredSignals:
                        signal.Report(f)
                    f.write('\n')
                    f.close()
                    self.reportedAnything = True
