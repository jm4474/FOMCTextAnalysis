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

    pattern = "(?<!above)(?<!rise)(?<!decline)(\s\d{1,2}\s?)(to)?(\s?\-?\d?\/?\d?)(\s*per\-?cent|\%)"
    regex=re.compile(pattern,re.IGNORECASE)
    empty=""
    if regex.search(sentence):
        for match in regex.finditer(sentence):
            if len(empty)>1:
                empty=empty+" fromto "+str(match.group(1))+" "+str(match.group(3))
            else:
                empty=empty+str(match.group(1))+" "+str(match.group(3))
        entry.update({"rate_target":empty.strip()})
        entry.update({"rate_unit":match.group(2)})
        
    total_entries.append(entry)
    

output=pd.DataFrame(total_entries)

output.to_csv("../output/statements_text_extraction.csv")




def clean_fraction(frac):
    fraction=frac.split("/")
    rate=int(fraction[0].strip())/int(fraction[1].strip())
    return rate
    
def clean_policy_change(change,unit,action):
    change=change.strip()
    unit=unit.strip().replace(" ","")
    #print(unit)
    if unit=="percentage":
        changebp=int(clean_fraction(change)*100)
        print(changebp)
    if unit=="basispoints" or unit=="basispoint" or unit==None:
        changebp=int(change)
    if action=="lower" or action=="cut" or action=="decline" or action=="reduction":
        changef=-int(changebp)
        finalaction="easing"
    else:
        changef=int(changebp)
    if action=="keep" or action=="maintain" or action=="unchanged" or action=="no change" or action=="did not take action":
        finalaction="unchanged"
    if action=="raise" or action=="rise":
        finalaction="tightening"       
    return [changef,finalaction]

def clean_number(targetrange):
    targetrange=targetrange.strip()
    targetrange=targetrange.replace(" ","")
    if len(targetrange)==1:
        result=int(targetrange.strip())
    else:
        try:
            result=clean_fraction(targetrange)
        except:
            targethelp=targetrange.replace(" ","").split("-")
            if len(targethelp)==2:
                result=int(targethelp[0].strip())+clean_fraction(targethelp[1])
    return result


def clean_target(targetrange):
    targetrange=targetrange.strip()
    fromtarget=[]
    try:
        targetrange=element['rate_target'].split("fromto")
    except:
        targetrange=targetrange
    if len(targetrange)==2:
        fromtarget=clean_number(targetrange[0])
        totarget=clean_number(targetrange[1])
    else:
        fromtarget=[]
        totarget=clean_number(targetrange[0])
    return [fromtarget,totarget]   

clean_list=[]
for element in total_entries:
    #element=total_entries[12]
    print(element)
    clean_entry={"date":element['date'],"sentence":element['e_state'],'policy_change_unit':"bps"}
    try:

        if element['policy_action'] in ["keep" ,"maintain","unchanged","no change","did not take action"]:
            clean_entry.update({"policy_treatment":"unchanged","policy_change":0})
        else:
            policy=clean_policy_change(element['policy_change'],element['policy_change_unit'],element['policy_action'])
            clean_entry.update({"policy_treatment":policy[1],"policy_change":policy[0]})
    except:
        pass
    try:
        target=clean_target(element['rate_target'])
        clean_entry.update({"target_before":target[0],"target_after":target[1]})
    except:
        pass
    
    clean_list.append(clean_entry)
      

output_clean=pd.DataFrame(clean_list)

output_clean.to_csv("../output/statements_text_extraction_clean.csv")
