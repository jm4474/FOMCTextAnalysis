
"""
@author: olivergiesecke & anand
1) This script extracts voting members using the minutes of FOMC meetings, and then appends a manual verification for certain values.
2) Create a unique id for the speakers and save dictionary
3) Code dummies for each speakers voting record


FILES IN:
    ../data/fomc_dissents_data.xlsx
    ../../../collection/python/data/transcript_raw_text
    ../data/voter_corrections.csv

FILES OUT:
    ../output/votingrecord.csv

"""

import pandas as pd
import numpy as np
import itertools  
import os
import json
import ast
import re
import pprint
import logging
from ast import literal_eval

###############################################################################

def get_voters():
    df = pd.read_excel("../data/fomc_dissents_data.xlsx",skiprows=3)
    df["Date"] = df["FOMC Meeting"].apply(lambda x:str(x).split(" ")[0])
    df['FOMC Votes'] = df['FOMC Votes'].apply(lambda x:0 if np.isnan(x) else x)

    df['date'] = pd.to_datetime(df["Date"])
    df['start_date'] = df['date'] - pd.Timedelta('1 days')
    df['start_date']=df['start_date'].dt.date
    df['date']=df['date'].dt.date
    df[['date','start_date']].head()
        
    voter_df = pd.DataFrame()

    for index,row in df.iterrows():
        voters = []
        num_voters = int(row['FOMC Votes'])
        date_path = '../../../collection/python/data/transcript_raw_text/{}.txt'.format(row['Date'])
        if not os.path.exists(date_path):
            #print("Date not found")
            date_path = '../../../collection/python/data/transcript_raw_text/{}.txt'.format(row['start_date'])
            if not os.path.exists(date_path):
                print("Alternative date not found")
                continue
            else:
                print('Process alternative date')
        with open(date_path) as f:
            broken = False
            broken_starts = 0
            broken_ends = 0
            lines = f.readlines()
            
            '''First Check For Broken Title'''

            #print("CHECKING USING FRAGMENT HEURISTIC")
            for line in lines[:200]:
                if line.strip():
                    if broken_ends==0:
                        title_frag = re.match(r'^(?:PRESENT: |PRESENT. )?(?:Mr.|Ms.|Mt.|Mrs. )$',line.strip())
                        if title_frag:
                            if not broken:
                                broken = True
                            #print("Broken Begining")
                            #print(title_frag.group(0))
                            title_frag_string = str(title_frag.group(0)).replace("PRESENT: ","")
                            voters.append(title_frag_string)
                            broken_starts+=1
                            continue
                    if broken and broken_ends<len(voters):
                        name_fragment = re.match('^[A-Z][a-z][A-Za-z]*',line.strip())
                        if name_fragment:
                            voters[broken_ends] = voters[broken_ends]+" "+str(name_fragment.group(0))
                            broken_ends+=1
            
            '''Check using Mr. Regex'''
            
            if len(voters)==0:
                #print("CHECKING TITLE REGEX")
                for line in lines[:200]:
                    '''Then check for valid input'''
                    voter_line = re.findall(r'(?:Mr.|Ms.|Mrs.) [A-Z][a-zA-Z]*',line.strip())
                    if voter_line:
                        #print(voter_line)
                        voters.append(voter_line[0])
                        if len(voters)>=num_voters:
                            break
            
            '''Check Last Name Regex'''
            
            if len(voters) == 0:
                #print("Checking POST-PRESENT-NAME HEURISTIC")
                found_present = False
                for line in lines[:200]:
                    if "PRESENT:" in line.strip() or "PRESENT." in line.strip():
                        found_present = True
                        present_line = line.split(",")[0].strip().replace("PRESENT","")
                        name_text = re.match('[A-Z][a-z]*\s?(?:[A-Z][a-z]*)?',present_line)
                        if name_text:
                            voters.append(name_text.group(0))
                        continue
                    if found_present:
                        #print(line)
                        name_text = re.match('[A-Z][a-z]*\s?(?:[A-Z][a-z]*)?',line.split(",")[0].strip())
                        if name_text:
                            voters.append(name_text.group(0))
                        if len(voters)>=num_voters:
                            break
        #print('Date:{}'.format(row['Date']))
        #print("Broken Status:{}".format(broken))
        #print("Voter Number:{}".format(num_voters))
        #print("Voters Found:{}".format(len(voters)))
        #pprint.pprint(voters)
        voter_df = voter_df.append({
            "Date":row['FOMC Meeting'],
            "voters_expected":num_voters,
            "voters_observed":len(voters),
            "Voters":voters if num_voters==len(voters) else None,
        },ignore_index=True)
    #print("="*50)
    #print(voter_df)
    return voter_df

