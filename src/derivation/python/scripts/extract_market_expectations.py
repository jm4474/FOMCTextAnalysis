#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Purpose: Computes the implied market expectations of MP from federal funds futures
Status: Draft
@author: olivergiesecke
"""
import pandas as pd
import numpy as np   

data_df=pd.read_csv('../output/daily_policy_data.csv')

# Get year and date
data_df['date']=pd.to_datetime(data_df["DATE"])
data_df['year']=data_df["date"].apply(lambda x:x.year)
data_df['month']=data_df["date"].apply(lambda x:x.month)

# Make pre 1994 adjustment
data_df.loc[data_df['year']<1994,'event_type']=data_df[data_df['year']<1994]['event_type'].shift(periods=1)
data_df=data_df[data_df['date'].notna()]
data_df['d_meeting']=data_df["event_type"]=="Meeting"

data_df=data_df[(data_df['year']>=1988) & (data_df['year']<2009)]
data_df=data_df[['DFEDTAR','DFF','FF1_COMDTY', 'FF2_COMDTY', 'end_date', 'event_type', 'date', 'year', 'month']]
# Make pre 1994 adjustment
data_df[data_df['year']<1994]=data_df[data_df['year']<1994].shift(periods=1)
data_df=data_df[data_df['date'].notna()]
data_df.loc[data_df['date']=="2003-09-15",'event_type']=np.nan
data_df.loc[data_df['date']=="2003-09-15",'end_date']=np.nan
# Define meeting / non-meeting months

data_df['d_meeting']=data_df["event_type"]=="Meeting"
aux_df=data_df[['d_meeting','year','month']].groupby(['year','month']).sum()
aux_df.rename(columns={"d_meeting":"n_meeting"},inplace=True)
aux_df['d_meeting_month']=aux_df['n_meeting']>0
data_df=data_df.merge(aux_df,how='outer',on=['year','month'])

# Merge the end of the month expected change 
aux_df=data_df[['date','DFEDTAR','FF2_COMDTY','FF1_COMDTY']]
aux_df['FF1_COMDTY']=aux_df['FF1_COMDTY'].fillna(method='ffill')
aux_df['FF2_COMDTY']=aux_df['FF2_COMDTY'].fillna(method='ffill')
aux_df['DFEDTAR']=aux_df['DFEDTAR'].fillna(method='ffill')
aux_df['expchange']=100-aux_df['FF2_COMDTY']-aux_df['DFEDTAR']

result_df = pd.Series(data_df['date']).dt.is_month_end 
aux_df=aux_df[['date','expchange']][result_df]
aux_df['year']=aux_df["date"].apply(lambda x:x.year)
aux_df['month']=aux_df["date"].apply(lambda x:x.month)
aux_df['lead_expchange']=aux_df['expchange'].shift(periods=1)

data_df=data_df.merge(aux_df[['lead_expchange','month','year']],how='outer',on=['year','month'])

#
from calendar import monthrange
data_df['days_month']=data_df["date"].apply(lambda x:monthrange(x.year, x.month)[1])
data_df['error_realized']=data_df['DFF']-data_df['DFEDTAR']
data_df['day']=data_df['date'].apply(lambda x:x.day)
# Calculate the one day before expected change

# Do iteration by month
startyear=int(data_df['year'].min())
endyear=int(data_df['year'].max())
phi=0.3

data_df["exp_change_wmeeting"]=0
data_df["meetday"]=0
for yr in range(startyear,endyear+1):
    print(yr)
    for mon in range(1,13):
        n_meeting=set(list(data_df[(data_df['month']==mon)&(data_df['year']==yr)]['n_meeting']))
        print(mon,'/',yr,':',n_meeting)
        if int(list(n_meeting)[0])>0:
            data_mon=data_df[(data_df['month']==mon)&(data_df['year']==yr)]
    
            meeting_days=list(data_mon["date"][data_mon['d_meeting']==True].apply(lambda x:x.day))
            kappa=monthrange(yr, mon)[1]
            
            total_exp=0
            for meet_day in meeting_days:
                mu=(meet_day-1)/kappa
                if meet_day>1:
                    avg_error_real = 1 / kappa * data_mon[data_mon['day']<meet_day]['error_realized'].sum()
                    exp_error = 1 / kappa * (phi * (1 - phi**(kappa-meet_day)))/(1 - phi) * data_mon[data_mon['day']==meet_day-1]['error_realized'].values[0]
                    target_before = data_mon[ data_mon['day'] == meet_day - 1 ]['DFEDTAR'].values[0]
                    fff_before = data_mon[ data_mon['day'] == meet_day - 1 ]['FF1_COMDTY'].values[0]
                
                    exp_change = 1 / (1 - mu) * (100 - fff_before - target_before) - 1 / ( 1 - mu ) * (avg_error_real + exp_error)
                
                else:

                    exp_change=0
                
                total_exp += exp_change
                
                print(total_exp)
                
            data_df.loc[(data_df['month']==mon)&(data_df['year']==yr),'exp_change_wmeeting']=total_exp
            data_df.loc[(data_df['month']==mon)&(data_df['year']==yr),'meetday']=meeting_days[-1]
            
data_df['meeting_day'] = data_df['date'][data_df['d_meeting']==True].apply(lambda x:x.day)

data_df.loc[(data_df['d_meeting_month'] == True) & (data_df['meetday']!=1 ),'market_exp']=data_df[ (data_df['d_meeting_month'] == True) & (data_df['meetday']!=1 ) ]['exp_change_wmeeting']
data_df.loc[(data_df['d_meeting_month'] == False)  ,'market_exp'] = data_df[ (data_df['d_meeting_month'] == False)  ]['lead_expchange']
data_df.loc[(data_df['d_meeting_month'] == True) & (data_df['meetday']==1 ),'market_exp']=data_df[ (data_df['d_meeting_month'] == True) & (data_df['meetday']==1 ) ]['lead_expchange']

data_monthly=data_df[['year','month','market_exp']].groupby(['year','month']).mean()
            
data_monthly.to_csv('../output/derived_monthly_market_exp.csv')
