#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  4 09:24:35 2019

@author: olivergiesecke
"""

###############################################################################
### Import Python packages ###
import os  
import subprocess
import logging
import pandas as pd
import numpy as np

###############################################################################

# Set the working directory 
directory='/Users/olivergiesecke/Dropbox/MPCounterfactual/simplified_metadata_scraper/'
os.chdir(directory)

# Import the raw csv file
rawcsv=pd.read_csv('test_metadata.csv', header='infer')

# Get total number of observations
total_nobs=len(rawcsv.index)
print(total_nobs)

# Get the meetings in a year
search_year=2013
rawcsv['meeting_info'][rawcsv['year']==search_year].unique().tolist()

# Get the documents for a specific meeting
search_meeting='October 16 (unscheduled) - 2013'
documents=rawcsv['document_name'][rawcsv['meeting_info']==search_meeting].unique().tolist()
print( documents)

rawcsv.groupby('year')




