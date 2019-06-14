#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 14 10:00:31 2019

@author: olivergiesecke
"""

###############################################################################
### Set packages ###

import pandas as pd
import requests
from bs4 import BeautifulSoup
import datetime
import csv
from tika import parser
import re
import os

###############################################################################
### Set the working directory ###
doc_list = os.listdir("../output/Bluebook_extract")
files=[]
for doc in doc_list:
    try:
        print("Work on the following file",doc)
    
        #doc='2008-01-29.txt'
            
        data={"meeting":doc}
        
        def unique1(list1): 
            # intilize a null list 
            unique_list = [] 
            # traverse for all elements 
            for x in list1: 
                # check if exists in unique_list or not 
                if x not in unique_list: 
                    unique_list.append(x) 
            return unique_list
        
        f = open('../output/Bluebook_extract/'+doc,"r") 
        phrases=[]
        alt_list=[]
        for line in f:
            if not re.match("\n",line) :
                line_clean=line.replace("\n",'')
                phrases.append(line_clean)
                if re.search("[Aa]lternatives?\s*[ABCDEabcde][^a-zA-Z]",line_clean):
                    help_list=re.findall("[Aa]lternatives?\s*[ABCDEabcde][^a-zA-Z]",line_clean)
                    for ele in help_list:
                        alt_list.append(ele[:-1])
                
        u_alt_list=unique1(alt_list)
        
        # Eliminate the plural
        lhelp=[]
        for element in u_alt_list:
            if re.search("[Aa]lternatives\s*[ABCDEabcde]",element):
        
                selement=element.replace("Alternatives","Alternative")
        
            else:
                selement=element
            lhelp.append(selement)        
        su_alt_list=unique1(lhelp)
        
        # Try to understand the number of sentences
        sentences=[]
        for phrase in phrases:
            sentence_list=re.split("\.\s*",phrase) # Remove empty entries
            sentence_list = list(filter(None, sentence_list))
            for sentence in sentence_list:
                sentences.append(sentence)
        n_sent=len(sentences)
        data.update({"number of sentences":n_sent})
        
        # For each available alternative find the relevant sentences
        
        for policy_option in su_alt_list:
            count=0
            option_sent=[]
            # Adjust the name for whitespaces
            policy_option_name="Alternative "+policy_option[-1].upper()
            for sentence in sentences:
                if re.search(policy_option,sentence):
                    count+=1
                    option_sent.append(sentence)
            data.update({policy_option_name+"_count":count})
            data.update({policy_option_name+"_sentences":option_sent})
        files.append(data)            
    except:
        print("file error")
        
# Collect output in dataframe
df_output=pd.DataFrame(files)
alt_columns=[]
for column in list(df_output.columns):
    if not column in ['meeting','number of sentences']:
        alt_columns.append(column)

ini_list=['meeting','number of sentences']
for element in sorted(alt_columns):
    ini_list.append(element)
df_output.sort_values('meeting', inplace=True)
df_output['year']=pd.to_numeric(df_output['meeting'].str[:4])


###  Do some summary statistics
# Total number of meetings
print("# total bluebooks",len(df_output))
# Meetings with phrases that contain alternatives
print("# meeting with sentences:",len(df_output[df_output['number of sentences']>0]))
# Number of meetings with alternative A
print("# meeting alternative A:",len(df_output[df_output['Alternative A_count']>0]))
# Number of meetings with alternative B
print("# meeting alternative B:",len(df_output[df_output['Alternative B_count']>0]))
# Number of meetings with alternative C
print("# meeting alternative C:",len(df_output[df_output['Alternative C_count']>0]))
# Number of meetings with alternative D
print("# meeting alternative D:",len(df_output[df_output['Alternative D_count']>0]))
# Number of meetings with alternative E
try:
    print("# meeting alternative E:",len(df_output[df_output['Alternative E_count']>0]))
except:
    print("No alternative E")
# Give missing meeting dates per year after 1968
i=1968
while i<2011:
    df_year=df_output[df_output['year']==i]
    i+=1
    print(i, "year: # meeting without sentences:",len(df_year[df_year['number of sentences']==0]))

      
# Write data frame to csv
df_output.to_csv("../output/bluebook_alternatives_og.csv")
