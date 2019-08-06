#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
* Propensity Score 
* olivergiesecke
"""

import pandas as pd
import numpy as np

data_df=pd.read_csv('../../../collection/python/output/string_theory_indicators_monthly.csv')
data_df.rename(columns={'month':'date'},inplace=True)
data_df['date']=pd.to_datetime(data_df['DATE'])
data_df['month'] = data_df['date'].apply(lambda x: x.month)
data_df['year'] = data_df['date'].apply(lambda x: x.year)

# Get year and date
data_daily=pd.read_csv('../output/daily_policy_data.csv')
data_daily['date']=pd.to_datetime(data_daily["DATE"])
data_daily['year']=data_daily["date"].apply(lambda x:x.year)
data_daily['month']=data_daily["date"].apply(lambda x:x.month)

data_daily=data_daily[(data_daily['year']>=1988) & (data_daily['year']<2009)]
data_daily=data_daily[['DFEDTAR', 'end_date', 'event_type', 'date', 'year', 'month']]

# Make pre 1994 adjustment
data_daily.loc[data_daily['year']<1994,'event_type']=data_daily[data_daily['year']<1994]['event_type'].shift(periods=1)
data_daily=data_daily[data_daily['date'].notna()]

data_daily['d_meeting']=data_daily["event_type"]=="Meeting"
data_daily.loc[:,'lead_DFEDTAR'] = data_daily['DFEDTAR'].shift(periods=1)
data_daily['ch_DFEDTAR']=data_daily['DFEDTAR']-data_daily['lead_DFEDTAR'] 

data_pchanges = data_daily[data_daily['d_meeting']==True][['date', 'year', 'month','ch_DFEDTAR']]
data_pchanges = data_pchanges.dropna()

data_pchanges=data_pchanges.groupby(['year', 'month']).sum()

# Define meeting / non-meeting months

#
clean_data=data_df[['month','year']]
clean_data=clean_data.sort_values(by=['year', 'month'])
clean_data.loc[:,'lagged_prices']=data_df['PCEPI'].shift(periods=1)
clean_data.loc[:,'l1y_prices']=data_df['PCEPI'].shift(periods=13)
clean_data['lagged_infl']=(np.log(clean_data['lagged_prices'])-np.log(clean_data['l1y_prices']))*100

clean_data.loc[:,'lagged_unemp']=data_df['UNRATE'].shift(periods=1)

#
market_df=pd.read_csv('../output/derived_monthly_market_exp.csv')
clean_data=clean_data.merge(market_df[['year','month','market_exp']],how='outer',on=['year','month'])
clean_data=clean_data.merge(data_pchanges,how='outer',on=['year','month'])

clean_data=clean_data[(clean_data['year']>1988) & (clean_data['year']<=2008)]
clean_data=clean_data.dropna()
clean_data=clean_data.sort_values(by=['year', 'month'])
clean_data.rename(columns={'ch_DFEDTAR':'target_change'},inplace=True)

# Encode changes into a ordinal variable
outcomes=sorted(list(set(list(clean_data['target_change']))))

i=1
out_dict={}
for outcome in outcomes:
    out_dict.update({outcome:i})
    i+=1
    
clean_data['ord_policy']=clean_data['target_change'].map(out_dict)
clean_data.drop(columns=['lagged_prices', 'l1y_prices'],inplace=True)    

clean_data.to_csv('../output/matlab_file.csv')



