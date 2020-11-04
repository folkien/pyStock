#!/usr/bin/python3
# -*- coding: utf-8 -*-
'Fetcher gets url data and extracts specified HTML element with specified classes'
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
        self.results = {}
        self.coding = 'utf-8'

    def fetchHtmlData(self):
        'Fetches HTML data from given URL'
        from urllib.request import Request, urlopen
        from urllib.error import URLError

        req = Request(self.url)
        try:
            response = urlopen(req)
        except URLError as e:
            if hasattr(e, 'reason'):
                print('(Error) We failed to reach a server.')
                print('(Error) Reason: ', e.reason)
            elif hasattr(e, 'code'):
                print('(Error) The server couldn\'t fulfill the request.')
                print('(Error) Error code: ', e.code)
        else:
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
        if (self.fetchHtmlData() is True):
            selection = self.getSelection()
            self.clean()
            return selection
        return 'Fetcher failed for %s.\n\n' % self.url

# testDocument = htmlFetcher("https://www.bankier.pl/inwestowanie/profile/quote.html?symbol=ELZAB",
#                            "div", "box300 boxGrey border3 right")
# print testDocument.Process()
