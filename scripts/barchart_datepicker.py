#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 12 19:27:56 2019

@author: wouternieuwerth
"""

from bokeh.plotting import figure
from bokeh.models import RadioButtonGroup, Panel, ColumnDataSource, LinearColorMapper
from bokeh.models.widgets import DatePicker
from bokeh.layouts import gridplot
from bokeh.palettes import inferno
import numpy as np
import pandas as pd
import datetime
from math import floor
from pytz import timezone
from datetime import date

TOOLS = "hover,save,pan,box_zoom,reset,wheel_zoom"

palette = inferno(25)
color_mapper = LinearColorMapper(palette=palette)

# standaardwaarden definieren:
usageType = 'gastotalusage'
start = datetime.date(2017,1,1)
stop = datetime.date.today()

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

def barchart_datepicker(df):
    
    def make_dataset(df, usageType='gastotalusage', start=datetime.date(2015,1,1), stop=datetime.date.today()):
        
        if type(start) == str:
            start = datetime.datetime.strptime(start, '%Y-%m-%d').date()
        if type(stop) == str:
            stop = datetime.datetime.strptime(stop, '%Y-%m-%d').date()
        
        start_milliseconds = ((start - datetime.date(1970,1,1)).total_seconds() * 1000)
        stop_milliseconds = ((stop - datetime.date(1970,1,1)).total_seconds() * 1000) + (86400000-1) # Plus 1 dag minus - milliseconde = einde van die dag
        
        if usageType == 'powertotalusage': # select both tariff1totalusage and tariff2totalusage
            
            df_verwerkt1 = df.loc[(df['attributeName'] == 'tariff1totalusage') & (df['time'] >= start_milliseconds) & (df['time'] <= stop_milliseconds)]
            df_verwerkt1 = df_verwerkt1.sort_values('time')
            df_verwerkt1 = df_verwerkt1.replace(0,np.NaN)
            df_verwerkt1 = df_verwerkt1.fillna(method='ffill')
            df_verwerkt1 = df_verwerkt1.fillna(method='bfill') # nodig om eerste rij te fixen.
            df_verwerkt1['time'] = pd.to_datetime(df_verwerkt1['time'], unit='ms', utc=True)
            df_verwerkt1['time'] = df_verwerkt1['time'].apply(lambda x: x.astimezone(timezone('Europe/Amsterdam')))
            # df_verwerkt1['hour'] = df_verwerkt1['time'].dt.hour
            df_verwerkt1['minutes'] = (df_verwerkt1['time'].dt.hour * 60) + df_verwerkt1['time'].dt.minute
            # df_verwerkt1['dayofweek'] = df_verwerkt1['time'].dt.dayofweek
            df_verwerkt1['difference'] = df_verwerkt1['value'].diff()
            df_verwerkt1['difference'] = df_verwerkt1['difference'].fillna(0)
            df_verwerkt1[df_verwerkt1['difference'] > 1000] = 0 # sprong naar Nederhoven uitfilteren
            df_verwerkt1 = df_verwerkt1[df_verwerkt1['difference'] > 0]
            
            # df_verwerkt1 = remove_outlier(df_verwerkt1, 'difference')
            
            df_verwerkt2 = df.loc[(df['attributeName'] == 'tariff2totalusage') & (df['time'] >= start_milliseconds) & (df['time'] <= stop_milliseconds)]
            df_verwerkt2 = df_verwerkt2.sort_values('time')
            df_verwerkt2 = df_verwerkt2.replace(0,np.NaN)
            df_verwerkt2 = df_verwerkt2.fillna(method='ffill')
            df_verwerkt2 = df_verwerkt2.fillna(method='bfill') # nodig om eerste rij te fixen.
            df_verwerkt2['time'] = pd.to_datetime(df_verwerkt2['time'], unit='ms', utc=True)
            df_verwerkt2['time'] = df_verwerkt2['time'].apply(lambda x: x.astimezone(timezone('Europe/Amsterdam')))
            # df_verwerkt2['hour'] = df_verwerkt2['time'].dt.hour
            df_verwerkt2['minutes'] = (df_verwerkt2['time'].dt.hour * 60) + df_verwerkt2['time'].dt.minute
            # df_verwerkt2['dayofweek'] = df_verwerkt2['time'].dt.dayofweek
            df_verwerkt2['difference'] = df_verwerkt2['value'].diff()
            df_verwerkt2['difference'] = df_verwerkt2['difference'].fillna(0)
            df_verwerkt2[df_verwerkt2['difference'] > 1000] = 0 # sprong naar Nederhoven uitfilteren
            df_verwerkt2 = df_verwerkt2[df_verwerkt2['difference'] > 0]
            
            # df_verwerkt2 = remove_outlier(df_verwerkt2, 'difference')
            
            df_verwerkt = pd.concat([df_verwerkt1, df_verwerkt2], ignore_index=True)
            
            groupby = df_verwerkt.groupby('minutes').sum()
            
        else:
            df_verwerkt = df.loc[(df['attributeName'] == usageType) & (df['time'] >= start_milliseconds) & (df['time'] <= stop_milliseconds)]
            df_verwerkt = df_verwerkt.sort_values('time')
            df_verwerkt = df_verwerkt.replace(0,np.NaN)
            df_verwerkt = df_verwerkt.fillna(method='ffill')
            df_verwerkt = df_verwerkt.fillna(method='bfill') # nodig om eerste rij te fixen.
            df_verwerkt['time'] = pd.to_datetime(df_verwerkt['time'], unit='ms', utc=True)
            df_verwerkt['time'] = df_verwerkt['time'].apply(lambda x: x.astimezone(timezone('Europe/Amsterdam')))
            # df_verwerkt['hour'] = df_verwerkt['time'].dt.hour
            df_verwerkt['minutes'] = (df_verwerkt['time'].dt.hour * 60) + df_verwerkt['time'].dt.minute
            # df_verwerkt['dayofweek'] = df_verwerkt['time'].dt.dayofweek
            df_verwerkt['difference'] = df_verwerkt['value'].diff()
            df_verwerkt['difference'] = df_verwerkt['difference'].fillna(0)
            df_verwerkt[df_verwerkt['difference'] > 1000] = 0 # sprong naar Nederhoven uitfilteren
            df_verwerkt = df_verwerkt[df_verwerkt['difference'] > 0]
            
            # df_verwerkt = remove_outlier(df_verwerkt, 'difference')
            
            groupby = df_verwerkt.groupby('minutes').sum()
        
        print('startdatum zoals verwerkt: ' + str(start))
        print('einddatum zoals verwerkt: ' + str(stop))
    
        return ColumnDataSource(data=groupby)
   
    def make_plot(src):
        
        # Deze regel maakt een dict met de vorm {0: '00:00', 1: '00:01', ... t/m 1440 voor alle minuten van de dag.
        # In feite zet deze regel alle minuten van 0 t/m 1440 om in een string met tijd voor de x-as.
        d = {i:f"{floor(i/60):02d}" + ":" + f"{int(i%60):02d}" for i in range(1440)}
        
        p = figure(title='Bar chart', x_range=(0, 1440), tools=TOOLS, background_fill_color="#fafafa")
        p.sizing_mode = 'stretch_both' # https://docs.bokeh.org/en/latest/docs/user_guide/layout.html
        p.vbar(x='minutes', bottom=0, top='difference', source=src, width=0.9, color={'field': 'difference', 'transform': color_mapper})

        p.y_range.start = 0
        p.xaxis.axis_label = 'Tijd'
        p.xaxis.major_label_overrides = d
        p.yaxis.axis_label = 'Verbruik'
        p.grid.grid_line_color="white"
        return p

    def update_radios(attr, old, new):
        
        # Get the selected items for the graph
        # ...
        selected = radio_button_group.active
        
        global usageType
        
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
        elif selected == 3:
            usageType = 'powertotalusage'
            p.title.text = 'Stroomverbruik totaal'
        
        print('Update usageType: ' + str(usageType))
       
        # update data
        new_src = make_dataset(df, usageType=usageType, start=start, stop=stop)
        src.data.update(new_src.data)
        
    def update_start_date(attr, old, new):
        
        print('New start date: ' + str(new))
        
        global start
        start = new
       
        # update data
        new_src = make_dataset(df, usageType=usageType, start=new, stop=stop)
        src.data.update(new_src.data)
        
    def update_end_date(attr, old, new):
        
        print('New stop date: ' + str(new))
        
        global stop
        stop = new
       
        # update data
        new_src = make_dataset(df, usageType=usageType, start=start, stop=new)
        src.data.update(new_src.data)

    radio_button_group = RadioButtonGroup(
        labels=["Gas", "Tarief 1", "Tarief 2", "Stroom totaal"], active=0)
    
    radio_button_group.on_change('active', update_radios)
    
    datepicker_start = DatePicker(title='Startdatum',min_date=date(2015,1,1),max_date=date.today())
    datepicker_stop = DatePicker(title='Einddatum',min_date=date(2015,1,1),max_date=date.today())
    
    datepicker_start.on_change('value', update_start_date)
    datepicker_stop.on_change('value', update_end_date)
    
    # initial execution
    src = make_dataset(df, 'gastotalusage')
    p = make_plot(src)
    
    # make a grid
    grid = gridplot([[p],[radio_button_group], [datepicker_start], [datepicker_stop]])
    grid.sizing_mode = 'scale_width'
    
    tab = Panel(child = grid, title = 'Bar chart')
    
    print("barchart() uitgevoerd")
   
    return tab