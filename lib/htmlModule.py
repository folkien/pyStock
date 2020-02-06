#!/usr/bin/python3
# -*- coding: utf-8 -*-
import  os, urllib, re
from bs4 import BeautifulSoup
from urllib.parse import urlparse


"Fetcher gets url data and extracts specified HTML element with specified classes"
class htmlFetcher:

        def __init__(self, url, element, classes):
            self.url = url
            self.hostname = urlparse(url).hostname
            self.htmlElement = element
            self.htmlElementClasses = classes
            self.text = ""
            self.coding = "utf-8"

        "Fetches HTML data from given URL"
        def fetchHtmlData(self):
            from urllib.request import Request, urlopen
            from urllib.error import URLError, HTTPError

            try:
                response = urllib.request.urlopen(self.url)
            except HTTPError as e:
                print('Error code: ', e.code)
            except URLError as e:
                print('Reason: ', e.reason)
            else:
                # Get encoding, try utf-8 if not found.
                self.coding = response.headers.get_content_charset()
                if (self.coding is None):
                    self.coding = "utf-8"

                # Get data as string
                if (len(response.read()) != 0):
                    print("Encoding is %s" % self.coding)
                    self.text=response.read().decode(self.url)
                    data = response.read().decode(self.coding)
                    print("Fetched %uB from %s." % (len(data),self.url))
                    self.text = data.replace(b"\n", b"")
                    return True
                else:
                    print("No data for %s !" % (self.url))
                    return False

        "Set HTML data to parse"
        def setHtmlData(self, newContent):
            self.text = newContent

        "Gets filteres selection"
        def getSelection(self):
            if (not self.text):
                return ""
            else:
                soup = BeautifulSoup(self.text,"lxml")
                selectionText = str(soup.find(self.htmlElement,class_=self.htmlElementClasses))
                # Correct selection links to add basename
                selectionText = re.sub("href=\"\/","href=\"%s/" % (self.hostname),selectionText.decode(self.coding))
                return selectionText.encode("ascii","ignore")


        "Clean class local data"
        def clean(self):
            self.text	 = ""
            self.results = {}

        "Do all work and return extracted selection"
        def Process(self):
            if (self.fetchHtmlData() == True):
                selection = self.getSelection()
                self.clean()
                return selection
            else:
                return "Fetcher failed for %s.\n\n" % self.url

# testDocument = htmlFetcher("https://www.bankier.pl/inwestowanie/profile/quote.html?symbol=ELZAB",
#                            "div", "box300 boxGrey border3 right")
# print testDocument.Process()

