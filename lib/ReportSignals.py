
# One signal entry
class SignalEntry():
    
    def __init__(self,t,parentName,signalName):
        self.timestamp  = t 
        self.parentName = parentName 
        self.signalName = signalName 
        
    # report to file 
    def Report(self,fileObject):
        fileObject.write("%s %s.\n" % (self.parentName,self.signalName))
        
# Report signals class
class ReportSignals():

    def __init__(self):
        self.signals = []
        
    # Add signal
    def AddSignal(self,t,parentName,signalName):
        self.signals.append(SignalEntry(t,parentName,signalName))
        
    # Report to file
    def Report(self,filepath):
        sortedSignals = sorted(self.signals,key=lambda x: x.timestamp, reverse=True)
        
        with open(filepath, 'a+') as f:
            for signal in sortedSignals:
                signal.Report(f)
            f.close()

        