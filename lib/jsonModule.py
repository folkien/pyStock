#!/usr/bin/python3
'''
Created on 3 sty 2020
@author: spasz
'''
import json
import os

def jsonRead(filename):
    data = []
    if os.path.isfile(filename):
        with open(filename, 'r') as f:
            data = json.load(f)
    else:
        print("(JsonModule) File not exists!")
    return data

def jsonWrite(filename,data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4, sort_keys=True)
        f.close()
    print("Written %s.\n" % (filename))

def jsonShow(data):
    for entry in data:
        print(entry)
