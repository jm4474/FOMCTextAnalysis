"""
Purpose: Summarizes the alternatives of the bluebooks
Status: Final -- 06/27/2019
@author: olivergiesecke
"""

###############################################################################
### Set packages ###

import pandas as pd
import re
import os
import matplotlib.pyplot as plt
import numpy as np


###############################################################################

def main():    
    dataffr=construct_dataset(1988,2008)
    plot_target(dataffr)
    
    data=load_bluebook_data(1988,2008)
    create_totstat(data,'tab_sumstats_menu')
    
    create_sumstat_byyear(data,'tab_sumstats_menu_byyear')
    
    turning_points=['1989-06-01','1993-06-01','1995-04-01','2000-11-01','2004-01-01','2007-02-01']
    create_sumstat_byperiod(data,turning_points,'tab_sumstats_menu_byperiod')



def create_totstat(data,name):
    sum_menu=pd.pivot_table(data,values='end_date',index='treatment_options',aggfunc=np.count_nonzero,fill_value=0)
    sum_menu=sum_menu.reset_index()
    sum_menu.rename(columns={"end_date":"count"},inplace=True)
    sum_menu=sum_menu.append({'treatment_options':'Total','count':sum_menu['count'].sum()},ignore_index=True)
    
    ### Export the dataframe to latex
    # Dictionary for column headers
    headers={"treatment_options":"Policy Options","count":"Number of Meetings"}
    sum_menu.rename(columns=headers,inplace=True)
    
    create_table_df(sum_menu,name)
    print("Table",name,"is written." )


def create_table_df(data,name):
    columnheaders=list(data.columns)
    numbercolumns=len(columnheaders)
    
    with open("../output/"+name+".tex", "w") as f:
        f.write(r"\begin{tabular}{"+"l" + "".join("c" * (numbercolumns-1)) + "}\n")
        f.write("\\hline\\hline \n")
        f.write("\\addlinespace"+" \n")
        f.write(" & ".join([str(x) for x in columnheaders]) + " \\\ \n")    
        f.write("\\hline \n")
        # write data
        for idx,row in data.iterrows():
            # Do formatting for specific tables 
            if row.iloc[0]=="Total":
                f.write("\\addlinespace"+" \n")
            
            f.write(" & ".join([str(x) for x in row.values]) + " \\\\\n")   
    
        f.write("\\hline \n")
        f.write(r"\end{tabular}")


def construct_dataset(startyear,endyear):
    ffr=pd.read_excel("../../../collection/python/data/FRED_DFEDTAR.xls",skiprows=10)
    ffr.rename(columns={"observation_date":"date","DFEDTAR":"ffrtarget"},inplace=True)
    ffr['year']=ffr['date'].apply(lambda x: x.year)
    ffr=ffr[(ffr['year']>=startyear) & (ffr['year']<=endyear)]
    return ffr


def plot_target(dataffr):
    dataffr[dataffr['year']==1990]
    
    ### Get turning points
    dataffr.reset_index(inplace=True)
    
    t_point=dataffr[dataffr['ffrtarget'].diff(1)!=0]
    t_point[t_point['year']==2007]
    
    plt.rc('text', usetex=True)
    fig = plt.figure(figsize=(10, 3))
    ax = fig.add_subplot(1, 1, 1)
    ax.plot(dataffr['date'],dataffr['ffrtarget'], color='blue', ls='solid')
    
    turning_points=['1989-06-01','1993-06-01','1995-04-01','2000-11-01','2004-01-01','2007-02-01']
    for datestring in turning_points:
        ax.axvline(x=pd.to_datetime(datestring), color='gray', linestyle='--')
    
    plt.legend(['Federal Funds Target'],frameon=False)
    plt.savefig('../output/fig_fed_target.png', dpi=300,bbox_inches='tight')
    print('fig_fed_target.png is written')
    
def load_bluebook_data(startyear,endyear):
    data=pd.read_excel("../data/bluebook_manual_data_online_WORKING.xlsx")
    data['year']=data['start_date'].apply(lambda x : x.year)
    data=data[(data['year']>=startyear) & (data['year']<=endyear)]
    data=data.reset_index()
    
    treatments=[]    
    for alt in ['a','b','c','d','e']:
        try:
            treatments+=data['C_TREATMENT_alt_'+alt].unique().tolist()
        except:
            print('No option found')
    treatments=list(set(treatments))
    
    data.loc[:,'treatment_options']=np.nan
    for idx,row in data.iterrows():
        treatments=[]    
        for alt in ['a','b','c','d','e']:
            try:
                treatments+=row['C_TREATMENT_alt_'+alt]
            except:
                print('No option found')
        
        notvalid_treatments=['N']
        treatments=[x for x in treatments if not x in notvalid_treatments]
        treatment_tuple=tuple(set(treatments))
        treatments=",".join(list(set(treatments)))
        #print(treatments)
        #print(idx)
        if not len(treatment_tuple)==0:
            data['treatment_options'].iloc[idx]=treatments
        else:
            pass
    return data


def create_sumstat_byyear(data,name):
    sum_menu_byyear=pd.pivot_table(data,values='end_date',index='treatment_options',columns='year',aggfunc=np.count_nonzero,fill_value=0)
    sum_menu_byyear=sum_menu_byyear.reset_index()
    
    addline={'treatment_options':'Total'}
    for item in list(sum_menu_byyear.columns)[1:]:
        addline.update({item:sum_menu_byyear[item].sum() })
    
    sum_menu_byyear=sum_menu_byyear.append(addline,ignore_index=True)
    
    ### Export the dataframe to latex
    # Dictionary for column headers
    headers={"treatment_options":"Policy Options"}
    sum_menu_byyear.rename(columns=headers,inplace=True)
    create_table_df(sum_menu_byyear,name)
    print("Table",name,"is written." )


def create_sumstat_byperiod(data,turning_points,name):
    data.loc[:,'period']=""
    data.loc[data['start_date']<=pd.to_datetime(turning_points[0]),'period']='pre '+turning_points[0]
    
    for i in range(len(turning_points)-1):    
        data.loc[(data['start_date']>pd.to_datetime(turning_points[i])) & (data['start_date']<=pd.to_datetime(turning_points[i+1])),'period']='\\shortstack{'+turning_points[i]+'- \\\ '+turning_points[i+1]+'}'
    
    data.loc[data['start_date']>=pd.to_datetime(turning_points[-1]),'period']='post '+turning_points[-1]
        
    sum_menu_period=pd.pivot_table(data,values='end_date',index='treatment_options',columns='period',aggfunc=np.count_nonzero,fill_value=0)
    sum_menu_period=sum_menu_period.reset_index()
    
    addline={'treatment_options':'Total'}
    for item in list(sum_menu_period.columns)[1:]:
        addline.update({item:sum_menu_period[item].sum() })
    
    cols = list(sum_menu_period)
    # move the column to head of list using index, pop and insert
    cols.insert(1, cols.pop(cols.index(cols[-1])))
    sum_menu_period=sum_menu_period[cols]
    
    sum_menu_period=sum_menu_period.append(addline,ignore_index=True)
    
    ### Export the dataframe to latex
    # Dictionary for column headers
    headers={"treatment_options":"Policy Options"}
    sum_menu_period.rename(columns=headers,inplace=True)
    create_table_df(sum_menu_period,name)
    print("Table",name,"is written." )


if __name__ == "__main__":
   main()
