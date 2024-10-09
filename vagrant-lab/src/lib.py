#!/usr/bin/env python3
import json

def import_json(filename):
    with open(filename,'r') as f:
        return json.load(f)



def str2dict(string):
    return eval(string)

def jrn2list(output):
    tmp = output.split('\n')
    tmp.pop()
    for k in range(len(tmp)):
        tmp[k] = str2dict(tmp[k])
    return tmp
