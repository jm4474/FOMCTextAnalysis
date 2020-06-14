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

def import_leaalttext(directory):
    # Import alternatives that Lea extracted
    emptylist=[]
    filenames = sorted(os.listdir(directory))
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
    
        # Restrict time period
    corpus_df['start_date']=pd.to_datetime(corpus_df['start_date_string'])
    corpus_df= corpus_df[(corpus_df['start_date']>="1988-01-01") & (corpus_df['start_date']<="2008-12-31")]                    
                        
    
        # Fill-in the missing corpora for time 3/20/01 - 1/27/04
    corpus_df = corpus_df[(corpus_df['start_date']<"2001-03-20") | (corpus_df['start_date']>"2004-01-29")]
    
        # Do a long reshape
    newnames = dict(zip(['a', 'b', 'c', 'd', 'e'] ,[ f"alt_{col}" for col  in ['a', 'b', 'c', 'd', 'e'] ]))
    corpus_df.rename(columns=newnames,inplace=True)
    corpus_df.drop(columns="start_date_string",inplace=True)
    
    len(corpus_df["start_date"].unique())
    
    corpus_long = pd.wide_to_long(corpus_df,"alt",i="start_date",j="alternative",sep="_",suffix="\w").reset_index()
    corpus_long.rename(columns={"alt":"text"},inplace=True)
    corpus_long = corpus_long.sort_values(["start_date","alternative"],ascending=(True, True))

    return corpus_long



directory = "../data/alternatives_corpora"
newdata = import_leaalttext(directory)