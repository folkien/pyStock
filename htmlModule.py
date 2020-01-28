#!/usr/bin/python
# -*- coding: utf-8 -*-
import  os, urllib2, re, math, datetime 
from bs4 import BeautifulSoup


"Fetcher gets url data and extracts specified HTML element with specified classes"
class htmlFetcher:

        def __init__(self, url, element, classes):
            self.url = url
            self.htmlElement = element
            self.htmlElementClasses = classes
            self.text = ""
            self.coding = "utf-8"

        "Fetches HTML data from given URL"
        def fetchHtmlData(self):
            # odczytujemy stronę www i wyszukujemy pattern
            try:
                response 			 = urllib2.urlopen(self.url)
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

        "Set HTML data to parse"
        def setHtmlData(self, newContent):
            self.text = newContent

        "Gets filteres selection"
        def getSelection(self):
            soup = BeautifulSoup(self.text,"lxml")
            return soup.find(self.htmlElement,class_=self.htmlElementClasses)

        "Clean class local data"
        def clean(self):
                self.text	 = ""
                self.results = {}
                
        "Do all work and return extracted selection"
        def Process(self):
            self.fetchHtmlData()
            selection = self.getSelection()
            self.clean()
            return selection

testDocument = htmlFetcher("https://www.bankier.pl/inwestowanie/profile/quote.html?symbol=ELZAB",
                           "div", "box300 boxGrey border3 right")
print testDocument.Process()

