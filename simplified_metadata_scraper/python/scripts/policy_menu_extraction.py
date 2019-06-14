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
    print("Work on the following file",doc)

    #doc='2008-01-29.txt'
        
    data={"meeting":doc}
    
    def unique(list1):
        unique_list=[]
        for ele in alt_list:
            if isinstance(ele, list):
                for ele1 in ele:
                    if not ele1 in unique_list:
                        unique_list.append(ele1)
            else:
                if not ele in unique_list:
                    unique_list.append(ele)
        return unique_list
                    
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
df_output=df_output[ini_list]

# Write data frame to csv
df_output.to_csv("../output/bluebook_alternatives_og.csv")
