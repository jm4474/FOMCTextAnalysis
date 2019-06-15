#!/usr/bin/env python3

# -*- coding: utf-8 -*-
"""
Created on Fri Jun 14 10:00:31 2019

@author: olivergiesecke
"""

###############################################################################
### Set packages ###

import pandas as pd
import csv
from tika import parser
import re
import os

###############################################################################
# Open points:
# 1) Handling of footnotes. Right now, they are mixed into sentence at the end 
# of the page.



###############################################################################

# Get all files except the hidden
doc_list=[]
for item in os.listdir("../output/raw_bluebook/"):
    if not item.startswith('.'):
        doc_list.append(item)

files=[]
for doc in doc_list:
    # Do for specific document
    doc=doc_list[20]
    
    # Open the file
    with open("../output/raw_bluebook/"+doc,'r') as f:
        # Read document line by line
        lines=f.readlines()
    
        cleaned_lines=[]
        for line in lines:
            # Replace linebreaks with space
            line=line.replace("\n"," ")
            # Remove empty lines 
            if not re.match(r'^\s*$', line):
                #Remove four character lines that do not end with period
                #regex = r".{1,4}(?<!\.)$"
                #if not re.match(regex, line):
                cleaned_lines.append(line)
        # Make a single element from list.
        text="".join(cleaned_lines)            
    
    # Search for alternative(s) and keep the sentence
    all_sentences=[]
    pattern = "([^.]*)(alternatives?\s+[a-e])(\.|[^a-z]\.|[^a-z][^\.]+\.)"
    regex = re.compile(pattern, re.IGNORECASE)
    for match in regex.finditer(text):
        all_sentences.append(match.group())
        
    data={"meeting_date":doc[:-4],"n_sentences":len(all_sentences),"sentences":all_sentences}
    
    # Search for alternative {a,b,c,d,e} and keep the sentence
    for alt in ["a","b","c","d","e"]:
        alt_sentences=[]
        pattern = "([^.]*)(alternative\s+"+alt+")(\.|[^a-z]\.|[^a-z][^\.]+\.)"
        regex = re.compile(pattern, re.IGNORECASE)
        for match in regex.finditer(text):
            alt_sentences.append(match.group())
        alt_sent="alt_"+alt+"_sentences"
        alt_count="alternative_"+alt+"_count"
        data.update({alt_sent:alt_sentences,alt_count:len(alt_sentences)})

    # Collect all files in the data file
    files.append(data)            
        

# Collect output in dataframe
df_output=pd.DataFrame(files)

df_output['year']=pd.to_numeric(df_output['meeting_date'].str[:4])
df_output['date']=pd.to_datetime(df_output['meeting_date'])

df_result=df_output[(df_output['date']<="2009-04-17") & (df_output['date']>="1968-07-17")]

###  Do some summary statistics 
# Total number of meetings between 19680813-20090317
print("# total bluebooks",len(df_result))
# Meetings with phrases that contain alternatives
print("# meeting with sentences:",len(df_output[df_result['n_sentences']>0]))

      
print("# meeting alternative a:",len(df_output[df_output['alternative_a_count']==0]))
print("# meeting alternative a:",len(df_output[df_output['alternative_a_count']<4]))

print("# meeting alternative b:",len(df_output[df_output['alternative_b_count']==1]))
print("# meeting alternative b:",len(df_output[df_output['alternative_b_count']>1]))
            
       
i=1968
while i<2011:
    df_year=df_output[df_output['year']==i]
    i+=1
    print(i, "year: # meeting without sentences:",len(df_year[df_year['number of sentences']==0]))

      
# Write data frame to csv
df_output.to_csv("../output/bluebook_alternatives_og.csv")

# CHECK: 2000-12-19.txt
