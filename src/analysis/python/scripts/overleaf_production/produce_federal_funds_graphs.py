
"""
Purpose: Plots the federal funds future curves for three consecutive days
Status: Final - 06/26/2019
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

def main(datestring):
    rates=pd.read_csv("../../../../derivation/python/output/federal_funds_futures.csv")
    rates['date']=pd.to_datetime(rates['date'])
    create_plot(rates,datestring)

def create_plot(rates,datestring):
    ### Plot the expected average federal funds rate at different horizon
    date_announcement=pd.to_datetime(datestring)
    date_pre_ann=date_announcement+pd.Timedelta('-1 days')
    date_post_ann=date_announcement+pd.Timedelta('1 days')
    #effr=data[(data['date']>="2002-11-01") & (data['date']<="2002-11-20")][['date','effr']]
    print(date_announcement)
    rates_annouc=[]
    rate_pre_annouc=[]
    rate_post_annouc=[]
    
    ffrs=['FFF_0', 'FFF_1', 'FFF_2', 'FFF_3', 'FFF_4', 'FFF_5', 'FFF_6']
    
    for fff_price in ffrs:
        rates_annouc.append(rates[rates['date']==date_announcement][fff_price+'_rate'].item())
        rate_pre_annouc.append(rates[rates['date']==date_pre_ann][fff_price+'_rate'].item())
        #rate_post_annouc.append(rates[rates['date']==date_post_ann][fff_price+'_rate'].item())
    
    rates_annouc[0]=rates[rates['date']==date_announcement]['ffr_future'].item()
    rate_pre_annouc[0]=rates[rates['date']==date_pre_ann]['ffr_future'].item()
    #rate_post_annouc[0]=rates[rates['date']==date_post_ann]['ffr_future'].item()
    
    
    plt.rc('text', usetex=True)

    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(1, 1, 1)

    ax.plot(rate_pre_annouc, color='red', ls='solid',marker='o')
    ax.plot(rates_annouc, color='blue', ls='solid',marker='o')
    #ax.plot(rate_post_annouc, color='k', ls='dashed',marker='o')
    
  
    ax.set_xlabel('Months into future')
    ax.set_ylabel('Implied federal funds rate (in \%)')


    plt.legend(['Pre announcement','Post announcement'],frameon=False)
    plt.savefig('../../output/overleaf_files/fed_future_'+datestring+'.png', dpi=300)

if __name__ == "__main__":
    datestring="2002-11-06"
    main(datestring)