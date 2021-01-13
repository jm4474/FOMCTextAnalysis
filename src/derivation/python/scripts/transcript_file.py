#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 11 13:49:50 2021

@author: olivergiesecke
"""

import os, shutil
import re
import timeit
import pandas as pd
import numpy as np
import pickle
import string

TRANSCRIPT_PATH = os.path.expanduser("~/Dropbox/MPCounterfactual/src/collection/python/output/transcript_raw_text")

MONTHS = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"]
month_string = r"((\b"+r"\b)?(\b".join(MONTHS)+r"\b)?)"
datestring = re.compile(month_string+r"\s+\d+\–?\-?(\d?\d?)\,\s+\d\d\d\d",re.IGNORECASE)

def generate_rawtranscripts():
    raw_doc = os.listdir(TRANSCRIPT_PATH)  # as above
    filelist = [f for f in sorted(raw_doc) if f!=".DS_Store"] # sort the pdfs in order

    newfiles = [f for f in filelist if np.datetime64(f[:10] , format="%y-%m-%d")>= np.datetime64("2006-02-01", format="%y-%m-%d")]


    raw_text = pd.DataFrame([])  # empty dataframe

    start = timeit.default_timer()
    for i, file in enumerate(newfiles):
        print("\n"+"*" * 80)
        print(f"Date and file {file}")
        print("*" * 80)
        #print('Document {} of {}: {}'.format(i, len(filelist), file))
        with open(os.path.join(TRANSCRIPT_PATH, file), 'r') as inf:
            parsed = inf.read()
        
        temp_df = pd.DataFrame(columns=['Date',"Daterregex", 'Speaker', 'content'])  # create a temporary dataframe
        date = ""
        
        try:
            pre  = re.compile("Transcript\s?of\s?(?:the:?)?\s?Federal\s?Open\s?Market\s?Committee",re.IGNORECASE)
            m = re.search(pre,parsed)
            print(parsed[m.start():m.start()+90])
        
            date = re.search(datestring,parsed[m.start():m.start()+90])[0]
            #month = re.search(month_string,date,re.IGNORECASE)[0]
            print(date)
            
            parsed = re.split(pre,parsed)[1]    
        except:  
            try:
                pre  = re.compile("Transcript\s?of\s?(?:Telephone:?)?\s?Conference\s?Call",re.IGNORECASE)
                m = re.search(pre,parsed)
                print(parsed[m.start():m.start()+100])
                date = re.search(datestring,parsed[m.start():m.start()+90])[0]
                #month = re.search(month_string,date,re.IGNORECASE)[0]
                print(date)
                parsed = re.split(pre,parsed)[1] 
            except:  
                print("No split")
                parsed = parsed  
                
        interjections = re.split('\\n\s*MR. |\\n\s*MS\. |\\n\s*CHAIRMAN |\\n\s*VICE\s+CHAIRMAN |\\n\s*CHAIR\s+', parsed)  # split the entire string by the names (looking for MR, MS, Chairman or Vice Chairman)
        
        interjections = [interjection.replace('\n', ' ') for interjection in
                         interjections]  # replace \n linebreaks with spaces
        
        temp = [re.split('(^\S*)', interjection.lstrip()) for interjection in
                interjections]  # changed to this split because sometimes (rarely) there was not a period, either other punctuation or whitespace
        speaker = []
        content = []
        for interjection in temp:
            speaker.append(interjection[1].strip(string.punctuation))
            content.append(interjection[2])
        print(type(date))   
        
        temp_df['Speaker'] = speaker
        temp_df['content'] = content  # save interjections
        temp_df['Date'] = file[:10]
        temp_df["Daterregex"] = date
        raw_text = pd.concat([raw_text, temp_df], axis=0)
        
    end = timeit.default_timer()   
    #raw_text.to_excel(os.path.join(CACHE_PATH,'raw_text.xlsx'))  # save as raw_text.xlsx
    print("Transcripts processed. Time: {}".format(end - start))    
    docs = raw_text.groupby('Date')['content'].sum().to_list()
    return docs,raw_text


# =============================================================================

def clean(row):
    datestring = row["Daterregex"].lower()
    new =  row["content"].lower().replace(datestring,"")
    return re.sub("\d+\sof\s\d+","",new)
    
# Data Import
docs,raw_text = generate_rawtranscripts()

# Data Cleaning
raw_text["content"] = raw_text.apply(clean,axis=1)

# Do Separation
sep_rules = pd.read_excel("../data/separation_part2.xlsx", dtype={"date": str},encoding='utf-8-sig')
sep_rules.loc[sep_rules["index"]=="None","index"] = np.nan

sep_rules["index"] = pd.to_numeric(sep_rules["index"])
rules = dict(zip([dat.replace("\ufeff","") for dat in sep_rules["date"].to_list()],sep_rules["index"].to_list()))

dates = list(raw_text['Date'].unique())
newdata = pd.DataFrame([])
for date in dates:
    data = raw_text[raw_text['Date']==date ].copy()
    print(f"\n\n************************{date}*****************************")
    
    # Lookup
    try:
        itr = rules[date]
        if str(itr) == "nan":
            print("Not Available")
        else:
            itr= int(itr)
                    
            temp1 = data.iloc[:itr-1].copy()
            temp1.loc[:,"Section"] = 1
    
            temp2 = data.iloc[itr:].copy()
            temp2.loc[:,"Section"] = 2
            
            newdata = pd.concat([newdata, temp1 , temp2],axis=0)
            
    except:
        print("Key is not available")

# Clean Speaer
newdata = newdata[(newdata['Speaker']!="Conf") & (newdata['Speaker']!="E") & 
                  (newdata['Speaker']!="FOMC") & (newdata['Speaker']!="Meeting") & (newdata['Speaker']!='Conference')].copy()
speakers = [sp for sp in sorted(list(newdata['Speaker'].unique()))]

newdict = {}
for sp in speakers:
    new = re.sub("\.\d","",sp)
    new = re.sub("\d","",new)
    newdict.update({sp:new})    

newdict.update({'KOCHERLOKTA':'KOCHERLAKOTA', 'KOCOHERLAKOTA':'KOCHERLAKOTA'})
newdata = newdata.replace({"Speaker":newdict})

newdata.to_excel("../output/raw_text_part2.xlsx")
newdata.to_pickle("../output/raw_text_part2.pkl")





