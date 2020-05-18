# -*- coding: utf-8 -*-
"""
Created on Tue Apr 21 12:09:04 2020

@author: Michael Murphy
"""

# Mann-Kendall trend analysis script. 
# TODO: Add title for html Bokeh plots'
# TODO: change coding of text boxes so that they import with png output
import numpy as np
import pandas as pd
from bokeh.layouts import column, row, gridplot
from bokeh.plotting import figure, show, output_file
from bokeh.models import LinearAxis,  Range1d, ColumnDataSource, Label, Title
import seaborn as sns
import matplotlib.pyplot as plt
import datetime as dt
import os
import pymannkendall as mk

### User-modified variables:
###############################################################################
# Update version suffix as needed: 
ver = "_Ricoh_01a"
# Update filename as needed:
f1 =  "LChem_Mann-Kendall_Query.xlsx"
###############################################################################
# Call today:
today1 = str(dt.date.today())
# Create path for output files, if path does not exist:
cwd1 = os.getcwd()
new_path = "MK-Trends_" + today1 + ver
if os.path.exists(new_path) == False:
    os.mkdir(new_path)

df1 = pd.read_excel(f1, infer_datetime_format=True)
print(df1.shape)
print(df1.head())

# Get list of unique locations, parameters:
locs_list = df1.LocCode.unique().tolist()
param_list = df1.ChemName.unique().tolist()
# Select first loc and param to build report dataframe:
loc0 = locs_list[0]
param0 = param_list[0]
# Generate dataframe to calculate M-K trends:
df1_loc0 = df1.loc[df1.LocCode==loc0]
df1_loc_param0 = df1_loc0.loc[df1_loc0.ChemName==param0]
# Calculate M-K trend:
mk_trend = mk.original_test(df1_loc_param0.Result)
trend_pred = mk_trend.trend
h_bool = mk_trend.h
p_val = mk_trend.p
z_val = mk_trend.z
k_tau = mk_trend.Tau
mk_score = mk_trend.s
var_s = mk_trend.var_s
sen_slope = mk_trend.slope
# Set other params:
dt_range = df1_loc_param0["Sampled_Date-Time"].min().strftime("%Y%m") + "-" + df1_loc_param0["Sampled_Date-Time"].max().strftime("%Y%m")
samp_count = str(len(df1_loc_param0))
u_count = str(len(df1_loc_param0.loc[df1_loc_param0.screen_qual == "U"]))
res_min = str(df1_loc_param0.Result.min())
res_max = str(df1_loc_param0.Result.max())
res_mean = str(df1_loc_param0.Result.mean())

# Generate new report dataframe to populate with for-loops
df_rpt = pd.DataFrame(columns=["Parameter", "Location", "Date_Range", "Samp_count", "U_count",  "Res_min", "Res_max", \
                               "Res_mean", "Predicted_Trend", "Trend_bool",\
                               "P_value", "M-K_score"])
df_rpt = df_rpt.append({"Parameter":param0, "Location":loc0, "Date_Range":dt_range, "Samp_count":samp_count, "U_count":u_count,  "Res_min":res_min, "Res_max":res_max, \
                               "Res_mean":res_mean, "Predicted_Trend":trend_pred, "Trend_bool":h_bool,\
                               "P_value":p_val, "M-K_score":mk_score}, ignore_index=True)
os.chdir(new_path)
# Append additional M-K values to existing report dataframe where there are at least 10 results and greater than 50% detections:
for loc in locs_list[1:]:
    df2_loc0 = df1.loc[df1.LocCode==loc]
    for param in param_list[1:]:
        df2_loc_param0 = df2_loc0.loc[df2_loc0.ChemName==param]
        if (len(df2_loc_param0) >= 10):
            # TODO: Get this to work:
            #ratio_d_nd = ((len(df2_loc_param0) / len(df2_loc_param0.loc[df2_loc_param0.screen_qual == "U"]))
            #if ratio_d_nd >= 0.5:
            mk_trend = mk.original_test(df2_loc_param0.Result)
            trend_pred = mk_trend.trend
            h_bool = mk_trend.h
            p_val = mk_trend.p
            z_val = mk_trend.z
            k_tau = mk_trend.Tau
            mk_score = mk_trend.s
            var_s = mk_trend.var_s
            sen_slope = mk_trend.slope
            # Set other params:
            dt_range = df2_loc_param0["Sampled_Date-Time"].min().strftime("%Y%m") + "-" + df2_loc_param0["Sampled_Date-Time"].max().strftime("%Y%m")
            samp_count = str(len(df2_loc_param0))
            u_count = str(len(df2_loc_param0.loc[df2_loc_param0.screen_qual == "U"]))
            res_min = df2_loc_param0.Result.min()
            res_max = df2_loc_param0.Result.max()
            res_mean = df2_loc_param0.Result.mean()
            # Append df_rpt with new values:
            df_rpt = df_rpt.append({"Parameter":param, "Location":loc, "Date_Range":dt_range, "Samp_count":samp_count, "U_count":u_count,  "Res_min":res_min, "Res_max":res_max, \
                                           "Res_mean":res_mean, "Predicted_Trend":trend_pred, "Trend_bool":h_bool,\
                                           "P_value":p_val, "M-K_score":mk_score}, ignore_index=True)
            if trend_pred == "increasing":
                p1 = figure(width=1000, height=775, title = param + " vs. Time in " + loc + ", " + dt_range, x_axis_type="datetime", \
                        y_axis_label= param, x_axis_label= "Sample Date")
                p1.y_range = Range1d((res_min)-1, (res_max)+1)
                p1.asterisk(df2_loc_param0["Sampled_Date-Time"], df2_loc_param0.Result, color="red", size=12, legend_label = loc)
                trend_rpt = Label(x=50, y=50, x_units='screen', y_units='screen', text="Calculated M-K Trend: " + trend_pred + "; Calculated p-value: " + str(p_val), border_line_color='black', border_line_alpha=1.0, background_fill_color='white', background_fill_alpha=0.5)
                p1.add_layout(trend_rpt)
                copyright1 = Title(text="Programmed by Michael J. Murphy, 2020", text_font_style='italic', text_font_size = '8pt')
                p1.add_layout(copyright1, 'right')
                
                output_file("trend_plot_"+ loc + "_"+ param +  ".html")
                show(p1)
                
