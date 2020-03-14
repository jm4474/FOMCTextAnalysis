"""
Author: Oliver Giesecke
Purpose: Constructs the set of alternatives with quantitative classification
and the corresponding corpus. This fills in the deviations in the 
3/20/01 - 1/27/04 period.
"""


import pandas as pd
import os
import re
import numpy as np
# =============================================================================
#     # what is the bluebook count in the period
#     
# path = "../../../collection/python/output/bluebook_pdfs/"
# filelist = os.listdir(path)
# filelist = sorted(filelist)
# filelist = [item.replace(".pdf","") for item in filelist]
# 
# dates_df= pd.DataFrame(filelist)
# dates_df['date']=pd.to_datetime(dates_df[0])
# 
# subset_dates = dates_df[(dates_df['date']>="1988-01-01") & (dates_df['date']<="2008-12-31")]
# number_bb = len(subset_dates )
# print(f"The number of Bluebooks in the time 1988-2008 are: {number_bb}")
# 
#     # check whether in the subset of dates the monthly date is unique
#     
# subset_dates['month'] = subset_dates['date'].dt.month
# subset_dates['year'] = subset_dates['date'].dt.year
# 
# len(subset_dates[['year','month']].drop_duplicates()) # it is unique
# 
#     # Check whether the Lea's corpora coincide with the list
# filenames = os.listdir("../data/alternatives_corpora")
# filenames  = [filename.replace(".txt","") for filename in filenames]
# filenames = sorted(filenames)
#     
# for filename in filenames:
#     print(filename)
#     if str(filename) in filelist:
#         print('yes')
#     else:
#         print('no')
#         
#     # Check whether changes in the federal funds rate coincide in length and in the date
# 
# target_df = pd.read_csv("../output/fed_targets_with_alternatives.csv")
# target_df.drop(columns="Unnamed: 0",inplace=True)
# target_df.rename(columns={'date':'datestring'},inplace=True)
# # Dates do not coincide
# 
# target_df['date']=pd.to_datetime(target_df['datestring'])
# target_df['month'] = target_df['date'].dt.month
# target_df['year'] = target_df['date'].dt.year
# 
# target_df['dup']= target_df.duplicated(subset=['year','month'],keep=False)
# target_df[target_df['dup']==True]
# target_df = target_df[target_df['date']!="2003-09-15"] # drop erroneous entry
# len(target_df) # same length as bb count
# 
# datelist = target_df['start_date'].tolist()
# for filename in datelist:
#     print(filename)
#     if str(filename) in filelist:
#         print('yes')
#     else:
#         print('no')
# #  Start dates coincide
# =============================================================================
        
################################################################################



# =============================================================================
# # EXAMPLE
# df = pd.DataFrame()
# filename = "../data/alternatives_corpora/2008-09-16.txt"
# alternatives = {'date':'2008-09-16','a':'aa','b':[],'c':[],'d':[],'e':[]}
# with open(filename) as f:
#     for line in f.readlines():
#         print(line)
#         
#         if line.strip():
#             split = re.split("[a-z]\s[A-Z]{3,4}\s\d*",line.strip(),1)
#             if len(split)>1:
#                 alt = line.strip()[0]
#                 alternatives[alt].append(split[1])
# 
# df = pd.DataFrame([alternatives])
# 
# print(alternatives)
# 
# =============================================================================
        
emptylist=[]
filenames = sorted(os.listdir("../data/alternatives_corpora"))
for filename in filenames:
    if ".txt" not in filename:
        print("not a txt file")
        continue
    # get start date
    start_date = filename.replace(".txt","")
        
    alternatives = {'start_date_string':start_date,'a':[],'b':[],'c':[],'d':[],'e':[]}
    with open(f"../data/alternatives_corpora/{filename}") as f:
        for line in f.readlines():
            if line.strip():
                split = re.split("[a-z]\s[A-Z]{3,4}\s\d*",line.strip(),1)
                if len(split)>1:
                    alt = line.strip()[0]
                    alternatives[alt].append(split[1])
    emptylist.append(alternatives)
corpus_df = pd.DataFrame(emptylist)

