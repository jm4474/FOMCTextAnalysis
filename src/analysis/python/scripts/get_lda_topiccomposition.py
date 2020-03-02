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
import gensim
from gensim import corpora, models
from nltk.stem.porter import PorterStemmer
from sklearn.decomposition import TruncatedSVD
import matplotlib.pyplot as plt
import re

import create_lda_data

###############################################################################


# Define functions

def extract_token(sentence):
    return simple_preprocess(str(sentence), deacc=True)

def count_mostcommon(myList):
    counts = {}
    for item in myList:
        counts[item] = counts.get(item,0) + 1
    return counts

def remove_stopwords(words,stopwords):
    nostopwords=[ word for word in words if word not in stopwords]
    return nostopwords

def do_stemming(words):
    p_stemmer = PorterStemmer()
    stemmed_words = [p_stemmer.stem(i) for i in words]
    return stemmed_words 

def create_wordcounts(stop_words):
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
    print(f'This are the most common {N} tokens without removing stopwords:')
    print(words100)
    
    # Remove stopwords
    wo_stopwords = remove_stopwords(tot_token,stop_words)
    
    wo_counts=count_mostcommon(wo_stopwords)
    sorted_wo_counts={k: v for k, v in sorted(wo_counts.items(), key=lambda item: item[1],reverse=True)}
    
    # Do stemming
    
    wo_stem_word = do_stemming(wo_stopwords)
    
    wo_counts=count_mostcommon(wo_stem_word)
    sorted_wo_counts={k: v for k, v in sorted(wo_counts.items(), key=lambda item: item[1],reverse=True)}
    
    out = dict(itertools.islice(sorted_wo_counts.items(), N))  
    wo_words100 = [(k, v) for k, v in out.items()]
    print(f'This are the most common {N} tokens with removing stopwords and stemming:')
    print(wo_words100)

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
    print("Running Truncated SVD over %i texts..." % (M.shape[0]))
    
    svd = TruncatedSVD(n_components=k, n_iter=n_iters)
    svd.fit(M)
    M_reduced=svd.transform(M)
 
    print("Done.")
    return M_reduced

def extract_vectors(ldamodel,num_topics,corpus): 
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
    return sent_topics_df

def output_plot(date,data):
    plt.figure()
    for i, row in data.iterrows():
        if re.search("^alt[a-d]", row["speaker"]):
            plt.scatter(row['PCI1'],row['PCI2'], edgecolors='k', c='b')
            plt.text(row['PCI1'],row['PCI2'], row["speaker"])
            
        else:
            plt.scatter(row['PCI1'],row['PCI2'], edgecolors='k', c='r')
            plt.text(row['PCI1'],row['PCI2'], row["speaker"])
    plt.title('Example %s' %date )
    plt.savefig('../output/example_%s.pdf'%date)


###############################################################################
    
    # Import data
data = create_lda_data.main()
data = data.reset_index()
data_light = data[['d_alt','date', 'speaker', 'speaker_id', 'votingmember', 'ambdiss','tighterdiss', 'easierdiss']]

    # Do simple preprocessing
data['parsed']=data['content'].apply(extract_token)

    # Revome stopwords and do stemming
stopwords = stopwords.words('english')
stopwords.extend(["mr","chairman"])
data['parsed_cleaned']=data['parsed'].apply(lambda x: do_stemming(remove_stopwords(x,stopwords)))

    # Build corpus
texts=[]
for row_index,row in data.iterrows():
    item=row['parsed_cleaned']
    texts.append(item)    

dictionary = corpora.Dictionary(texts)
corpus = [dictionary.doc2bow(text) for text in texts]

    # Do LDA
num_topics=5
ldamodel = models.ldamodel.LdaModel(corpus, num_topics, id2word = dictionary, passes=20)

    # Extract topic vectors
sent_topics_df = extract_vectors(ldamodel,num_topics,corpus)
data_lda =  pd.concat([data_light,sent_topics_df],axis=1, join='inner')

    # Apply SVD for dimensionality reduction
col_topics = [ col for col in data_lda.columns if re.match("^topic",col)]
dfvalues=data_lda[col_topics].values
twodim = reduce_to_k_dim(dfvalues)
df_pca=pd.DataFrame(twodim)
df_pca.rename(columns={0:'PCI1',1:'PCI2'},inplace=True)
data_lda_pca = pd.concat([data_lda,df_pca],axis=1, join='inner')

    # Show a single example

data_lda_pca['date'].unique()

date='1995-07-05'
dataexample = data_lda_pca[(data_lda_pca['d_alt']==1) | (data_lda_pca['votingmember']==1)][data_lda_pca['date']==date]
output_plot("1992-11-17",dataexample)


        
    