def get_errors(voter_df):
    #print(len(voter_df[voter_df["Voters"].isna()]))

    voter_errors = voter_df[voter_df["Voters"].isna()].reset_index(drop=True)
    voter_errors.to_csv("../output/voter_errors.csv",index=False)

def merge_error_correction(voter_df):
    correction_df = pd.read_csv("../data/voter_corrections.csv")
    correction_df['Date'] = pd.to_datetime(correction_df['Date'])
    voter_df['Date'] = pd.to_datetime(voter_df['Date'])
    voter_df = pd.concat([voter_df,correction_df])
    voter_df = voter_df.drop_duplicates(['Date'], keep="last").sort_values(by="Date")
    voter_df = voter_df[(voter_df['Date'].dt.year>1987)&(voter_df['Date'].dt.year<2010)]
    
    voter_df = voter_df.reset_index()
    for idx,row in voter_df.iterrows():
        #print(type(row["Voters"])!=str)
        if type(row["Voters"])!=str:
            voter_df.loc[idx,"Voters"] = str(row["Voters"])
    return voter_df

def create_speakerids(data):
    votingmembers=[]
    for idx,row in data["Voters"].dropna().iteritems():
        name_list=ast.literal_eval(row)
        for item in name_list:
            #print(item)
            newitem=re.search("(^M[r-s]\.\s+)(\w+)",item)[2]

            if newitem not in votingmembers:
                votingmembers.append(newitem)
    
    votingmembers.sort()
    index=[f"id_{i}" for i in range(0,len(votingmembers))]
    speakerid = dict(zip(votingmembers,index))
    
    with open('../output/data.json', 'w') as speakerids:
        json.dump(speakerid, speakerids)
        
    return speakerid


def create_votingrecord(datainput,speakerid):
    data=[]
    for idx,row in datainput[~datainput["Voters"].isna()].iterrows():
        dic={}
        date=row["Date"]
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
    voter_df = get_voters()
    get_errors(voter_df)
    
    voterdata = merge_error_correction(voter_df)
    
    voterdata['date'] = pd.to_datetime(voterdata['Date']).dt.date
    excel_df = pd.read_excel("../data/fomc_dissents_data.xlsx",skiprows=3)
    excel_df['FOMC Votes'] = excel_df['FOMC Votes'].apply(lambda x:0 if np.isnan(x) else x)
    excel_df['date'] = excel_df["FOMC Meeting"].dt.date
    excel_df = excel_df[~excel_df["Chair"].isna()]
    merge_df = voterdata.merge(excel_df,left_on="date",right_on="date",how="left")
      
    speakerid = create_speakerids(merge_df)
    dataout = create_votingrecord(merge_df,speakerid ).sort_values(by="date")
    
    
    speakerid = dict((k.lower(), v) for k, v in speakerid.items()) 

    invspeakerid = dict((v,k) for k, v in speakerid.items()) 
    
    dataout=dataout[dataout["date"]<="2008-12-31"] 
    
    dataout["speaker"] = dataout['speaker_id'].map(invspeakerid)
    
    colorder = ["speaker"] + [col for col in dataout.columns if col!="speaker"]
    dataout = dataout[colorder]
    
    print(f"Number of votes in the data: {len(dataout[dataout['votingmember']==1])}; 1905 voters in D. Thornton")
    
    dataout.to_csv("../output/votingrecord.csv",index=False)

if __name__== "__main__":
    main()
    
