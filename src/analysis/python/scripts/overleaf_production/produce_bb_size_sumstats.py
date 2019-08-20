"""
Purpose: Summarizes the treatment size alternatives of the bluebooks
Status: Final -- 06/27/2019
@author: olivergiesecke
"""

###############################################################################
### Set packages ###

import pandas as pd
import re
import matplotlib.pyplot as plt
import numpy as np
from obtain_sumstats_bb_options import create_totstat, create_sumstat_byperiod

###############################################################################

### Create the summary statistics including the size.

def main():
    data_sumstats=prepare_data(1988,2008)
    create_totstat(data_sumstats,'tab_sumstat_sizeoptions')
    #turning_points=['1989-06-01','1993-06-01','1995-04-01','2000-11-01','2004-01-01','2007-02-01']
    #create_sumstat_byperiod(data_sumstats,turning_points,'tab_sumstats_sizeoptions_byperiod')

    #data_graphs=produce_data_graph(1988,2008)
    # Plot individual meeting
    #datestring="2002-11-06"
    #produce_graph(data_graphs,datestring)


def prepare_data(startdate,enddate):
    data=pd.read_excel("../../data/bluebook_manual_data_online_WORKING.xlsx")
    data['year']=data['start_date'].apply(lambda x : x.year)
    data=data[(data['year']>=startdate) & (data['year']<=enddate)]
    data['start_date']=pd.to_datetime(data['start_date'])   
    data['end_date']=pd.to_datetime(data['end_date'])   
    data=data.reset_index()
    
    treatments=[]    
    for alt in ['a','b','c','d','e']:
        try:
            treatments+=data['C_TREATMENT_SIZE_alt_'+alt].unique().tolist()
        except:
            print('No option found')
    treatments=list(set(treatments))
    
    data.loc[:,'treatment_options']=np.nan
    data.loc[:,'treatment_options']=data.loc[:,'treatment_options'].astype('object')
    for idx,row in data.iterrows():
        treatments=[]    
        for alt in ['a','b','c','d','e']:
            try:
                treatments.append(row['C_TREATMENT_SIZE_alt_'+alt])
            except:
                print('No option found')
           
        filtered_treatments=[]
        for treatment in treatments:
            
            try:
                if not re.search('\?',str(treatment)):
                    if not np.isnan(treatment):
                        if isinstance(treatment, int) or isinstance(treatment, float):
                            filtered_treatments.append(treatment)
            except:
                pass
        filtered_treatments=", ".join([str(x) for x in sorted(filtered_treatments)])
        print(filtered_treatments)
        if not len(filtered_treatments)==0:
            data['treatment_options'].iloc[idx]=filtered_treatments
    return data
    

def produce_data_graph(startdate,enddate):
    data=pd.read_excel("../../data/bluebook_manual_data_online_WORKING.xlsx")
    data['year']=data['start_date'].apply(lambda x : x.year)
    data=data[(data['year']>=startdate) & (data['year']<=enddate)]
    data['start_date']=pd.to_datetime(data['start_date'])   
    data['end_date']=pd.to_datetime(data['end_date']) 
    data=data.reset_index()
    
    treatments=[]    
    for alt in ['a','b','c','d','e']:
        try:
            treatments+=data['C_TREATMENT_SIZE_alt_'+alt].unique().tolist()
        except:
            print('No option found')
    treatments=list(set(treatments))
    
    data.loc[:,'treatment_options']=np.nan
    data.loc[:,'treatment_options']=data.loc[:,'treatment_options'].astype('object')
    for idx,row in data.iterrows():
        treatments=[]    
        for alt in ['a','b','c','d','e']:
            try:
                treatments.append(row['C_TREATMENT_SIZE_alt_'+alt])
            except:
                print('No option found')
           
        filtered_treatments=[]
        for treatment in treatments:
            
            try:
                if not re.search('\?',str(treatment)):
                    if not np.isnan(treatment):
                        if isinstance(treatment, int) or isinstance(treatment, float):
                            if treatment==0:
                                filtered_treatments.append(treatment+0.01)
                            else:
                                filtered_treatments.append(treatment)
            except:
                pass
        print(filtered_treatments)
        if not len(filtered_treatments)==0:
            data['treatment_options'].iloc[idx]=filtered_treatments
        else:
            pass
        
    return data


def produce_graph(data,datestring):
    ind_meeting_data=data[data['end_date']==pd.to_datetime(datestring)]
    title= "Meeting "+ pd.Series(ind_meeting_data['start_date']).dt.strftime('%Y-%m-%d').item()+" - "+\
            pd.Series(ind_meeting_data['end_date']).dt.strftime('%Y-%m-%d').item()
    treatment_sizes=ind_meeting_data['treatment_options'].item()
    treatment_sizes=sorted(treatment_sizes)
    index=[]
    name=[]
    for i in range(1,len(treatment_sizes)+1):
        index.append(i)
        name.append("Alternative "+str(i))
    
    plt.rc('text', usetex=True)
    fig = plt.figure(figsize=(4, 6))
    ax = fig.add_subplot(1, 1, 1)
    ax.bar(index,treatment_sizes,align='center',width =.4)
    ax.set_xticks(index, name)
    ax.set_ylim(-1,1)
    ax.axhline(color='gray',ls="--")
    ax.set_title(title)
    plt.savefig('../../output/fig_policy_option_'+datestring+'.png', dpi=300,bbox_inches='tight')
    
if __name__ == "__main__":
   main()

