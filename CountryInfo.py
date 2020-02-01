'''

@author: spasz
'''

class CountryInfo(object):
    defaultCountry=['pl']
    countrySymbol=defaultCountry

    def __init__(self, stockCode):
        self.SetStockCode(stockCode)
    
    def SetStockCode(self, stockCode):
        symbol_parts = stockCode.split(".")
        if len(symbol_parts) > 1:
            self.countrySymbol=symbol_parts[1].lower()
        
    def GetCurrency(self):
        currencies = {
            "pl" : "zl",
            "de" : "eur",
            "hk" : "?",
            "hu" : "?",
            "jp" : "yen",
            "uk" : "GBP",
            "us" : "$",
            }
        return currencies[self.countrySymbol]
        