#df_rpt = df_rpt.reset_index(inplace=True)
               
writer = pd.ExcelWriter('Mann_Kendall_Trend_report_' + today1 + ver +'.xlsx')
df_rpt.to_excel(writer, 'MK_trends')
writer.save()            
os.chdir(cwd1)       
# TODO: Add plots            
"""
analyte_list = ["Barium", "Chromium", "Chromium VI", "Mercury", "Zinc", "Vanadium"]
color_list = ["blue", "orange", "red", "gray", "purple", "green"]
df3 = df2 #.loc[df2.analyte.isin(analyte_list)]
analyte_list1 = df3.analyte.unique().tolist()
df3["max_conc"] = 0
for a in analyte_list1:
    df3.loc[df3.analyte == a, 'max_conc'] = df3.loc[df3.analyte == a].res_num.max()
df3["res_norm"] = df3.res_num / df3.max_conc
df3["date_ordinal"] = df3.date_dt.map(dt.datetime.toordinal)
#g1 = sns.FacetGrid(df3, row="Well_ID1", col="analyte", hue ="analyte", height=4)
#g1.map(plt.scatter, "date_dt", "res_norm")


#g2 = sns.lmplot("date_ordinal", "res_norm", row="Well_ID1", col="analyte", data=df3, hue ="analyte", height=4)
#g2.map(plt.scatter, "date_dt", "res_norm")
df4 = df3[['Well_ID1', 'Date', 'date_dt', 'date_ordinal', 'qtr_ID', 'sample_ID',
       'analyte', 'result', 'res_num', 'flag', 'd_nd', 'res_rand',
       'rand_multiplier', 'max_conc', 'res_norm']]
#df_Cr = df4.loc[df4.analyte == "Chromium"]


ver = '_01d'
today1 = str(dt.date.today())
new_path = "EDA_plots_" + today1 + ver
if os.path.exists(new_path) == False:
    os.mkdir(new_path)
cwd1 = os.getcwd()
os.chdir(new_path)
for l in loc_list:
    df4_loc = df4.loc[df4.Well_ID1 == l]
    df_gwe = df1_gwe.loc[df1_gwe.well_id == l].sort_values(by=["date_dt"])
    title2 = "GWE vs. Time in " + l
    for a, c in zip(analyte_list, color_list):
        df_metal = df4_loc.loc[df4_loc.analyte == a].sort_values(by=["date_dt"])
        title1 = a + ", "
        ylabel = a + " mg/L"
        metal = ColumnDataSource(df_metal)
        gwe = ColumnDataSource(df_gwe)
        mk_trend = mk.seasonal_test(df_metal.res_rand)
        trend1 = mk_trend.trend
        trend2 = mk_trend.p
        trend_rpt = Label(x=50, y=50, x_units='screen', y_units='screen',
                 text="Predicted M-K Trend (seasonal): " + trend1 +"; Calculated p-value: " + str(trend2), render_mode='css',
                 border_line_color='black', border_line_alpha=1.0,
                 background_fill_color='white', background_fill_alpha=0.5)
        p1 = figure(width=1000, height=775, title = title1 + title2, x_axis_type="datetime", \
                                y_axis_label= ylabel, x_axis_label= "Sample Date")
        p1.y_range = Range1d(df_metal.res_num.min()-1, df_metal.res_num.max()+1)
        p1.asterisk(df_metal.date_dt, df_metal.res_rand, color=c, size=13, legend_label = a)    
        p1.extra_y_ranges = {"rng_gwe": Range1d(start = df_gwe.gwe_ft_amsl.min()-1, end = df_gwe.gwe_ft_amsl.max()+1 )}
        p1.add_layout(LinearAxis(y_range_name="rng_gwe", axis_label='GWE ft amsl'), 'right')
        p1.line(df_gwe.date_dt, df_gwe.gwe_ft_amsl, y_range_name='rng_gwe', legend_label= "GWE")
        p1.inverted_triangle(df_gwe.date_dt, df_gwe.gwe_ft_amsl, y_range_name='rng_gwe', legend_label= "GWE")
        p1.add_layout(trend_rpt)
        output_file("trend_plot_"+ l + "_"+ a + "_gwe" + ".html")
        show(p1)
os.chdir(cwd1)        
        
        

# Generate bokeh plots:


writer = pd.ExcelWriter('Table_6_total_metals_long_fmt_processed_' + today1 + ver +'.xlsx')
df4.to_excel(writer, 'Data')
writer.save()

#plt.show()
"""