#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: olivergiesecke
1) Load the data from Anand
2) Create a unique id for the speakers and save dictionary
3) Code dummies for each speakers voting record
"""

import pandas as pd
import numpy as np
import itertools  
import os
import json
import ast
import re

###############################################################################

def create_speakerids(data):
    votingmembers=[]
    for idx,row in data["Voters"].dropna().iteritems():
        name_list=ast.literal_eval(row)
        for item in name_list:
            newitem=re.search("(^M[r-s]\.\s)(\w+)",item)[2]
            if newitem not in votingmembers:
                votingmembers.append(newitem)
    
    votingmembers.sort()
    index=[f"id_{i}" for i in range(0,len(votingmembers))]
    speakerid = dict(zip(votingmembers,index))
    
    with open('data.json', 'w') as speakerids:
        json.dump(speakerid, speakerids)
        
    return speakerid


def create_votingrecord(datainput,speakerid):
    data=[]
    for idx,row in datainput[~datainput["Voters"].isna()].iterrows():
        dic={}
        date=row["date"]
        #print(date)
        dic.update({"date":date})
        for key, value in speakerid.items():
            dic.update({"votingmember_"+value:0})
            dic.update({"ambdiss_"+value:0})
            dic.update({"tighterdiss_"+value:0})
            dic.update({"easierdiss_"+value:0})
            
            
            name_list=ast.literal_eval(row["Voters"])
            for item in name_list:
                newitem=re.search("(^M[r-s]\.\s)(\w+)",item)[2]
                
                if key == newitem:
                    d1={"votingmember_"+value:1}
                    #print({value:1})
                    dic.update(d1)
            
        if str(row['Dissenters Other/Indeterminate']) != "nan":
            new = row['Dissenters Other/Indeterminate'].split(",")
            for newitem in new:
                newitems=newitem.strip()
                #print(speakerid[newitems])
                newdc = {"ambdiss_"+speakerid[newitems]:1}
                dic.update(newdc)
                
        if str(row['Dissenters Tighter']) != "nan":
            new = row['Dissenters Tighter'].split(",")
            for newitem in new:
                newitems=newitem.strip()
                #print(speakerid[newitems])
                newdc = {"tighterdiss_"+speakerid[newitems]:1}
                dic.update(newdc)
                
        if str(row['Dissenters Easier']) != "nan":
            new = row['Dissenters Easier'].split(",")
            for newitem in new:
                newitems=newitem.strip()
                #print(speakerid[newitems])
                newdc = {"easierdiss_"+speakerid[newitems]:1}
                dic.update(newdc)
                
        data.append(dic)
        
    votingrecord = pd.DataFrame(data)
    
    # Do a few checks of the dataframe
    vot_cols = [col for col in votingrecord.columns if re.match("^id\_[0-9]",col)]
    new_df=pd.concat([votingrecord[["date"]+vot_cols].sum(axis=1),votingrecord["date"]],axis=1)
    
    vot_cols = [col for col in votingrecord.columns if re.match("^easierdissid\_[0-9]",col)]
    new_df=pd.concat([votingrecord[["date"]+vot_cols].sum(axis=1),votingrecord["date"]],axis=1)
    
    #print(votingrecord.columns)
    
    votingrecord_long=pd.wide_to_long(votingrecord,stubnames=["votingmember","ambdiss","tighterdiss","easierdiss"],i="date",j="speaker_id",sep="_",suffix='\w+')
    votingrecord_long=votingrecord_long.reset_index()
    
    return votingrecord_long
    
    
def main():
    voterdata = pd.read_csv("../output/alternatives_corpus_and_voting_information.csv")
    speakerid = create_speakerids(voterdata)
    dataout = create_votingrecord(voterdata,speakerid )

    dataout.to_csv("../output/votingrecord.csv",index=False)

if __name__== "__main__":
    main()
    
