#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author Anand Chitale
Produces a final derived file containing all information required for data preperation
"""

import pandas as pd
import numpy as np
import math
import sys

# Monthly data
data_df=pd.read_csv('../../../collection/python/output/string_theory_indicators_monthly.csv')
data_df.rename(columns={'month':'date'},inplace=True)
data_df['date']=pd.to_datetime(data_df['DATE'])
data_df['month'] = data_df['date'].apply(lambda x: x.month)
data_df['year'] = data_df['date'].apply(lambda x: x.year)

# Daily data
data_daily=pd.read_csv('../output/daily_policy_data.csv')
data_daily['date']=pd.to_datetime(data_daily["DATE"])
data_daily['year']=data_daily["date"].apply(lambda x:x.year)
data_daily['month']=data_daily["date"].apply(lambda x:x.month)

data_daily=data_daily[(data_daily['year']>=1987) & (data_daily['year']<2009)]
data_rates=data_daily[['TRY_3M', 'TRY-2Y', 'TRY-10Y','DFEDTAR','year', 'month']]
for var in ['TRY_3M', 'TRY-2Y', 'TRY-10Y']:
    data_rates.loc[data_rates[var]=="ND",var]=np.nan

data_rates[['TRY_3M', 'TRY-2Y', 'TRY-10Y']]=data_rates[['TRY_3M', 'TRY-2Y', 'TRY-10Y']].astype(float)
data_rates=data_rates.groupby(['year', 'month']).mean()
data_rates=data_rates.rename(columns={"TRY-2Y":"TRY_2Y","TRY-10Y":"TRY_10Y","DFEDTAR":"FF_TAR"})

data_daily=data_daily[['DFEDTAR', 'end_date', 'event_type', 'date', 'year', 'month']]

# Make pre 1994 adjustment
data_daily.loc[data_daily['year']<1994,'event_type']=data_daily[data_daily['year']<1994]['event_type'].shift(periods=1)
data_daily=data_daily[data_daily['date'].notna()]
data_daily['d_meeting']=data_daily["event_type"]=="Meeting"

from calendar import monthrange
data_daily['days_month']=data_daily["date"].apply(lambda x:monthrange(x.year, x.month)[1])
data_daily['day']=data_daily['date'].apply(lambda x:x.day)

# Scale variable 
data_daily['scale']=data_daily[data_daily["event_type"]=="Meeting"]['days_month'] / ( data_daily[data_daily["event_type"]=="Meeting"]['days_month'] -  data_daily[data_daily["event_type"]=="Meeting"]['day'] + 1 )
data_scale=data_daily[['scale', 'year', 'month']].groupby(['year', 'month']).mean()

# Crisis dummy
data_daily['d_crisis']=data_daily["date"]>"2006-08-01"
data_crisis=data_daily[['d_crisis', 'year', 'month']].groupby(['year', 'month']).mean()

# Monthly target changes
data_meeting=data_daily[['d_meeting', 'year', 'month']].groupby(['year', 'month']).sum()
data_daily=data_daily[data_daily['day']==data_daily['days_month']]

data_daily.loc[:,'lag_DFEDTAR'] = data_daily['DFEDTAR'].shift(periods=1)
data_daily['ch_DFEDTAR']=data_daily['DFEDTAR']-data_daily['lag_DFEDTAR'] 

data_pchanges = data_daily[[ 'year', 'month','ch_DFEDTAR','lag_DFEDTAR','DFEDTAR']]
data_pchanges = data_pchanges.dropna()

# Define meeting / non-meeting months
clean_data=data_df[['date','month','year','INDPRO','PCEPI','PCEPI_PCA']]
clean_data=clean_data.sort_values(by=['year', 'month'])
clean_data.loc[:,'inflation']=data_df['PCEPI_PCH']
#clean_data.loc[:,'l1_inflation']=data_df['PCEPI_PCH'].shift(periods=1)
#clean_data.loc[:,'l2m_prices']=data_df['PCEPI'].shift(periods=2)
#clean_data['lagged_infl']=(np.log(clean_data['lagged_prices'])-np.log(clean_data['l2m_prices']))*100
clean_data.loc[:,'unemp']=data_df['UNRATE']
clean_data.loc[:,'lagged_unemp']=data_df['UNRATE'].shift(periods=1)
#clean_data.drop(columns=['lagged_prices', 'l2m_prices'],inplace=True)
#
market_df=pd.read_csv('../output/derived_monthly_market_exp.csv')

clean_data=clean_data.merge(market_df[['year','month','market_exp']],how='outer',on=['year','month'])
clean_data=clean_data.merge(data_pchanges,how='outer',on=['year','month'])
clean_data=clean_data.merge(data_meeting,how='outer',on=['year','month'])   
clean_data=clean_data.merge(data_scale,how='outer',on=['year','month'])
clean_data=clean_data.merge(data_crisis,how='outer',on=['year','month'])
clean_data=clean_data.merge(data_rates,how='outer',on=['year','month'])
# Merge the policy menu
menu_df = pd.read_csv('../../../analysis/python/output/monthly_treatment_counts.csv')
menu_df.drop(columns=['Unnamed: 0'],inplace=True)
clean_data = clean_data.merge(menu_df,how='outer',on=['year','month'])
print(clean_data[clean_data['d_m050'].notna()][['month','year','d_m050']])
clean_data['d_crisis']=clean_data['d_crisis']>0
clean_data['d_meeting']=clean_data['d_meeting']>0
clean_data=clean_data[(clean_data['year']>1987) & (clean_data['year']<=2008)]
clean_data=clean_data.sort_values(by=['year', 'month'])
clean_data.rename(columns={'ch_DFEDTAR':'target_change'},inplace=True)
clean_data.loc[clean_data['scale'].isna(),'scale']=0

# Encode changes into a ordinal variable
outcomes=sorted(list(set(list(clean_data['target_change']))))

i=1
out_dict={}
for outcome in outcomes:
    out_dict.update({outcome:i})
    i+=1
    
clean_data['ord_policy']=clean_data['target_change'].map(out_dict)
clean_data['d_nineeleven']=(clean_data['month']==9) & (clean_data['year']==2001)


# Create the month dummies
clean_data['date']=clean_data['date_x'].apply(lambda x:x.strftime("%m/%d/%Y"))
clean_data=pd.get_dummies(clean_data,columns=['month'],prefix='d_month')

for month in range(1,13):
    clean_data['d_month_'+str(month)+'_fomc']=clean_data['d_month_'+str(month)]*clean_data['d_meeting']

clean_data['target_change_last']=clean_data['target_change'].shift(periods=1)
clean_data['target_change_last_fomc']=clean_data['target_change_last']*clean_data['d_meeting']

clean_data[['d_meeting',  'd_crisis', 'd_nineeleven']]=clean_data[['d_meeting',  'd_crisis', 'd_nineeleven']].astype('int32')

clean_data.to_csv("../output/matlab_file.csv",index=False)

#AC: FURTHER DUMMIES
print("reached Anand's section")

change_dummies = ['d_m075','d_m050','d_m025','d_0',
	'd_025','d_050','d_075','d_dec','d_inc','d_unc']

menu_dummies = [d.replace("_","_menu_") for d in change_dummies]

rename_dict = dict(zip(change_dummies,menu_dummies))
clean_data.rename(columns=rename_dict,inplace=True)

menu_adjusted_dummies = [d.replace("_","_menu_adj_") for d in change_dummies]
for menu in menu_adjusted_dummies:
    clean_data[menu] = clean_data[menu.replace("menu_adj_","menu_")]
clean_data['d_menu_adj_m050'] = ((clean_data['d_menu_m050']+clean_data['d_menu_m075'])>0).astype(int)
clean_data['d_menu_adj_050'] = ((clean_data['d_menu_050']+clean_data['d_menu_075'])>0).astype(int)

clean_data.drop(columns=['d_menu_adj_075','d_menu_adj_m075'],inplace=True)

clean_data['d_sample1'] = (clean_data['date_x']>=pd.to_datetime('07-1989'))&\
	(clean_data['date_x']<pd.to_datetime('07-2005'))

clean_data['d_sample2'] = (clean_data['date_x']<=pd.to_datetime('07-1989'))&\
	(clean_data['date_x']>pd.to_datetime('12-2008'))

clean_data['target_change_adj'] = clean_data['target_change']


clean_data.loc[clean_data.target_change>0.5,'target_change_adj'] = 0.5
clean_data.loc[clean_data.target_change<-0.5,'target_change_adj'] = -0.5
clean_data.loc[clean_data.target_change==-0.3125,'target_change_adj'] = -0.25
clean_data.loc[clean_data.date_x == pd.to_datetime('01-2000'),'d_y2k'] = 1

clean_data["l1_inflation"] = clean_data["inflation"].shift(1)
clean_data['l2_inflation'] = clean_data["inflation"].shift(2)


#clean_data['l1_diff_unemp'] = clean_data['lagged_unemp'] - clean_data['lagged_unemp'].shift(3)
#clean_data['l2_diff_unemp'] = clean_data['l1_diff_unemp'].shift(3) - clean_data['l1_diff_unemp'].shift(6)
clean_data['diff_unemp'] = clean_data['unemp'] - clean_data['unemp'].shift(1)
clean_data['l1_diff_unemp'] = clean_data['diff_unemp'].shift(1)
clean_data['l2_diff_unemp'] = clean_data['diff_unemp'].shift(2)


#clean_data['l1_inf'] = (np.log(clean_data['PCEPI'].shift(1))
	#-np.log(clean_data.PCEPI.shift(4)))*100
#clean_data['l2_inf'] = (np.log(clean_data['PCEPI'].shift(4))\
	#-np.log(clean_data.PCEPI.shift(7)))*100
clean_data['ld_inflation'] = (np.log(clean_data['PCEPI'])\
	-np.log(clean_data['PCEPI'].shift(1)))*100
clean_data['l1_ld_inflation'] = clean_data['ld_inflation'].shift(1)
clean_data['l2_ld_inflation'] = clean_data['ld_inflation'].shift(2)

clean_data['l1_target_change'] = clean_data.target_change.shift(1)
clean_data['l2_target_change'] = clean_data.target_change.shift(2)
clean_data['l3_target_change'] = clean_data.target_change.shift(3)
clean_data['l4_target_change'] = clean_data.target_change.shift(4)
clean_data['l5_target_change'] = clean_data.target_change.shift(5)

clean_data["Fl1_target_change"] = clean_data.l1_target_change*clean_data.d_meeting


clean_data['d_policy_m050'] = clean_data.target_change_adj==-.5
clean_data['d_policy_m025'] = clean_data.target_change_adj==-.25
clean_data['d_policy_0'] = clean_data.target_change_adj==0
clean_data['d_policy_025'] = clean_data.target_change_adj== .25
clean_data['d_policy_050'] = clean_data.target_change_adj==.5

clean_data['d_policy_inc'] = ( (clean_data.d_policy_025 == 1) |  (clean_data.d_policy_050==1))
clean_data['d_policy_unc'] = (clean_data.d_policy_0 == 1 )
clean_data['d_policy_dec'] = ( (clean_data.d_policy_m025 == 1) | (clean_data.d_policy_m050==1))

for indic in ['INDPRO','PCEPI']:
	for time_shift in range(-1,-25,-1):
		horizon = abs(time_shift)
		clean_data[indic+"_g_"+str(horizon)] = (np.log(clean_data[indic].shift(time_shift)
			)-np.log(clean_data[indic]))*100
for indic in ['unemp','TRY_3M','TRY_2Y','TRY_10Y','FF_TAR']:
	for time_shift in range(-1,-25,-1):
		horizon = abs(time_shift)
		clean_data[indic+"_g_"+str(horizon)] = clean_data[indic].shift(time_shift)\
			-clean_data[indic]


#clean_data.to_csv('../output/final_data_file.csv',index=False)

clean_data['d_sub_1'] = ((clean_data['d_menu_inc'] == 1)& 
	(clean_data['d_menu_unc'] == 1) &
	(clean_data['d_menu_dec'] == 0)& 
	(clean_data['d_sample1'] == 1))

clean_data['d_sub_2'] = ((clean_data['d_menu_inc'] == 1) & 
	(clean_data['d_menu_unc'] == 1) &
	(clean_data['d_menu_dec'] == 1) & 
	(clean_data['d_sample1'] == 1))

clean_data['d_sub_3'] = ((clean_data['d_menu_inc'] == 1) & 
	(clean_data['d_menu_unc'] == 0) &
	(clean_data['d_menu_dec'] == 1) & 
	(clean_data['d_sample1'] == 1))
clean_data['d_sub_4'] = ((clean_data['d_menu_inc'] == 0) & 
	(clean_data['d_menu_unc'] == 1) &
	(clean_data['d_menu_dec'] == 1) & 
	(clean_data['d_sample1'] == 1))

clean_data['d_sub_01'] = ((clean_data['d_sub_1'] == 1)
	| (clean_data['d_sub_2'] == 1) 
	| (clean_data['d_sub_3'] == 1))
clean_data['d_sub_00'] = ((clean_data['d_sub_1'] == 1) 
	| (clean_data['d_sub_4'] == 1) 
	| (clean_data['d_sub_2'] == 1))
clean_data['d_sub_m1'] = ((clean_data['d_sub_4'] == 1) 
	| (clean_data['d_sub_2'] == 1) 
	| (clean_data['d_sub_3'] == 1))
clean_data['yearly_inflation_change'] = \
	(clean_data['PCEPI']-(clean_data['PCEPI'].shift(12)))/(clean_data['PCEPI'].shift(12))*100
#print(clean_data[['date','diff_unemp','l1_diff_unemp','l2_diff_unemp',\
#	'ld_inflation','l1_ld_inflation','l2_ld_inflation']])

clean_data['l1_diff_unemp_yearly'] = (clean_data['unemp']-clean_data['unemp'].shift(12)).shift(1)
clean_data['l1_diff_unemp_quarterly'] = (clean_data['unemp']-clean_data['unemp'].shift(3)).shift(1)

clean_data['ld_inflation_yearly'] = (np.log(clean_data['PCEPI'])\
	-np.log(clean_data['PCEPI'].shift(12)))*100
clean_data['ld_inflation_quarterly'] = (np.log(clean_data['PCEPI'])\
	-np.log(clean_data['PCEPI'].shift(3)))*100

clean_data['l1_ld_inflation_yearly'] = clean_data['ld_inflation_yearly'].shift(1)
clean_data['l1_ld_inflation_quarterly'] = clean_data['ld_inflation_quarterly'].shift(1)

clean_data['etu_outcome'] = np.sign(clean_data['target_change_adj'])

clean_data.rename(columns={"date_x":"date_m"},inplace=True)
clean_data.drop(columns=["date_y"])
clean_data.to_csv("../../../analysis/matlab/data/final_data_file.csv",index=False)