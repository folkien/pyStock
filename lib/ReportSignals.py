import datetime

# One signal entry
class SignalEntry():
    
    def __init__(self,t,parentName,signalName):
        self.timestamp  = t 
        self.parentName = parentName 
        self.signalName = signalName 
        
    # report to file 
    def Report(self,fileObject):
        fileObject.write("* %s %s %s.\n" % (self.timestamp.strftime("%d %b"),
                                        self.parentName,self.signalName))
        
def CreateReportSignals():
    return ReportSignals()


# Report signals class
class ReportSignals():

    def __init__(self):
        self.signals = []
        self.beginTimestamp = datetime.datetime.now()  - datetime.timedelta(days=1)
        
    # set begin timestamp
    def SetBeginTimestamp(self,timestamp):
        if (type(timestamp) == datetime.datetime):
            self.beginTimestamp = timestamp
        
    # Add single signal
    def AddSignal(self,t,parentName,signalName):
        self.signals.append(SignalEntry(t,parentName,signalName))
    
    # Add dataframe with signals
    def AddDataframeSignals(self,data,parentName,signalName):
        if (data is not None and data.size):
            for i in range(len(data.values)):
                self.AddSignal(data.index[i],parentName,signalName)
        
    # Report to file
    def Report(self,filepath):
        if (len(self.signals)>0):
            sortedSignals = sorted(self.signals,key=lambda x: x.timestamp, reverse=True)
            
            with open(filepath, 'a+') as f:
                f.write("## Signals :\n")
                for signal in sortedSignals:
                    if (signal.timestamp > self.beginTimestamp):
                        signal.Report(f)
                    else:
                        break
                f.write("\n")
                f.close()

        