"""
Purpose: Outputs the statistics of the bluebook alternatives
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
# Open points:
# 1) Handling of footnotes. Right now, they are mixed into sentence at the end 
# of the page. This interrupts the sentence that do not end at the end of the 
#page.
# 2) Think about the use of nltk for the extraction of the relevant information
# 3) Adjust the cloud of words to be more relevant to our objective.


# Do the merge with the news data
# Do the merge with the statements 


###############################################################################


### Define table output 
def create_table(data,name):
    # Output the table
    columnheaders=list(data[0].keys())[1:]
    keysofdict=list(data[0].keys())
    numbercolumns=len(data[0])
    with open("../output/"+name+".tex", "w") as f:
        f.write(r"\begin{tabular}{"+"l" + "".join("c" * (numbercolumns-1)) + "}\n")
        f.write("\\hline\\hline \n")
        f.write(" & "+" & ".join([x for x in columnheaders]) + " \\\ \n")    
        f.write("\\hline \n")
        # write data
        for idx,entry in enumerate(data):

            # Do formatting for specific tables 
            if name=="tab_aggsum":
                if idx==1:
                    f.write("\\addlinespace"+" \n")
                if idx==2:
                    f.write("\\textit{of which:} \\\ \n")
            if name=="tab_summary_count":
                if idx==1:
                    f.write("\\addlinespace"+" \n")
                    
            entries=[]
            for key in keysofdict:
                entries.append(str(entry[key]))
            f.write(" & ".join(entries) + " \\\ \n")
        f.write("\\hline \n")
        f.write(r"\end{tabular}")


### Create cloud of words

def remove_stopwords(words,stopwords):
    nostopwords=[]
    for word in words:
        if word not in stopwords:
            nostopwords.append(word)        
    return nostopwords
    
def lemmatization(texts, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV']):
    """https://spacy.io/api/annotation"""
    texts_out = []
    # Initialize spacy 'en' model, keeping only tagger component (for efficiency)
    # python3 -m spacy download en
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(" ".join(texts)) 
    texts_out.append([token.lemma_ for token in doc if token.pos_ in allowed_postags])
    return texts_out
    

