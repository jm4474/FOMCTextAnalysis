#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
* Purpose: Import the federal funds future data and analyse the match with the 
           with the statements from the bluebooks.
@author: olivergiesecke
"""
import pandas as pd
import re
import os
import numpy as np
import matplotlib.pyplot as plt

### Read the effective federal funds future data

ffr_raw=pd.read_excel("../data/NYF_effective_federal_funds_data.xls",skiprows=4)
ffr=ffr_raw[['EFFR\n(PERCENT)','DATE']]
ffr.rename(columns={'EFFR\n(PERCENT)':'effr','DATE':'date'},inplace=True )    
ffr=ffr[ffr.index<4648]

def tranform_date(date):
    return re.search('(\d{4}\-\d{2}\-\d{2})([\[r\]]*)',date,re.IGNORECASE).group(1)

ffr.loc[:,'date']=ffr.loc[:,'date'].apply(tranform_date)
ffr['date'] = pd.to_datetime(ffr['date'])

### Open the csv

data=pd.read_excel("../data/FFF_1m3m_extract.xlsx")
data['date'] = pd.to_datetime(data['date'])

data=data.merge(ffr,how='left',on='date')


######

data['diff']= data['date'].diff(periods=-1)
data['diff']=-data['diff']/pd.Timedelta(1, unit='d')

data['month']=data['date'].apply(lambda x: x.month)
data['year']=data['date'].apply(lambda x: x.year)


def get_cont_ffr_exp(date,data):
    print(date)
    month=date.month
    year=date.year
    day=date.year
    
    # effective future series
    newdata=data[(data['month']==month) & (data['year']==year) & (data['date']<=date)][['date','diff','effr']]
    newdata['effr']=newdata['effr'].astype(float)
    newdata['diff']=newdata['diff'].astype(int)
    newdata['w_effr']=newdata['diff']*newdata['effr']
    
    FFF_0=data[data['date']==date]['FFF_0'].item()
    print(FFF_0)
    
    if newdata[newdata['effr'].notna()]['diff'].sum()==0:
        ffr_future=np.nan
    else:  
        ffr_past=newdata['w_effr'].sum(skipna=True)/newdata[newdata['effr'].notna()]['diff'].sum()
    
        acc_factor=30/(30-day)
    
        ffr_future=acc_factor*(1-FFF_0/100)+(1-acc_factor)*ffr_past/100
    
    print(ffr_future)
    return ffr_future

data.loc[:,"ffr_future"]=np.nan
for idx,row in data.iterrows():
    date=row['date']
    ffr_future=get_cont_ffr_exp(date,data)
    data.loc[idx,"ffr_future"]=ffr_future





#######

columns=data.columns
rates=pd.DataFrame(data['date'])
ffrs=['FFF_0', 'FFF_1', 'FFF_2', 'FFF_3', 'FFF_4', 'FFF_5', 'FFF_6']
for fff_price in ffrs:
    variable=fff_price+'_rate'
    rates.loc[:,variable]=100-data[fff_price]
    
### Plot the expected average federal funds rate at different horizons

date="1995-12-18"
date2="1995-12-19"

rate=[]
rate2=[]
for fff_price in ffrs:
    rate.append(rates[rates['date']==date][fff_price+'_rate'].item())
    rate2.append(rates[rates['date']==date2][fff_price+'_rate'].item())

plt.plot(rate)
plt.plot(rate2)
plt.ylabel('implied federal funds rate (in %)')
plt.xlabel('months into future')
plt.show()