corpus_df['start_date']=pd.to_datetime(corpus_df['start_date_string'])
corpus_df= corpus_df[(corpus_df['start_date']>="1988-01-01") & (corpus_df['start_date']<="2008-12-31")]                    
                    
target_df = pd.read_csv("../output/fed_targets_with_alternatives.csv")
target_df.drop(columns="Unnamed: 0",inplace=True)
target_df.rename(columns={'start_date':'datestring'},inplace=True)
target_df['start_date']=pd.to_datetime(target_df['datestring'])
target_df = target_df[target_df['date']!="2003-09-15"] # drop erroneous entry

merge_df = pd.merge(target_df,corpus_df,on="start_date",how='outer',indicator=False)
new_col = dict(zip([alt for alt in ['a','b','c','d','e']],[f"alt {alt} corpus" for alt in ['a','b','c','d','e']]))
merge_df.rename(columns = new_col ,inplace=True)
# merge is perfect -- 168 bbs #

    # Fill-in the missing corpora for time 3/20/01 - 1/27/04
merge_df = merge_df[(merge_df['date']<"2001-03-20") | (merge_df['date']>"2004-01-29")]
fillin_df = pd.read_csv("../output/fed_targets_with_alternatives_missinbb.csv")
fillin_df['start_date']=pd.to_datetime(fillin_df['start_date'] )

all_df = pd.concat([merge_df,fillin_df],join="inner",axis=0,ignore_index=True)

all_df.sort_values(by="date",inplace=True)

    # Try to identify the alternative that has been chosen
all_df = all_df.reset_index()
for alt in ['a','b','c','d']:
    all_df[f"bluebook_treatment_size_alt_{alt}"] = pd.to_numeric(all_df[f"bluebook_treatment_size_alt_{alt}"], errors='coerce')
    # Create tie breaker    
    all_df[f"d{alt}"] = pd.DataFrame(np.divide((np.sign(all_df['decision'].values) == np.sign(all_df[f"bluebook_treatment_size_alt_{alt}"].values)).astype(int), 100))    
for alt in ['a','b','c','d']:    
    all_df[f"alt{alt}"] = pd.DataFrame(np.abs(all_df['decision'].values - all_df[f"bluebook_treatment_size_alt_{alt}"].values) - all_df[f"d{alt}"].values)

col_alts = [col for col in all_df.columns if re.match("^alt[a-d]",col)]
all_df["act_chosen"] = all_df[col_alts].idxmin(axis=1)
all_df.loc[all_df['date']=="2008-12-16" , "act_chosen"]="alta"

    # Identify easier and tighter policy alternatives
all_df["vote_tighter"]=np.nan
all_df["vote_easier"]=np.nan
for idx,row in all_df.iterrows():
    ch_alt = row["act_chosen"][-1:]
    treatment_size = row[f"bluebook_treatment_size_alt_{ch_alt}"] 
       
    easierlist=[]
    tighterlist=[]
    for alt in ['a','b','c','d']:
        if row[f"bluebook_treatment_size_alt_{alt}"] < treatment_size:
            easierlist.append(f"alt{alt}")        
        if row[f"bluebook_treatment_size_alt_{alt}"] > treatment_size:
            tighterlist.append(f"alt{alt}")        
    
    all_df.loc[idx,"vote_tighter"]=", ".join(tighterlist)
    all_df.loc[idx,"vote_easier"]=", ".join(easierlist)
    

alternative_results = all_df[['date','act_chosen', 'vote_tighter', 'vote_easier']]
all_df = all_df.drop(columns=['act_chosen', 'vote_tighter', 'vote_easier','da', 'db', 'dc', 'dd', 'alta', 'altb', 'altc', 'altd'])

alternative_results.to_csv("../output/alternative_results.csv")
all_df.to_csv("../output/alternative_outcomes_and_corpus.csv")


# =============================================================================
# 
# 
# all_df['date'] = pd.to_datetime(all_df['date'])
# all_df['mergetime']=all_df['date'].dt.date
# 
# voting_mem= pd.read_csv("../output/voting_members.csv")
# voting_mem['date'] = pd.to_datetime(voting_mem["Date"]).dt.date
# 
# all_df = all_df.merge( voting_mem , left_on="mergetime",right_on="date",how="left")
# 
# 
# 
# =============================================================================




