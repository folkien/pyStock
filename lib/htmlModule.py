#!/usr/bin/python3
# -*- coding: utf-8 -*-
'Fetcher gets url data and extracts specified HTML element with specified classes'

import os
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse


class htmlFetcher:

    def __init__(self, url, element, classes):
        self.url = url
        self.hostname = urlparse(url).hostname
        self.htmlElement = element
        self.htmlElementClasses = classes
        self.text = ''
        self.coding = 'utf-8'

    def fetchHtmlData(self):
        'Fetches HTML data from given URL'
        import urllib.request
        with urllib.request.urlopen(self.url) as response:
            data = response.read()

            # Get encoding, try utf-8 if not found.
            self.coding = response.headers.get_content_charset()
            if (self.coding is None):
                self.coding = 'utf-8'
            print('Encoding is %s' % self.coding)

            # Get data as string
            if (len(data) != 0):
                self.text = data.decode(self.coding)
                print('Fetched %uB from %s.' % (len(data), self.url))
                self.text = self.text.replace('\n', '')
                return True
            else:
                print('No data for %s !' % (self.url))
                return False

        return False

    def setHtmlData(self, newContent):
        'Set HTML data to parse'
        self.text = newContent

    def getSelection(self):
        'Gets filteres selection'
        if (not self.text):
            return ''
        else:
            soup = BeautifulSoup(self.text, 'lxml')
            selectionText = str(
                soup.find(self.htmlElement, class_=self.htmlElementClasses))
            # Correct selection links to add basename
            selectionText = re.sub("href=\"\/", "href=\"%s/" %
                                   (self.hostname), selectionText)
            return selectionText

    def clean(self):
        'Clean class local data'
        self.text = ''
        self.results = {}

    def Process(self):
        'Do all work and return extracted selection'
        if (self.fetchHtmlData() == True):
            selection = self.getSelection()
            self.clean()
            return selection
        else:
            return 'Fetcher failed for %s.\n\n' % self.url

# testDocument = htmlFetcher("https://www.bankier.pl/inwestowanie/profile/quote.html?symbol=ELZAB",
#                            "div", "box300 boxGrey border3 right")
# print testDocument.Process()
