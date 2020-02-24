#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: olivergiesecke
1) Collect the data on the speakers and text for each alternative.
2) Do the regular pre-processing for each text entry.
3) Apply standard LDA
4) Provide summary statics how the probability mass lines up with the different alternatives.
5) Check alignment with the voting record.
"""
from nltk.corpus import stopwords
import pandas as pd
import numpy as np
from gensim.utils import simple_preprocess
import itertools  
import os


os.chdir(r"/users/olivergiesecke/Dropbox/MPCounterfactual/src/analysis/python/scripts")

## %% 1) Condense all the data in a sinle dataframe

# Speaker text
speakers = pd.read_csv("../output/speaker_data/speaker_corpus.csv")

# Alternatives that Anand collected
alternatives = pd.read_csv("../output/alternative_outcomes_and_corpus.csv")

alternatives = alternatives[["date","alt a corpus","alt b corpus","alt c corpus"]]
names = {"alt a corpus":"corpus_alta","alt b corpus":"corpus_altb","alt c corpus":"corpus_altc"}
alternatives.rename(columns=names,inplace=True)
alts = pd.wide_to_long(alternatives,stubnames="corpus", sep="_",i="date", j="alternatives", suffix='\w+')
alts=alts.reset_index()
alts.rename(columns={'date':'Date','alternatives':'Speaker','corpus':'content'},inplace=True)

data = pd.concat([speakers,alts])
data.drop(columns="Unnamed: 0",inplace=True)

## %% 2) Text pre-processing

# Extract tokens
def extract_token(sentence):
    return simple_preprocess(str(sentence), deacc=True)


def count_mostcommon(myList):
    counts = {}
    for item in myList:
        counts[item] = counts.get(item,0) + 1
    return counts

def remove_stopwords(words,stopwords):
    nostopwords=[]
    for word in words:
        if word not in stopwords:
            nostopwords.append(word)        
    return nostopwords
    
data['parsed']=data['content'].apply(extract_token)

# List the 100 most common terms
tot_token=[]
for row_index,row in data.iterrows():
    tot_token.extend(row['parsed'])
    
print('The corpus has %d token' % len(tot_token) )
counts=count_mostcommon(tot_token)
sorted_counts={k: v for k, v in sorted(counts.items(), key=lambda item: item[1],reverse=True)}

N = 100
out = dict(itertools.islice(sorted_counts.items(), N))  
words100 = [(k, v) for k, v in out.items()]
print('This are the most common 100 tokens without removing stopwords:')
print(words100)


# Remove stopwords
stop_words = stopwords.words('english')
stop_words.extend(["mr","chairman"])
wo_stopwords = remove_stopwords(tot_token,stop_words)

wo_counts=count_mostcommon(wo_stopwords)
sorted_wo_counts={k: v for k, v in sorted(wo_counts.items(), key=lambda item: item[1],reverse=True)}

# Do stemming

from nltk.stem.porter import PorterStemmer
p_stemmer = PorterStemmer()
wo_stem_word = [p_stemmer.stem(i) for i in wo_stopwords]

wo_counts=count_mostcommon(wo_stem_word)
sorted_wo_counts={k: v for k, v in sorted(wo_counts.items(), key=lambda item: item[1],reverse=True)}

N = 100
out = dict(itertools.islice(sorted_wo_counts.items(), N))  
wo_words100 = [(k, v) for k, v in out.items()]
print('This are the most common 100 tokens without removing stopwords:')
print(wo_words100)


# Do the LDA
import gensim
from gensim import corpora, models

texts=[]
for row_index,row in data.iterrows():
    item=row['parsed']
    item_wo_stem=[p_stemmer.stem(i) for i in remove_stopwords(item,stop_words)]
    texts.append(item_wo_stem)    

dictionary = corpora.Dictionary(texts)
corpus = [dictionary.doc2bow(text) for text in texts]

num_topics=5
ldamodel = models.ldamodel.LdaModel(corpus, num_topics, id2word = dictionary, passes=20)

sent_topics_df = pd.DataFrame()
for i, row in enumerate(ldamodel[corpus]):
    # Get the Dominant topic, Perc Contribution and Keywords for each document
    emptylist=[]
    for k in range(num_topics):          
        emptylist.append(0)
        for j, (topic_num, prop_topic) in enumerate(row):    
            if k==topic_num:
                emptylist[-1]=(round(prop_topic,4))
    sent_topics_df = sent_topics_df.append(pd.Series(emptylist), ignore_index=True)

coln = sent_topics_df.columns
coln = ['topic_%s'%c for c in coln]
sent_topics_df.columns=coln

data_lda = data.join(sent_topics_df)

# Apply SVD for dimensionality reduction
from sklearn.decomposition import TruncatedSVD

def reduce_to_k_dim(M, k=2):
    """ Reduce a co-occurence count matrix of dimensionality (num_corpus_words, num_corpus_words)
        to a matrix of dimensionality (num_corpus_words, k) using the following SVD function from Scikit-Learn:
            - http://scikit-learn.org/stable/modules/generated/sklearn.decomposition.TruncatedSVD.html
    
        Params:
            M (numpy matrix of shape (number of corpus words, number of corpus words)): co-occurence matrix of word counts
            k (int): embedding size of each word after dimension reduction
        Return:
            M_reduced (numpy matrix of shape (number of corpus words, k)): matrix of k-dimensioal word embeddings.
                    In terms of the SVD from math class, this actually returns U * S
    """    
    n_iters = 10     # Use this parameter in your call to `TruncatedSVD`
    M_reduced = None
    print("Running Truncated SVD over %i words..." % (M.shape[0]))
    
        # ------------------
        # Write your implementation here.
    svd = TruncatedSVD(n_components=k, n_iter=n_iters)
    svd.fit(M)
    M_reduced=svd.transform(M)


        # ------------------

    print("Done.")
    return M_reduced

abc=sent_topics_df.values

twodim = reduce_to_k_dim(abc)
df=pd.DataFrame(twodim )
df.columns=['PCI1','PCI2']

data_lda_pca = data_lda.join(df)


### Show the output based on a single example
import matplotlib.pyplot as plt
import re

def output_plot(date,data):
    plt.figure()
    data_example=data[data['Date']==date]
    for i, row in data_example.iterrows():
        if re.search("^alt[a-d]", row["Speaker"]):
            plt.scatter(row['PCI1'],row['PCI2'], edgecolors='k', c='b')
            plt.text(row['PCI1'],row['PCI2'], row["Speaker"])
            
        else:
            plt.scatter(row['PCI1'],row['PCI2'], edgecolors='k', c='r')
            plt.text(row['PCI1'],row['PCI2'], row["Speaker"])
    plt.title('Example %s' %date )
    plt.savefig('../output/example_%s.pdf'%date)
            
       
output_plot("1992-05-19",data_lda_pca)

output_plot("1999-11-16",data_lda_pca)

     
        
        
data_example=data[data['Date']=="1992-05-19"]
data_example["Speaker"]
        
        
    

