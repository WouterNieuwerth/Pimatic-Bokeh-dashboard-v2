#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 11 19:12:11 2019

@author: wouternieuwerth
"""

import numpy as np
import pandas as pd
from math import pi

from bokeh.models import ColumnDataSource, LinearColorMapper, ColorBar, BasicTicker, PrintfTickFormatter, RadioButtonGroup, Panel
from bokeh.models.tickers import FixedTicker
from bokeh.plotting import figure
from bokeh.palettes import inferno
from bokeh.layouts import gridplot

colors = inferno(25)
TOOLS = "hover,save,pan,box_zoom,reset,wheel_zoom"

def heatmap(df):
    
    def make_dataset(df, usageType):
        """
        usageType:'gastotalusage, tariff1totalusage of tariff2totalusage
        """
        
        df_verwerkt = df[df['attributeName'] == usageType]
        df_verwerkt = df_verwerkt.sort_values('time')
        df_verwerkt = df_verwerkt.replace(0,np.NaN)
        df_verwerkt = df_verwerkt.fillna(method='ffill')
        df_verwerkt['time'] = pd.to_datetime(df_verwerkt['time'], unit='ms')
        df_verwerkt['hour'] = df_verwerkt['time'].dt.hour
        df_verwerkt['dayofweek'] = df_verwerkt['time'].dt.dayofweek
        df_verwerkt['difference'] = df_verwerkt['value'].diff()
        
        pivot = pd.pivot_table(df_verwerkt, index='dayofweek', columns='hour', values='difference', aggfunc=sum)
        pivot = pivot.fillna(0)
        stacked = pivot.stack().reset_index()
        stacked = stacked.rename(columns={0:'aantal'})
            
        return ColumnDataSource(data=stacked)
        # return stacked
   
    def make_plot(src):


        p1 = figure(title="Gasverbruik per uur",
                   x_range=(-0.5,23.5), y_range=(-0.5,6.5),
                   x_axis_location="above", plot_width=900, plot_height=400,
                   tools=TOOLS, toolbar_location='below',
                   tooltips=[('Aantal', '@aantal'),('Dag', '@dayofweek'),('Uur','@hour')]
                  )

        p1.grid.grid_line_color = None
        p1.axis.axis_line_color = None
        p1.axis.major_tick_line_color = None
        p1.axis.major_label_text_font_size = "5pt"
        p1.axis.major_label_standoff = 0
        p1.xaxis.major_label_orientation = pi / 3
        p1.xaxis.ticker = FixedTicker(ticks=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23])
        p1.yaxis.ticker = FixedTicker(ticks=[0,1,2,3,4,5,6])
        p1.yaxis.major_label_overrides = {0:'Maandag', 1:'Dinsdag', 2:'Woensdag', 3:'Donderdag', 4:'Vrijdag', 5:'Zaterdag', 6:'Zondag'}
        
        p1.rect(x="hour", y="dayofweek", width=1, height=1,
               source=src,
               fill_color={'field': 'aantal', 'transform': mapper1},
               line_color=None)
        
        color_bar1 = ColorBar(color_mapper=mapper1, major_label_text_font_size="5pt",
                             ticker=BasicTicker(desired_num_ticks=len(colors)),
                             formatter=PrintfTickFormatter(format="%d"),
                             label_standoff=6, border_line_color=None, location=(0, 0))
        p1.add_layout(color_bar1, 'right')
        
        return p1

    def update(attr, old, new):
        
        # Get the selected items for the graph
        # ...
        selected = radio_button_group.active
        
        usageType = 'gastotalusage' # standaardwaarde
        
        # Koppel de selectie aan de juiste gegevens uit het DataFrame
        if selected == 0:
            usageType = 'gastotalusage'
            p.title.text = 'Gasverbruik per uur'
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
        
        # update color bar
        new_df = src.to_df()
        mapper1.low = new_df.aantal.min()
        mapper1.high = new_df.aantal.max()
        
        print('------------------------')

    radio_button_group = RadioButtonGroup(
        labels=["Gas", "Tarief 1", "Tarief 2"], active=0)
    
    radio_button_group.on_change('active', update)
    
    # initial execution
    src = make_dataset(df, 'gastotalusage')
    new_df = src.to_df()
    mapper1 = LinearColorMapper(palette=colors, low=new_df.aantal.min(), high=new_df.aantal.max())
    p = make_plot(src)
    
    # make a grid
    grid = gridplot([[p, radio_button_group]])
    
    tab = Panel(child = grid, title = 'Heatmap')
    
    print("heatmap() uitgevoerd")
   
    return tab