#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 17 14:47:03 2019

@author: olivergiesecke
"""
import pandas as pd
import re
import os


### Open the csv

data=pd.read_csv("../../Matlab/Output/Statements/Statements_text.csv")

total_entries=[]
for index, row in data.iterrows():
    
    statement=row['statements']
    statement=statement.replace("\n"," ")
    
    entry={"date":row['start_date']}
    entry.update({"e_state":statement})
    
    sentence=""
    pattern = "([^\.]*)(federal\sfunds)(\.|[^\.]*\.)"    
    if re.search(pattern,statement,re.IGNORECASE):
        sentence=re.search(pattern,statement,re.IGNORECASE).group()
    else:
        sentence=""

    pattern = "(\d\/\d|\d{1,2}|)(\s*basis\s*points?|\s*percentage)"
    if re.search(pattern,sentence,re.IGNORECASE):
        entry.update({"policy_change":str(re.search(pattern,sentence,re.IGNORECASE).group(1))})
        entry.update({"policy_change_unit":re.search(pattern,sentence,re.IGNORECASE).group(2)})

    pattern = "(rise|lower|cut|decline|reduction|keep|maintain|unchanged|no/s*change|raise)"
    if re.search(pattern,sentence,re.IGNORECASE):
        entry.update({"policy_action":re.search(pattern,sentence,re.IGNORECASE).group()})

    pattern = "(?<!above)(\s\d{1,2}\s?)(to)?(\s?\-?\d?\/?\d?)(\s*per\-?cent|\%)"
    regex=re.compile(pattern,re.IGNORECASE)
    empty=""
    if regex.search(sentence):
        for match in regex.finditer(sentence):
            if len(empty)>1:
                empty=empty+" to "+str(match.group(1))+" "+str(match.group(3))
            else:
                empty=str(match.group(1))+" "+str(match.group(3))
        entry.update({"rate_target":empty.strip()})
        entry.update({"rate_unit":match.group(2)})
        
    total_entries.append(entry)
    

output=pd.DataFrame(total_entries)

output.to_csv("../output/Statements_text_extraction.csv")

        
# =============================================================================
#         
#     entry={"date":row['start_date']}
#     entry.update({"e_state":statement})
#     regex = re.compile(pattern, re.IGNORECASE)
#     for match in regex.finditer(statement):
#         entry.update({"sentence":match.group()})
#         entry.update({"policy_change":match.group(4)})
#         entry.update({"policy_change_unit":match.group(5)})
#         
#         
#     
#     pattern = "([^\.]+)(federal\sfunds)([^\.0-9]*)(\d\/\d|\d{1,2}|)(\s*basis\s*points?|\s*percentage)(\.|[^\.]*\.)"
#     entry={"date":row['start_date']}
#     entry.update({"e_state":statement})
#     regex = re.compile(pattern, re.IGNORECASE)
#     for match in regex.finditer(statement):
#         entry.update({"sentence":match.group()})
#         entry.update({"policy_change":match.group(4)})
#         entry.update({"policy_change_unit":match.group(5)})
#         
#     pattern = "([^\.]+)(federal\sfunds)([^\.]*)(\d{1,2}\-?\d?\/?\d?)(\s*per\-?cent|\%)(\.|[^\.]*\.)"
#     regex = re.compile(pattern, re.IGNORECASE)
#     for match in regex.finditer(statement):
#         entry.update({"target":match.group(4)})    
#         entry.update({"target_unit":match.group(5)})    
#     
# =============================================================================
