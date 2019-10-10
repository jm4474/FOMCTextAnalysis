
"""
Purpose: Clean the raw statements and bring output into consistent format
Status: Final -- 06/25/2019
@author: olivergiesecke
"""
###############################################################################
### Import packages

import pandas as pd
import re
import numpy as np
###############################################################################


def main():
    data=pd.read_csv("../../../collection/python/output/statement_data.csv")
    final=do_cleaning(data)    
    final.to_csv("../output/statements_text_extraction.csv",index=False)


def do_cleaning(data):
    data.sort_values("end_date",inplace=True)
    
    total_entries=[]
    for index, row in data.iterrows():
        
        statement=row['file_text']
        statement=statement.replace("\n"," ")
        
        entry={"meeting_end_date":row['end_date']}
        entry.update({"release_date":row['release_date']})
        entry.update({"statement":statement})
        
        sentence=""
        pattern = "([^\.]*)(federal\sfunds)(\.|[^\.]*\.)"    
        if re.search(pattern,statement,re.IGNORECASE):
            sentence=re.search(pattern,statement,re.IGNORECASE).group()
        else:
            sentence=""
    
        pattern = "(\d\/\d|\d{1,2}|)(\s*basis\s*points?|\s*percentage)"
        if re.search(pattern,sentence,re.IGNORECASE):
            entry.update({"policy_change_crude":str(re.search(pattern,sentence,re.IGNORECASE).group(1))})
            entry.update({"policy_change_unit_crude":re.search(pattern,sentence,re.IGNORECASE).group(2)})
    
        pattern = "(fall|raise|rise|lower|cut|decline|reduction|keep|maintain|unchanged|no/s*change)"
        if re.search(pattern,sentence,re.IGNORECASE):
            entry.update({"policy_action_crude":re.search(pattern,sentence,re.IGNORECASE).group()})
    
        pattern = "(?<!above)(?<!rise)(?<!decline)(?<!Committee's)(?<!Committee’s)(\s\d{1,2}\s?)(to)?(\s?\-?\d?\/?\d?)(\s*per\-?cent|\%)"
        regex=re.compile(pattern,re.IGNORECASE)
        if regex.search(sentence):
            target=[]
            for match in regex.finditer(sentence):
                string=str(match.group(1))+str(match.group(3))
                target.append(string.strip())    
             
            pre_target,post_target=clean_target(target)
    
            entry.update({"rate_target":target})
            entry.update({"pre_target":pre_target})
            entry.update({"post_target":post_target})
        
        total_entries.append(entry)
    
    output=pd.DataFrame(total_entries)
    
    output.loc[:,"policy_change"]=np.nan
    output.loc[:,"policy_action"]=np.nan
    
    for i in range(len(output.rate_target)):
        changef, finalaction=clean_policy_change(output.policy_change_crude.loc[i],output.policy_change_unit_crude.loc[i],output.policy_action_crude.loc[i])    
     
        output["policy_change"].loc[i]=changef
        output["policy_action"].loc[i]=finalaction
        
    
    final=output[['meeting_end_date','release_date','pre_target','post_target','policy_change','policy_action','statement']]
    return final


def clean_fraction(frac):
    if re.search("/",frac):
        fraction=frac.split("/")
        rate=int(fraction[0].strip())/int(fraction[1].strip())
    elif frac=="":
        rate=0
    else:
       #print(frac)
        rate=int(frac)
        
    return rate

def clean_number(targetrange):
    #print(targetrange)
    if re.search("\s+",targetrange):
        aux=targetrange.split(" ")
        #print(aux)
        if len(aux)==1:
            result=int(aux[0])
        if len(aux)==3:
            result=str(aux[0])+"-"+str(clean_fraction(aux[2]))
        else:
            #print(aux)
            result=int(aux[0])+clean_fraction(aux[1])
    elif re.search("-",targetrange):
        aux=targetrange.split("-")
        if len(aux)==1:
            result=int(aux[0])
        else: 
            result=int(aux[0])+clean_fraction(aux[1])
    else: 
        
        result=clean_fraction(targetrange)
    return result

def clean_target(target):
    try:
        if np.isnan(target):
            pre_target=np.nan
            post_target=np.nan
    except:
        if len(target)==2:
            pre_target=clean_number(target[0])
            post_target=clean_number(target[1])
        if len(target)==1:
            pre_target=np.nan
            post_target=clean_number(target[0])
       
        
    return [pre_target,post_target]
    

def clean_policy_change(change,unit,action):
    try:
        if np.isnan(unit) or np.isnan(change):
            changef=np.nan 
            try:
                if np.isnan(action):
                    finalaction=np.nan 
            except:
                if action=="keep" or action=="maintain" or action=="unchanged" or action=="no change" or action=="did not take action":
                    finalaction="unchanged"
                    changef=0
                if action=="raise" or action=="rise":
                    finalaction="tightening"  
                if action=="lower" or action=="cut" or action=="decline" or action=="reduction":
                    finalaction="easing"

    except:
        change=change.strip()
        unit=unit.strip().replace(" ","")
        #print(unit)
        if unit=="percentage":
            changebp=int(clean_fraction(change)*100)
        if unit=="basispoints" or unit=="basispoint" or unit==None:
            changebp=int(change)
        
        if action=="lower" or action=="cut" or action=="decline" or action=="reduction" or action=="Reduction"  or action=="fall":
            changef=-int(changebp)
            finalaction="easing"
        elif action=="raise" or action=="rise":
            finalaction="tightening"  
            changef=int(changebp)  
        elif action=="keep" or action=="maintain" or action=="unchanged" or action=="no change" or action=="did not take action":
            finalaction="unchanged"
            changef=0
        else:
            finalaction=np.nan
            changef=np.nan
    return [changef,finalaction]

if __name__ == "__main__":
   main()

