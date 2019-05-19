#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 12 19:27:56 2019

@author: wouternieuwerth
"""

from bokeh.plotting import figure
from bokeh.models import RadioButtonGroup, Panel, ColumnDataSource, LinearColorMapper
from bokeh.layouts import gridplot
from bokeh.palettes import inferno
import numpy as np
import pandas as pd

TOOLS = "hover,save,pan,box_zoom,reset,wheel_zoom"

palette = inferno(25)
color_mapper = LinearColorMapper(palette=palette)

#------------------------------------------------------------------------------
# accept a dataframe, remove outliers, return cleaned data in a new dataframe
# see http://www.itl.nist.gov/div898/handbook/prc/section1/prc16.htm
#------------------------------------------------------------------------------
def remove_outlier(df_in, col_name):
    """accept a dataframe, remove outliers, return cleaned data in a new dataframe"""
    q1 = df_in[col_name].quantile(0.25)
    q3 = df_in[col_name].quantile(0.75)
    iqr = q3-q1 #Interquartile range
    fence_low  = q1-1.5*iqr
    fence_high = q3+1.5*iqr
    df_out = df_in.loc[(df_in[col_name] > fence_low) & (df_in[col_name] < fence_high)]
    return df_out

def barchart(df):
    
    def make_dataset(df, usageType):
        
        df_verwerkt = df[df['attributeName'] == usageType]
        df_verwerkt = df_verwerkt.sort_values('time')
        df_verwerkt = df_verwerkt.replace(0,np.NaN)
        df_verwerkt = df_verwerkt.fillna(method='ffill')
        df_verwerkt = df_verwerkt.fillna(method='bfill') # nodig om eerste rij te fixen.
        df_verwerkt['time'] = pd.to_datetime(df_verwerkt['time'], unit='ms')
        df_verwerkt['hour'] = df_verwerkt['time'].dt.hour
        df_verwerkt['minutes'] = (df_verwerkt['time'].dt.hour * 60) + df_verwerkt['time'].dt.minute
        df_verwerkt['dayofweek'] = df_verwerkt['time'].dt.dayofweek
        df_verwerkt['difference'] = df_verwerkt['value'].diff()
        df_verwerkt['difference'] = df_verwerkt['difference'].fillna(0)
        df_verwerkt = df_verwerkt[df_verwerkt['difference'] > 0]
        
        df_verwerkt = remove_outlier(df_verwerkt, 'difference')
        
        groupby = df_verwerkt.groupby('minutes').sum()
    
        return ColumnDataSource(data=groupby)
   
    def make_plot(src):
        
        p = figure(title='Bar chart', tools=TOOLS, background_fill_color="#fafafa")
        p.vbar(x='minutes', bottom=0, top='difference', source=src, width=0.9, color={'field': 'difference', 'transform': color_mapper})

        p.y_range.start = 0
        p.legend.location = "center_right"
        p.legend.background_fill_color = "#fefefe"
        p.xaxis.axis_label = 'Tijd'
        p.yaxis.axis_label = 'Verbruik'
        p.grid.grid_line_color="white"
        return p

    def update(attr, old, new):
        
        # Get the selected items for the graph
        # ...
        selected = radio_button_group.active
        
        usageType = 'gastotalusage' # standaardwaarde
        
        # Koppel de selectie aan de juiste gegevens uit het DataFrame
        if selected == 0:
            usageType = 'gastotalusage'
            p.title.text = 'Gasverbruik per minuut'
        elif selected == 1:
            usageType = 'tariff1totalusage'
            p.title.text = 'Stroomtarief 1 verbruik'
        elif selected == 2:
            usageType = 'tariff2totalusage'
            p.title.text = 'Stroomtarief 2 verbruik'
        
        print('Update usageType: ' + str(usageType))
       
        # update data
        new_src = make_dataset(df, usageType)
        src.data.update(new_src.data)

    radio_button_group = RadioButtonGroup(
        labels=["Gas", "Tarief 1", "Tarief 2"], active=0)
    
    radio_button_group.on_change('active', update)
    
    # initial execution
    src = make_dataset(df, 'gastotalusage')
    p = make_plot(src)
    
    # make a grid
    grid = gridplot([[p, radio_button_group]])
    
    tab = Panel(child = grid, title = 'Bar chart')
    
    print("barchart() uitgevoerd")
   
    return tab