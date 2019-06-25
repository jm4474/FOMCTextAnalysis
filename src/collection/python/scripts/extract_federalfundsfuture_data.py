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


### Open the csv

data=pd.read_excel("../data/FFF_1m3m_extract.xlsx")

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





