#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May  4 11:56:08 2019

@author: wouternieuwerth

Based on: https://towardsdatascience.com/data-visualization-with-bokeh-in-python-part-iii-a-complete-dashboard-dc6a86aa6e23

Navigate to directory
Run with !bokeh serve --show main.py
"""

from scripts.datahandler import getData

# Bokeh basics 
from bokeh.io import curdoc
from bokeh.models.widgets import Tabs


# Each tab is drawn by one script
from scripts.heatmap import heatmap
from scripts.heatmap_hour_day import heatmap2
from scripts.barchart import barchart
from scripts.barchart_datepicker import barchart_datepicker
    
df = getData()

# Create each of the tabs
tab1 = heatmap2(df)
tab2 = barchart(df)
tab3 = heatmap(df)
tab4 = barchart_datepicker(df)

# Put all the tabs into one application
tabs = Tabs(tabs = [tab1, tab2, tab3, tab4])

# Put the tabs in the current document for display
curdoc().add_root(tabs)