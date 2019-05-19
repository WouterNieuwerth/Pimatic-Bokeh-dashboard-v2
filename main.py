#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May  4 11:56:08 2019

@author: wouternieuwerth

Based on: https://towardsdatascience.com/data-visualization-with-bokeh-in-python-part-iii-a-complete-dashboard-dc6a86aa6e23
"""

# Pandas for data management
import pandas as pd

# general imports
import datetime

# my own modules
from scripts.pimatic_api import smartmeter

# os methods for manipulating paths
from os.path import dirname, join

# Bokeh basics 
from bokeh.io import curdoc
from bokeh.models.widgets import Tabs


# Each tab is drawn by one script
from scripts.heatmap import heatmap
from scripts.heatmap_test import heatmap2
from scripts.barchart import barchart

# Read data into dataframe
try:
    df = pd.read_csv(join(dirname(__file__), 'data', 'smartmeter_output.csv'), 
	                                          index_col=0)
    latest = max(pd.to_datetime(df['time'], unit='ms'))
    now = datetime.datetime.today()
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

# Create each of the tabs
tab1 = heatmap(df)
tab2 = heatmap2(df)
tab3 = barchart(df)

# Put all the tabs into one application
tabs = Tabs(tabs = [tab1, tab2, tab3])

# Put the tabs in the current document for display
curdoc().add_root(tabs)