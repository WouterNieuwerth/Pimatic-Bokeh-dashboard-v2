#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 11 19:12:11 2019

@author: wouternieuwerth
"""

import numpy as np
import pandas as pd
from math import pi
from pytz import timezone

from bokeh.models import ColumnDataSource, LinearColorMapper, ColorBar, BasicTicker, PrintfTickFormatter, RadioButtonGroup, Panel
from bokeh.models.widgets import Button
from bokeh.models.tickers import FixedTicker
from bokeh.plotting import figure
from bokeh.palettes import inferno
from bokeh.layouts import gridplot

from scripts.datahandler import getData

colors = inferno(25)
TOOLS = "hover,save,pan,box_zoom,reset,wheel_zoom"

def heatmap2(df):
    
    def make_dataset(df):
        """
        usageType:'gastotalusage, tariff1totalusage, tariff2totalusage of powertotalusage
        """
        
        pivot = pd.pivot_table(df, index='dayofweek', columns='hour', values='difference', aggfunc=sum)
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
                   tooltips=[('Verbruik', '@aantal'),('Dag', '@dayofweek'),('Uur','@hour')]
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
            p1.title.text = 'Gasverbruik per uur'
        elif selected == 1:
            usageType = 'tariff1totalusage'
            p1.title.text = 'Stroomtarief 1 verbruik'
        elif selected == 2:
            usageType = 'tariff2totalusage'
            p1.title.text = 'Stroomtarief 2 verbruik'
        elif selected == 3:
            usageType = 'powertotalusage'
            p1.title.text = 'Stroomverbruik per uur'
        
        print('Update usageType: ' + str(usageType))
       
        # update data
        df_usageType = make_dataset_usageType(df, usageType)
        new_src = make_dataset(df_usageType)
        new_srch = make_dataset_horizontaal(df_usageType)
        new_srcv = make_dataset_verticaal(df_usageType)
        
        src.data.update(new_src.data)
        srch.data.update(new_srch.data)
        srcv.data.update(new_srcv.data)
        
        # update color bar
        new_df = src.to_df()
        mapper1.low = new_df.aantal.min()
        mapper1.high = new_df.aantal.max()
        
        print('------------------------')
        
    def update_data():
        
        df = getData()
        
        # Get the selected items for the graph
        # ...
        selected = radio_button_group.active
        
        usageType = 'gastotalusage' # standaardwaarde
        
        # Koppel de selectie aan de juiste gegevens uit het DataFrame
        if selected == 0:
            usageType = 'gastotalusage'
            p1.title.text = 'Gasverbruik per uur'
        elif selected == 1:
            usageType = 'tariff1totalusage'
            p1.title.text = 'Stroomtarief 1 verbruik'
        elif selected == 2:
            usageType = 'tariff2totalusage'
            p1.title.text = 'Stroomtarief 2 verbruik'
        elif selected == 3:
            usageType = 'powertotalusage'
            p1.title.text = 'Stroomverbruik per uur'
        
        print('Update usageType: ' + str(usageType))
       
        # update data
        df_usageType = make_dataset_usageType(df, usageType)
        new_src = make_dataset(df_usageType)
        new_srch = make_dataset_horizontaal(df_usageType)
        new_srcv = make_dataset_verticaal(df_usageType)
        
        src.data.update(new_src.data)
        srch.data.update(new_srch.data)
        srcv.data.update(new_srcv.data)
        
        # update color bar
        new_df = src.to_df()
        mapper1.low = new_df.aantal.min()
        mapper1.high = new_df.aantal.max()
        
        print('------------------------')
        
    def make_dataset_horizontaal(df):
        
        groupby = df.groupby('hour').sum()
    
        return ColumnDataSource(data=groupby)
    
    def make_plot_horizontaal(src):

        p = figure(tools=TOOLS, 
                   background_fill_color="#ffffff", 
                   plot_width=846, plot_height=400, 
                   x_range=(-0.5,23.5),
                   tooltips=[('Verbruik', '@difference'),('Uur','@hour')])
        p.vbar(x='hour', bottom=0, top='difference', source=src, width=0.96, color={'field': 'difference', 'transform': mapper2},)
    
        p.y_range.start = 0
        p.xaxis.axis_label = 'Uur van de dag'
        p.yaxis.axis_label = 'Verbruik'
        p.grid.grid_line_color="#ffffff"
        p.xaxis.ticker = FixedTicker(ticks=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23])
        return p
    
    def make_dataset_verticaal(df):
        
        groupbyVertical = df.groupby('dayofweek').sum()
    
        return ColumnDataSource(data=groupbyVertical)
    
    def make_plot_verticaal(src):
    
        p = figure(title=' ', 
                   tools=TOOLS, 
                   background_fill_color="#ffffff", 
                   plot_width=400, 
                   plot_height=400, 
                   y_range=(-0.5,6.5), 
                   y_axis_location="right",
                   tooltips=[('Verbruik', '@difference'),('Dag','@dayofweek')])
        p.hbar(y='dayofweek', left=0, right='difference', source=src, height=0.96, color={'field': 'difference', 'transform': mapper2},)

        p.xaxis.axis_label = 'Verbruik'
        p.yaxis.axis_label = 'Dag van de week'
        p.grid.grid_line_color="#ffffff"
        p.yaxis.ticker = FixedTicker(ticks=[0,1,2,3,4,5,6])
        p.yaxis.major_label_overrides = {0:'Maandag', 1:'Dinsdag', 2:'Woensdag', 3:'Donderdag', 4:'Vrijdag', 5:'Zaterdag', 6:'Zondag'}
        return p
    
    def make_dataset_usageType(df, usageType):
        
        if usageType == 'powertotalusage': # select both tariff1totalusage and tariff2totalusage
            
            df_verwerkt1 = df[df['attributeName'] == 'tariff1totalusage']
            df_verwerkt1 = df_verwerkt1.sort_values('time')
            df_verwerkt1 = df_verwerkt1.replace(0,np.NaN)
            df_verwerkt1 = df_verwerkt1.fillna(method='ffill')
            df_verwerkt1 = df_verwerkt1.fillna(method='bfill') # nodig om eerste rij te fixen.
            df_verwerkt1['time'] = pd.to_datetime(df_verwerkt1['time'], unit='ms', utc=True)
            df_verwerkt1['time'] = df_verwerkt1['time'].apply(lambda x: x.astimezone(timezone('Europe/Amsterdam')))
            df_verwerkt1['hour'] = df_verwerkt1['time'].dt.hour
            # df_verwerkt1['minutes'] = (df_verwerkt1['time'].dt.hour * 60) + df_verwerkt1['time'].dt.minute
            df_verwerkt1['dayofweek'] = df_verwerkt1['time'].dt.dayofweek
            df_verwerkt1['difference'] = df_verwerkt1['value'].diff()
            df_verwerkt1['difference'] = df_verwerkt1['difference'].fillna(0)
            df_verwerkt1[df_verwerkt1['difference'] > 1000] = 0 # sprong naar Nederhoven uitfilteren
            
            df_verwerkt2 = df[df['attributeName'] == 'tariff2totalusage']
            df_verwerkt2 = df_verwerkt2.sort_values('time')
            df_verwerkt2 = df_verwerkt2.replace(0,np.NaN)
            df_verwerkt2 = df_verwerkt2.fillna(method='ffill')
            df_verwerkt2 = df_verwerkt2.fillna(method='bfill') # nodig om eerste rij te fixen.
            df_verwerkt2['time'] = pd.to_datetime(df_verwerkt2['time'], unit='ms', utc=True)
            df_verwerkt2['time'] = df_verwerkt2['time'].apply(lambda x: x.astimezone(timezone('Europe/Amsterdam')))
            df_verwerkt2['hour'] = df_verwerkt2['time'].dt.hour
            # df_verwerkt2['minutes'] = (df_verwerkt2['time'].dt.hour * 60) + df_verwerkt2['time'].dt.minute
            df_verwerkt2['dayofweek'] = df_verwerkt2['time'].dt.dayofweek
            df_verwerkt2['difference'] = df_verwerkt2['value'].diff()
            df_verwerkt2['difference'] = df_verwerkt2['difference'].fillna(0)
            df_verwerkt2[df_verwerkt2['difference'] > 1000] = 0 # sprong naar Nederhoven uitfilteren
            
            df_verwerkt = pd.concat([df_verwerkt1, df_verwerkt2], ignore_index=True)
            
        else: # business as usual, select a single usageType
            df_verwerkt = df[df['attributeName'] == usageType]
            df_verwerkt = df_verwerkt.sort_values('time')
            df_verwerkt = df_verwerkt.replace(0,np.NaN)
            df_verwerkt = df_verwerkt.fillna(method='ffill')
            df_verwerkt = df_verwerkt.fillna(method='bfill') # nodig om eerste rij te fixen.
            df_verwerkt['time'] = pd.to_datetime(df_verwerkt['time'], unit='ms', utc=True)
            df_verwerkt['time'] = df_verwerkt['time'].apply(lambda x: x.astimezone(timezone('Europe/Amsterdam')))
            df_verwerkt['hour'] = df_verwerkt['time'].dt.hour
            # df_verwerkt['minutes'] = (df_verwerkt['time'].dt.hour * 60) + df_verwerkt['time'].dt.minute
            df_verwerkt['dayofweek'] = df_verwerkt['time'].dt.dayofweek
            df_verwerkt['difference'] = df_verwerkt['value'].diff()
            df_verwerkt['difference'] = df_verwerkt['difference'].fillna(0)
            df_verwerkt[df_verwerkt['difference'] > 1000] = 0 # sprong naar Nederhoven uitfilteren
            
        return df_verwerkt

    radio_button_group = RadioButtonGroup(
        labels=["Gas", "Tarief 1", "Tarief 2", "Stroom totaal"], active=0)
    
    radio_button_group.on_change('active', update)
    
    button = Button(label="Update data", button_type="success")
    
    button.on_click(update_data)
    
    # initial execution
    df_usageType = make_dataset_usageType(df, 'gastotalusage')
    src = make_dataset(df_usageType)
    srch = make_dataset_horizontaal(df_usageType)
    srcv = make_dataset_verticaal(df_usageType)
    new_df = src.to_df()
    mapper1 = LinearColorMapper(palette=colors, low=new_df.aantal.min(), high=new_df.aantal.max())
    mapper2 = LinearColorMapper(palette=colors)
    p1 = make_plot(src)
    p2 = make_plot_horizontaal(srch)
    p3 = make_plot_verticaal(srcv)
    
    
    # make a grid
    grid = gridplot([[radio_button_group, button],[p1, p3],[p2]])
    
    tab = Panel(child = grid, title = 'Heatmap')
    
    print("heatmap() uitgevoerd")
   
    return tab