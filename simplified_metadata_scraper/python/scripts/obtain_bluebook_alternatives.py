"""
Purpose: Loads the bluebook data from the raw files and extracts the sentences 
         that are affiliated with the alternatives
@author: olivergiesecke
"""

###############################################################################
### Set packages ###

import pandas as pd
import re
import os
import matplotlib.pyplot as plt


from nltk.corpus import stopwords
import gensim
import gensim.corpora as corpora
from gensim.utils import simple_preprocess
from gensim.models.phrases import Phrases, Phraser
# spacy for lemmatization
from distutils.core import setup
from Cython.Build import cythonize
import spacy
from wordcloud import WordCloud
import numpy as np

###############################################################################
# Open points:
# 1) Handling of footnotes. Right now, they are mixed into sentence at the end 
# of the page. This interrupts the sentence that do not end at the end of the 
#page.
# 2) Think about the use of nltk for the extraction of the relevant information
# 3) Adjust the cloud of words to be more relevant to our objective.


# Do the merge with the news data
# Do the merge with the statements 


###############################################################################
    
### Define data download
def getdata_bluebook():
    # Get all files except the hidden
    doc_list=[]
    for item in os.listdir("../../../collection/python/output/bluebook_raw_text/"):
        if not item.startswith('.'):
            doc_list.append(item)
    
    files=[]
    for idx,doc in enumerate(doc_list):
        print(idx," Working on file", doc)
        # Do for specific document
        #doc=doc_list[20]
        
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
    return pd.DataFrame(files)
    

###############################################################################

### Read data and define sample ###
df_output=getdata_bluebook()
df_output['year']=pd.to_numeric(df_output['meeting_date'].str[:4])
df_output['date']=pd.to_datetime(df_output['meeting_date'])
df_result=df_output[(df_output['date']<="2009-03-18") & (df_output['date']>="1968-08-13")]
# Write data frame to csv
df_output.to_csv("../output/bluebook_alternatives_population.csv")
df_result.to_csv("../output/bluebook_alternatives_sample.csv")
