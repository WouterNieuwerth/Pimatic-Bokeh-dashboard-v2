#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 16 19:11:24 2019

@author: wouternieuwerth
"""

import requests
import datetime
import pandas as pd
from secretsss import secrets

secrets = secrets()

def smartmeter (start_date=datetime.datetime(2019, 3, 1), end_date=datetime.datetime.today()):
    df = pd.DataFrame()
    array = []
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    for single_date in daterange(start_date, end_date):
        print (single_date.strftime("%Y-%m-%d"))
    
        start = unix_time_millis(single_date)
        eind = start + 86400000 -1 # one day minus one millisecond
        
        # https://pimatic.org/api/actions/ --> queryDeviceAttributeEvents
        data = '{"criteria": { "deviceId": "smartmeter2", "after": ' + str(start) + ', "before": ' + str(eind) +'}}'
    
        response = requests.get('http://192.168.2.17:8080/api/database/device-attributes/', auth=(secrets['username'], secrets['password']), headers=headers, data=data)
        jsonresponse = response.json()
    
        for data in jsonresponse['events']:
            #print(data)
            array.append(pd.DataFrame(data, index=[0]))
    
    df = pd.concat(array, ignore_index=True)
    
    return df

epoch = datetime.datetime.utcfromtimestamp(0)
def unix_time_millis(dt):
    return int((dt - epoch).total_seconds() * 1000.0)

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)+1):
        yield start_date + datetime.timedelta(n)