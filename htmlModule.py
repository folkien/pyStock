#!/usr/bin/python
# -*- coding: utf-8 -*-
import  os, urllib2, re, math, datetime, sqlite3
from bs4 import BeautifulSoup


# Pozbywanie się HTML z tekstu
from HTMLParser import HTMLParser

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

# Klasa do przechowywania pomiarów
class cMeasurement:

        def __init__(self, newLoc, newMoment, newDesc, newPatterns, newValue = ""):
            self.localization = newLoc
            self.moment       = newMoment
            self.desc         = newDesc
            # Ponieważ pomiar zazwyczaj uzyskujemy za pomocą przeszukiwania treści dokumentu
            # wyrażeniami regularnymi, dlatego też dodajemy listę wyrażen, których będziemy używać
            # aby wydobyć pomiar.
            self.patterns     = newPatterns
            self.value        = newValue

        def sqlFormat(self):
            return (self.localization, self.moment, self.desc, self.value)

        def str(sefl):
            return str(self.localization) +  str(self.moment) + str(self.desc) + str(self.value)

class htmlMeasurments:

        def __init__(self, newLink, newMeasurments=[]):
            self.link  	 = newLink
            self.text = ""
            self.measurments = newMeasurments
            self.coding = "utf-8"

        "Pobiera dokument o adresie wskazanym przez self.link z internetu."
        def fetchData(self):
            # odczytujemy stronę www i wyszukujemy pattern
            try:
                response 			 = urllib2.urlopen(self.link)
            except urllib2.HTTPError as err:
                print("Url error!")
                self.text = ""
            else:
                self.text			 = response.read().replace("\n", "")
                # Sprawdzamy kodowanie strony www
                result = re.search("charset=[a-zA-Z0-9\-]*", self.text)  # pierwszy filtr
                if (result != None):
                    # nadpisujemy kodowanie
                    self.coding = result.group(0)[8:]

        "Ustawia ręcznie treść dokumentu."
        def setData(self, newContent):
            self.text = newContent

        "Filtruje treść dokumentu dla każdego zestawu wzorców. Odczytane \
            wartości zapisuje w słowniku self.results."
        def doFiltering(self):
            soup = BeautifulSoup(self.text)
            print soup.find('div',['box300','boxGrey','border3','right']).text
            print soup.find('div',class_='box300').text
            print soup.find('div',{'class':['box300','boxGrey','border3','right']}).text
            return
            for measurement in self.measurments:
                result = self.text
                # Przechodzimy przez wszystkie filtry
                for filtr in measurement.patterns:
                    # print "Filtr:" + filtr
                    result = re.search(filtr, result)
                    if (result != None):
                        result = result.group(0)
                    else:
                        result = ""
                    # print "Result:" + result
                # Po filtrowaniu mamy w końcu rezultat który zapisujemy jako pomiar
                measurement.value = strip_tags(result).decode(self.coding)

            def freeMemory(self):
                    self.text	 = ""
                    self.results = {}

actualDate = "test"
testDocument = htmlMeasurments("https://www.bankier.pl/inwestowanie/profile/quote.html?symbol=ELZAB",
                            [
                            cMeasurement("Goryczkowa",actualDate,"wiatr",["<div class=\"box300 boxGrey border3 right\".*?</div>"])
                            ])
testDocument.fetchData()
testDocument.doFiltering()
for m in testDocument.measurments:
    print m.desc
    print m.localization
    print m.moment
    print m.value

