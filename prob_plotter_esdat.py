# -*- coding: utf-8 -*-
"""
Created on Thu Jul  9 19:04:34 2020

@author: Michael
"""
# Updated prob_plot script using ESDat ProUCL output

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import seaborn_qqplot as sqp
from scipy.stats import norm, gamma, probplot
import pylab
import scipy.stats as stats
import os
from datetime import date
from bokeh.plotting import figure, output_file, show, ColumnDataSource
from bokeh.models import Title 

df0 = pd.read_excel('bg_metals_pplot_test_data.xlsx')
print(df0.head())
print(df0.shape)

# TODO: Change dataframe to long tidy format DONE!
df1 = pd.melt(df0, id_vars=["Field_ID", "LocCode", "Matrix_Description"], var_name="analyte", value_name="res_num").reset_index(drop=True)
print(df1.head())
print(df1.shape)

cols_list = df1.columns.tolist()
analyte_list = [i for i in df1.analyte.unique().tolist() if i[:2] != "D_"]

# TODO: Change data selection and plotting in Test/POC to work interatively 

for a in analyte_list:
    dfa = df1.loc[df1.analyte==a].reset_index(drop=True)
    dfa["d_nd"] = df1.res_num.loc[df1.analyte=="D_" + a].reset_index(drop=True)
    dfa1 = dfa.sort_values(by="res_num")
    p1 = probplot(dfa1["res_num"], plot=None, fit=True, dist='norm')
    # Extract values from probplot tuples:
    x = p1[0][0] # Array of calculated theoretical quantiles
    y = p1[0][1] # Array of ordered values
    m = p1[1][0] # Calclulated slope
    b = p1[1][1] # Calculated intercept
    r = p1[1][2] # Calculated value of R
    y_pred = [m*i + b for i in x] # Calculate y_predicted
    
    dfa1["quantiles"] = x
    
    source = ColumnDataSource(dfa1)
    TOOLTIPS = [("Sample ID", "@Field_ID"), ("Result (mg/kg)", "@res_num")]
    # Generate bokeh plots
    plot1 = figure(width=1000, height=750, title="Probability Plot, " + a + " "+ "(" + dfa1["Matrix_Description"][0] + ")", \
               x_axis_label="Theoretical Quantiles (Standard Normal)", \
                   y_axis_label="Ordered Values for " + a + " (mg/kg)", \
                       y_range=(0, dfa1.res_num.max() + dfa1.res_num.mean()/10), tooltips=TOOLTIPS)

    plot1.diamond('quantiles', "res_num", color='blue', source=source, size=8, alpha=0.6, legend_label=a)
    copyright1 = Title(text="Michael J. Murphy, 2020", text_font_style='italic', align='right', text_font_size = '7pt')
    plot1.add_layout(copyright1, 'right')
    plot1.line(x, y_pred, color='black', legend_label= "y="+str(round(m, 2))+"x" + " + " + str(round(b, 2)) + "; " + "R=" + str(round(r, 3)) )
    plot1.legend.location = "top_left"

    show(plot1)




"""
## Test/POC for individual analytes
# Set test df subset
df2 = df0["Cadmium"]

p1 = probplot(df0["Cadmium"], plot=None, fit=True, dist='norm')

x = p1[0][0] # Array of calculated theoretical quantiles
y = p1[0][1] # Array of ordered values
m = p1[1][0] # Calclulated slope
b = p1[1][1] # Calculated intercept
r = p1[1][2] # Calculated value of R
y_pred = [m*i + b for i in x] # Calculate y_predicted


# Generate bokeh plots
plot1 = figure(width=750, height=500, title="Probability Plot, " + df2.name + " "+ "(" + df0.Matrix_Description[0] + ")", \
               x_axis_label="Theoretical Quantiles (Standard Normal)", y_axis_label="Ordered Values for " + df2.name + " (mg/kg)", y_range=(0, df2.max() + 5))

plot1.diamond(x, y, color='darkred', legend_label=df2.name)
copyright1 = Title(text="Michael J. Murphy, 2020", text_font_style='italic', align='right', text_font_size = '7pt')
plot1.add_layout(copyright1, 'right')
plot1.line(x, y_pred, color='red', legend_label= "y="+str(round(m, 2))+"x" + " + " + str(round(b, 2)) + "; " + "R=" + str(round(r, 3)) )
plot1.legend.location = "top_left"

show(plot1)
"""