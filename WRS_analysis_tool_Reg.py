# -*- coding: utf-8 -*-
"""
@author: Michael Murphy
"""

# Wilcoxon Rank-sum calculator for environmental datasets. Input consists of pandas-readable flat file with 'PARAMNAME', 'Sys_Loc_Code', and 'Result'.
# Script parses unique pairs of locations ('Sys_Loc_Code') and for each pair-parameter combination, calculates Wilcoxon rank-sum comparison and tabulates results. 

import numpy as np
import pandas as pd
from bokeh.layouts import column, row, gridplot
from bokeh.plotting import figure, show, output_file
from bokeh.models import LinearAxis,  Range1d, ColumnDataSource, Label
import seaborn as sns
import matplotlib.pyplot as plt
import datetime as dt
import os
import itertools as itls
from scipy.stats import ranksums as rsums

### User-modified variables:
###############################################################################
# Update version suffix as needed: 
ver = "_01a"
# Update filename as needed:
f1 =  "Data.xlsx"
###############################################################################
df1 = pd.read_excel(f1)
print(df1.shape)
print(df1.head())
# Call today:
today1 = str(dt.date.today())

# Generate list of unique locations, parameters
locs_list = df1.Sys_Loc_Code.unique().tolist()
param_list = df1.PARAMNAME.unique().tolist()
# Generate list of tuples with unique combinations of two locations
comb_list = list(itls.combinations(locs_list, 2))

# Select first loc and param to build report dataframe:
loc0 = comb_list[0][0]
loc1 = comb_list[0][1]
param0 = param_list[0]

# Generate dataframes to calculate Wilcox Rank-Sums:
df1_loc0 = df1.loc[df1.Sys_Loc_Code==loc0].reset_index(drop=True)
df1_loc1 = df1.loc[df1.Sys_Loc_Code==loc1].reset_index(drop=True)
df1_loc_param0 = df1_loc0.loc[df1_loc0.PARAMNAME==param0].reset_index(drop=True)
df1_loc_param1 = df1_loc1.loc[df1_loc1.PARAMNAME==param0].reset_index(drop=True)

# Instantiate report  DataFrame (template)
df_rpt = pd.DataFrame()

# Calculate rank-sum for first pair:
ar0 = df1_loc0.Result
ar1 = df1_loc1.Result
rsums0 = rsums(ar0, ar1)
stat = np.around(rsums0.statistic, 3)
pval = rsums0.pvalue 
pair_id = '_'.join([loc0, loc1])
if pval < 0.05:
    sig = 'True'
else:
    sig = 'False'

df_rpt = pd.DataFrame(columns=["Pair_ID", "Parameter",  "Wilcoxon_ranksum_Stat", "P-value", "Significant"])
df_rpt = df_rpt.append({"Pair_ID":pair_id, "Parameter":param0, "Wilcoxon_ranksum_Stat":stat, "P-value":pval, "Significant":sig }, ignore_index=True)


# Iterate through params, combinations to generate summary report
for p in param_list:
    df1_p = df1.loc[df1.PARAMNAME==p].reset_index(drop=True)

    for n in range(1, len(comb_list)):
        loc0 = comb_list[n][0]
        loc1 = comb_list[n][1]
        # Generate dataframes to calculate Wilcox Rank-Sums:
        df1_loc0 = df1_p.loc[df1_p.Sys_Loc_Code==loc0].reset_index(drop=True)
        df1_loc1 = df1_p.loc[df1_p.Sys_Loc_Code==loc1].reset_index(drop=True)
        # Calculate rank-sum for each pair:
        ar0 = df1_loc0.Result
        ar1 = df1_loc1.Result
        rsums0 = rsums(ar0, ar1)
        stat = np.around(rsums0.statistic, 3)
        pval = rsums0.pvalue 
        pair_id = '_'.join([loc0, loc1])
        if pval < 0.05:
            sig = 'True'
        else:
            sig = 'False'
        df_rpt = df_rpt.append({"Pair_ID":pair_id, "Parameter":p, "Wilcoxon_ranksum_Stat":stat, "P-value":pval, "Significant":sig }, ignore_index=True)
print(df_rpt.head())
print(df_rpt.shape)

writer = pd.ExcelWriter('Wilcoxon_rank-sum_report_' + today1 + ver +'.xlsx')
df_rpt.to_excel(writer, 'WRS_RPT')
writer.save()   

"""
