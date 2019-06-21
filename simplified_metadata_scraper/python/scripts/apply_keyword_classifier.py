"""
Purpose: Do classification of bluebook alternatives based on a manual vocabulary
         and output the results
Status: Draft
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

df_result=pd.read_csv("../output/bluebook_alternatives_sample.csv")

keywords_ease=["lower","cut","cuts","decline","reduction","ease","reduce","easing"]
keywords_unchanged=["keep","unchanged","no change","maintained","maintain","remain","forego","continue"]
keywords_tighten=["raise","hike","raised","firm","firming","increase","tightening","rise","tighten","tighter"]

for alt in ["a","b","c","d","e"]:
    df_result.loc[:,"alt_"+alt+"_class"]=""
    ### Keyword classification
    for idx,row in df_result.iterrows():
        sentences=row["alt_"+alt+"_sentences"]
        #sentences=df_result[df_result['date']=="2006-12-12"]["alt_c_sentences"].item()
        keep_sentences=[]
          
        for sentence in sentences:
            pattern = "(alternatives?\s+[^"+alt+"])([^a-z])"
            if not re.search(pattern,sentence,re.IGNORECASE):
                keep_sentences.append(sentence)        
                    
        # Do counts for each keyword
        if len(keep_sentences)==0:
            df_result.loc[df_result['date']==row['date'],"alt_"+alt+"_class"]="No sentence"
        else:
            count_ease=0
            count_unchanged=0
            count_tighten=0
            for sentence in keep_sentences:
                
                for keyword in keywords_ease:
                    pattern = "[^a-z]"+keyword+"[^a-z]"
                    regex=re.compile(pattern,re.IGNORECASE)
                    for match in regex.finditer(sentence):
                        count_ease+=1
                        #print(match.group())
                
                for keyword in keywords_unchanged:
                    pattern = "[^a-z]"+keyword+"[^a-z]"
                    regex=re.compile(pattern,re.IGNORECASE)
                    for match in regex.finditer(sentence):
                        count_unchanged+=1
                        #print(match.group())                
                        
                for keyword in keywords_tighten:
                    pattern = "[^a-z]"+keyword+"[^a-z]"
                    regex=re.compile(pattern,re.IGNORECASE)
                    for match in regex.finditer(sentence):
                        count_tighten+=1
                        #print(match.group())
            #print("ease: ",count_ease,"unchanged: ",count_unchanged,"tighten:",count_tighten)
            
            counts=[count_ease,count_unchanged,count_tighten]
            new_count=[]
            if 0 in counts:
                new_count=counts.copy()
                new_count.remove(0)
            else:
                new_count=counts.copy()
            
            d_conflict=0
            if len(new_count)>=2:
                if sorted(new_count)[-1]==sorted(new_count)[-2]:
                    d_conflict=1

            
            sum_counts=sum(counts)
            labels=["ease","unchanged","tighten"]
            if not sum_counts==0 and not d_conflict==1:
                index_max = np.argmax([count_ease,count_unchanged,count_tighten])
                #print(labels[index_max])
                df_result.loc[df_result['date']==row['date'],"alt_"+alt+"_class"]=labels[index_max]
            else:
                df_result.loc[df_result['date']==row['date'],"alt_"+alt+"_class"]="No assignment"
      
df_result.sort_values('date', inplace=True)

df_result.to_csv("../output/bluebook_alt_and_class_output.csv")

### Get summary stats
alternative="b"
start_year=1994
end_year=1999
pd.pivot_table(df_result[(df_result['year']>=start_year) & (df_result['year']<=end_year)],'date',index=['alt_'+alternative+'_class'], \
               aggfunc=np.count_nonzero)
pd.pivot_table(df_result[df_result['year']>=start_year],'date',index=['alt_'+alternative+'_class'], \
               columns=['year'],aggfunc=np.count_nonzero)

# Check the no assignment cases
df_result[(df_result["alt_"+alternative+"_class"]=="No assignment") &  \
          (df_result['year']>=start_year) & (df_result['year']<=end_year)] \
          ["alt_"+alternative+"_sentences"].iloc[3]
          
