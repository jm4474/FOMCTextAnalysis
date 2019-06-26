
"""
Purpose: Import the federal funds future data, and the effective federal funds
         and adjust the current month for the day of the month on which the meeting
         taked place. Then, it allows for the plot of the federal funds future 
         curve around the meeting days.
Status: Final -- 06/26/2019
@author: olivergiesecke
"""

###############################################################################
### Import packages
import pandas as pd
import re
import os
import numpy as np
import matplotlib.pyplot as plt
from calendar import monthrange
###############################################################################

### Read the effective federal funds future data
# =============================================================================
# # this is only needed for the raw data from the Fed NY
# ffr_raw=pd.read_excel("../data/NYF_effective_federal_funds_data.xls",skiprows=4)
# ffr=ffr_raw[['EFFR\n(PERCENT)','DATE']]
# ffr.rename(columns={'EFFR\n(PERCENT)':'effr','DATE':'date'},inplace=True )    
# ffr=ffr[ffr.index<4648]
# 
# def tranform_date(date):
#     return re.search('(\d{4}\-\d{2}\-\d{2})([\[r\]]*)',date,re.IGNORECASE).group(1)
# ffr.loc[:,'date']=ffr.loc[:,'date'].apply(tranform_date)
# =============================================================================

def main():
    data=construct_dataset()
    data=define_adjusted_future(data)
    rates=reshape_data(data)
    datestring="2002-11-06"
    create_plot(rates,datestring)
    

def construct_dataset():
    ffr=pd.read_excel("../data/FRED_DFF.xls",skiprows=10)
    ffr.rename(columns={"observation_date":"date","DFF":"effr"},inplace=True)
    
    ffr['date'] = pd.to_datetime(ffr['date'])
    
    ### Merge with the futures data
    data=pd.read_excel("../data/FFF_1m3m_extract.xlsx")
    data['date'] = pd.to_datetime(data['date'])
    
    data=data.merge(ffr,how='left',on='date')
    
    ### Do some data cleaning
    data['diff']= data[data['effr'].notna()]['date'].diff(periods=1)
    data['diff']=-data['diff']/pd.Timedelta(1, unit='d')
    
    data['month']=data['date'].apply(lambda x: x.month)
    data['year']=data['date'].apply(lambda x: x.year)
    return data


def define_adjusted_future(data):
    data.loc[:,"ffr_future"]=np.nan
    for idx,row in data.iterrows():
        date=row['date']
        print('Execute date: ',date)
        if date.year < 2014 and date.year >= 1990:
            ffr_future=get_cont_ffr_exp(date,data)
            data.loc[idx,"ffr_future"]=ffr_future
        else:
            data.loc[idx,"ffr_future"]=np.nan
    return data


def get_cont_ffr_exp(date,data):
    #print(date)
    month=date.month
    year=date.year
    day=date.day
    
    days=monthrange(year, month)
    totdaysinmonth=days[1]
    
    # effective future series
    newdata=data[(data['month']==month) & (data['year']==year) & (data['date']<=date)][['date','diff','effr']]
    newdata['effr']=newdata['effr'].astype(float)
    
    if newdata[newdata['effr'].notna()]['diff'].sum()==0:
        ffr_future=np.nan
    elif totdaysinmonth==day:
        ffr_future=np.nan
    
    else:
        newdata['diff']=-newdata['diff']
        newdata['w_effr']=newdata['diff']*newdata['effr']
        
        FFF_0=data[data['date']==date]['FFF_0'].item()
        #print(FFF_0)
        
        ffr_past=newdata['w_effr'].sum(skipna=True)/newdata[newdata['effr'].notna()]['diff'].sum()
        ffr_future=totdaysinmonth/(totdaysinmonth-(day-1))*(1-FFF_0/100)-(day-1)/(totdaysinmonth-(day-1))*ffr_past/100
        
        #print(ffr_future)
    return ffr_future

def reshape_data(data):
    rates=pd.DataFrame(data['date'])
    ffrs=['FFF_0', 'FFF_1', 'FFF_2', 'FFF_3', 'FFF_4', 'FFF_5', 'FFF_6']
    for fff_price in ffrs:
        variable=fff_price+'_rate'
        rates.loc[:,variable]=100-data[fff_price]
        
    rates.loc[:,'ffr_future']=data.loc[:,'ffr_future']*100
    return rates    



def create_plot(rates,datestring):
    ### Plot the expected average federal funds rate at different horizon
    date_announcement=pd.to_datetime(datestring)
    date_pre_ann=date_announcement+pd.Timedelta('-1 days')
    date_post_ann=date_announcement+pd.Timedelta('1 days')
    #effr=data[(data['date']>="2002-11-01") & (data['date']<="2002-11-20")][['date','effr']]
    
    rates_annouc=[]
    rate_pre_annouc=[]
    rate_post_annouc=[]
    
    ffrs=['FFF_0', 'FFF_1', 'FFF_2', 'FFF_3', 'FFF_4', 'FFF_5', 'FFF_6']
    
    for fff_price in ffrs:
        rates_annouc.append(rates[rates['date']==date_announcement][fff_price+'_rate'].item())
        rate_pre_annouc.append(rates[rates['date']==date_pre_ann][fff_price+'_rate'].item())
        rate_post_annouc.append(rates[rates['date']==date_post_ann][fff_price+'_rate'].item())
    
    rates_annouc[0]=rates[rates['date']==date_announcement]['ffr_future'].item()
    rate_pre_annouc[0]=rates[rates['date']==date_pre_ann]['ffr_future'].item()
    rate_post_annouc[0]=rates[rates['date']==date_post_ann]['ffr_future'].item()
    
    plt.plot(rate_pre_annouc)
    plt.plot(rates_annouc)
    plt.plot(rate_post_annouc)
    plt.legend(['Pre Ann.','Ann. day','Post Ann.'])
    plt.ylabel('Implied federal funds rate (in %)')
    plt.xlabel('Months into future')
    plt.show()
    