def create_cloudwords(sentences,name):
    stop_words = stopwords.words('english')
       
    # Manual extraction of words
    data_man="".join(sentences)
    words_man=data_man.replace(".", " ")
    
    # Gensium extraction of words
    def sent_to_words(sentences):
        for sentence in sentences:
            yield(gensim.utils.simple_preprocess(str(sentence), deacc=True))  # deacc=True removes punctuations
    
    wordsperphrase = list(sent_to_words(sentences))
    words_model=[]
    for phrase in wordsperphrase:
        for word in phrase:
            words_model.append(word)
        
    # Do some simple comparison
    print("Manual word count: ",len(words_man))
    print("Model word count: ",len(words_model))
    
    # Assign the words
    data_words=words_model
        
    # Remove Stop Words
    data_words_nostops = remove_stopwords(data_words,stop_words)
    
    # Do lemmatization keeping only noun, adj, vb, adv
    data_lemmatized = lemmatization(data_words_nostops, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV'])
     
# =============================================================================
#     # Define functions for stopwords, bigrams, trigrams and lemmatization
#     # Build the bigram and trigram models
#     bigram = Phrases(data_lemmatized[0], min_count=1, threshold=0.1) # higher threshold fewer phrases.
#     trigram = Phrases(bigram[data_lemmatized[0]], threshold=.1)  
#     
#     bigram_mod = Phraser(bigram)  # construct faster model (this is only an wrapper)
#     bigram_mod[data_lemmatized[0]]  # apply model to sentence
#     
#     print("original",len(data_lemmatized[0]),"processed",len(bigram_mod[data_lemmatized[0]]))
#     
# =============================================================================
    
    wordcloud = WordCloud(width = 1600, height = 1600, 
                    background_color ='white', 
                    min_font_size = 10).generate(" ".join(data_lemmatized[0])) 
      
    # plot the WordCloud image                        
    plt.figure(figsize = (8, 8), facecolor = None) 
    plt.imshow(wordcloud) 
    plt.axis("off") 
    plt.show() 
    
    plt.savefig("../output/"+name+".png")
    


###  Do some summary statistics ###
df_output=pd.read_csv("../../../derivation/python/output/bluebook_alternatives.csv")
df_output['year']=pd.to_numeric(df_output['meeting_date'].str[:4])
df_output['date']=pd.to_datetime(df_output['meeting_date'])
df_result=df_output[(df_output['date']<="2009-03-18") & (df_output['date']>="1968-08-13")]


if not os.path.isdir("../output"):
    os.mkdir("../output/")

## Aggregate Statistics ##
# Number of bluebooks
dat_list=[]
columnname="Number of Meetings with Bluebooks "

entry="Total"
print(entry,len(df_output))
dat_list.append({"entry":entry, columnname:len(df_output)})

# Number of meetings between 19680813-20090317
entry=r"In Period 08/13/1968-03/17/2009"
print(entry,len(df_result))
dat_list.append({"entry":entry, columnname:len(df_result)})

# Number with alt between 19680813-20090317
entry=r"...with mentioning of alternative(s)"
number=len(df_result[df_result['n_sentences']>0])
print(entry,number)
dat_list.append({"entry":entry, columnname:number})

# Number of meetings with alt A
for alt in ["a","b","c","d","e"]:
    entry=r"...mentioning of alternative {"+alt.upper()+"}"
    number=len(df_result[df_result["alternative_"+alt+"_count"]>=1])
    print(entry,number)
    dat_list.append({"entry":entry, columnname:number})

# Create the table for latex import
create_table(dat_list,name="tab_aggsumstat")

## Get counts per alternative [No plural here] ##

# Total counts
totalcount={"counter":"Total"}
for alt in ["a","b","c","d","e"]:
    val=df_result[df_result["alternative_"+alt+"_count"]>=1]["alternative_"+alt+"_count"].sum()
    totalcount.update({"Alternative "+alt.upper():val})

countbynumber=[totalcount]
for count in range(1,11):
    counter={"counter":count}
    for alt in ["a","b","c","d","e"]:    
        val=len(df_result[df_result["alternative_"+alt+"_count"]==count])
        counter.update({"Alternative "+alt.upper():val})
    countbynumber.append(counter)
    
counter={"counter":"$>10$"}
for alt in ["a","b","c","d","e"]:    
    val=len(df_result[df_result["alternative_"+alt+"_count"]>10])
    counter.update({"Alternative "+alt.upper():val})
countbynumber.append(counter)

create_table(countbynumber,name="tab_summary_count")

## Show the mentioning of alternative {A-E} graphically

fig, ax = plt.subplots()
for alt in ["a","b","c","d","e"]:    
    df_result.loc[:,"d_alt_"+alt]=df_result["alternative_"+alt+"_count"]>=1
    df_result.loc[:,"d_alt_label_"+alt]=""
    df_result.loc[df_result["d_alt_"+alt]==True,"d_alt_label_"+alt]="Alt. "+alt.upper()
    ax.plot_date(df_result["date"],df_result["d_alt_label_"+alt],marker='o',markersize=3)

ax.set_ylim(["Alt. A","Alt. E"])

fig.savefig('../output/fig_alt_time.png')
# =============================================================================
# 
# ## Show the bigrams associated with each alternative
# 
# for alt in ["a","b","c","d","e"]:
#     phrases=df_result[df_result["alternative_"+alt+"_count"]>=1]["alt_"+alt+"_sentences"].tolist()
#     sentences=[]
#     for phrase in phrases:
#         for sentence in phrase:
#             sentences.append(sentence)
#     create_cloudwords(sentences,name="fig_cloudwords_"+alt)
# 
# 
# =============================================================================

