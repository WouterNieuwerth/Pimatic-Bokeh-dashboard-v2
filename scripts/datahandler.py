#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 15 10:34:50 2019

@author: wouternieuwerth
"""

# Pandas for data management
import pandas as pd

# general imports
import datetime

# my own modules
from scripts.pimatic_api import smartmeter

# os methods for manipulating paths
from os.path import dirname, join

def getData():
    # Read data into dataframe
    try:
        df = pd.read_csv(join(dirname(__file__), 'data', 'smartmeter_output.csv'), index_col=0)
        latest = max(pd.to_datetime(df['time'], unit='ms'))
        now = datetime.datetime.now()
        try:
            if (latest < now):
                df_new = smartmeter(start_date=latest, end_date=now)
                df = df.append(df_new, ignore_index=True)
        except:
            print('Error, geen nieuwe data opgehaald.')
    except:
        now = datetime.datetime.today()
        df = smartmeter(start_date=datetime.datetime(2018, 9, 8), end_date=now)
        
    df.to_csv(join(dirname(__file__), 'data', 'smartmeter_output.csv'))
    
    return df