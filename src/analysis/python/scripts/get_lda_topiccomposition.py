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
pd.set_option('mode.chained_assignment', None)

###############################################################################


# Define functions
    # Calculate Hellinger distance which is between 0 and 1.
def hellinger(x,y,col_topics):
    array1 = x[col_topics].values[0]
    array2 = y[col_topics].values[0]
    helpvar = np.sqrt(1 - np.sum(np.sqrt(np.multiply(array1,array2))))
    return helpvar

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

def create_distance(date,data):
    emptylist=[]
    for speaker in data.loc[(data['date']==date) & (data['votingmember']==1),"speaker"].to_list():
        dic={'date':date,'speaker':speaker}
        z=data[(data['date']==date) & (data['speaker']==speaker)]
        #print(z)
        for alt in ['a','b','c','d','e']:
            zz=data[(data['date']==date) & (data['speaker']=='alt'+alt)]
            #print(zz)
            
            if zz.index.empty or z.index.empty:
                pass
            else:
                dist=hellinger(z,zz,col_topics)
                dic.update({'alt'+alt:dist})
        emptylist.append(dic)        
        
    distances = pd.DataFrame(emptylist)
    return distances

###############################################################################

    # Import data
data = create_lda_data.main()
data.rename(columns={"start_date":"date"},inplace=True)
data.to_csv("../output/lda_dataset.csv",index=False)

    # Produce summary stats
data['new']=1
df_balt=data[data['d_alt']==1].pivot_table(index="date",values='new',aggfunc=np.sum).reset_index()
df_summary = data.pivot_table(index="date",values='new',columns=['d_alt','votingmember'],aggfunc=np.sum)

###############################################################################
    # Make a data selection and learn the model #

## Keep only dates for which alternatives are available and speakers who are votingmembers
data_speakers=data[data['votingmember']==1].merge(df_balt,on='date',how='inner')
data_alternatives=data[data['d_alt']==1]

print("### SUMMARY STATISTICS ###\n")
print("Number of speaker dates: %d" % len(data_speakers['date'].unique()))
print("Number of alternative dates: %d" % len(data_alternatives['date'].unique()))

print("Number of words for the speakers is: %s million" % (len(" ".join(data_speakers['content'].tolist())) / 1e6))
print("Number of words for the alternatives is: %s million" % (len(" ".join(data_alternatives['content'].tolist())) / 1e6 ))
## Speakers have roughly 10x the number of words

# =============================================================================
#     # Subsample the speakers -- only to learn the model
# data_speakers_subsample = data_speakers.sample(frac =.1 ,random_state=5) 
# print("Number of words for the subsample of speakers is: %s" % (len(" ".join(data_speakers_subsample ['content'].tolist())) / 1e6))
# data_sel = pd.concat([data_speakers_subsample,data_alternatives],axis=0, join='inner')
# data_sel = data_sel.reset_index()
# =============================================================================

    # Learn the model based only on basis of the alternatives
print("\n### MODEL ESTIMATION - ALTERNATIVES ONLY ###\n")
data_sel = data_alternatives.reset_index()

    # Do simple preprocessing
data_sel['parsed']=data_sel['content'].apply(extract_token)

    # Revome stopwords and do stemming
stopwordsnltk = stopwords.words('english')
stopwordsnltk.extend(["mr","chairman","yes"])
add_list = ["presid", "governor", "would","think","altern","could","committe","may"]
data_sel['parsed_cleaned']=data_sel['parsed'].apply(lambda x: remove_stopwords(do_stemming(remove_stopwords(x,stopwordsnltk)),add_list))

    # Build corpus
texts=[]
for row_index,row in data_sel.iterrows():
    item=row['parsed_cleaned']
    texts.append(item)    

dictionary = corpora.Dictionary(texts)
corpus = [dictionary.doc2bow(text) for text in texts]

    # Do LDA

num_topics = 10
eta_p = 0.1
rnd_state = 5
print(f"# Model parameter: Number of topics = {num_topics}, eta = {eta_p}, random state = {rnd_state}\n")
ldamodel = models.ldamodel.LdaModel(corpus, num_topics, id2word = dictionary, passes=20,eta=eta_p ,random_state=rnd_state)

    # Inpect the topics
x=ldamodel.show_topics(num_topics, num_words=10,formatted=False)
topics_words = [(tp[0], [wd[0] for wd in tp[1]]) for tp in x]

print("# These are the topic distributions for the estimated model:\n")
for topic,words in topics_words:
    print(str(topic)+ "::"+ str(words))


# =============================================================================
# ldamodel1 = models.ldamodel.LdaModel(corpus, num_topics, id2word = dictionary, passes=20,eta=0.01)
# 
#     # Inpect the topics
# x=ldamodel1.show_topics(num_topics, num_words=10,formatted=False)
# topics_words = [(tp[0], [wd[0] for wd in tp[1]]) for tp in x]
# for topic,words in topics_words:
#     print(str(topic)+ "::"+ str(words))
# 
# =============================================================================

###############################################################################

data=pd.concat([data_speakers,data_alternatives],axis=0, join='inner')
data = data.reset_index()
data_light = data[['d_alt','date', 'speaker', 'speaker_id', 'votingmember', 'ambdiss','tighterdiss', 'easierdiss']]

    # Do simple preprocessing
data['parsed']=data['content'].apply(extract_token)

    # Revome stopwords and do stemming
data['parsed_cleaned']=data['parsed'].apply(lambda x: remove_stopwords(do_stemming(remove_stopwords(x,stopwordsnltk)),add_list))

    # Build corpus
texts=[]
for row_index,row in data.iterrows():
    item=row['parsed_cleaned']
    texts.append(item)    

corpus = [dictionary.doc2bow(text) for text in texts]

    # Extract topic vectors
sent_topics_df = extract_vectors(ldamodel,num_topics,corpus)
data_lda =  pd.concat([data,sent_topics_df],axis=1, join='inner')

    # Apply SVD for dimensionality reduction
print("\n### DIMENSIONALITY REDUCTION FOR VISUAL OUTPUT ###\n")
col_topics = [ col for col in data_lda.columns if re.match("^topic",col)]
dfvalues=data_lda[col_topics].values
twodim = reduce_to_k_dim(dfvalues)
df_pca=pd.DataFrame(twodim)
df_pca.rename(columns={0:'PCI1',1:'PCI2'},inplace=True)
data_lda_pca = pd.concat([data_lda,df_pca],axis=1, join='inner')


### Compute the preferred alternative for each speaker and contrast it with the voting outcome

    # Individual date for all speakers
date = '1990-10-02'
print(F"\n### CONFUSION MATRIX FOR {date} - HELLINGER DISTANCE ###\n")
pref_distance = create_distance(date,data_lda_pca)

col_alts = [ col for col in pref_distance.columns if re.match("^alt",col)]
pref_distance["pred_vote"] = pref_distance[col_alts].idxmin(axis=1)
pref_distance = pref_distance.merge(data_lda_pca[['date','speaker','act_vote']],on=['speaker','date'])
confusion_matrix = pd.crosstab(pref_distance["act_vote"], pref_distance["pred_vote"], rownames=['Actual'], colnames=['Predicted'])
print (confusion_matrix)

    # All dates and all speakers 
print("\n### CONFUSION MATRIX ALL DATA - HELLINGER DISTANCE ###\n")
pref_distance = pd.DataFrame()
for date in data_lda_pca['date'].unique():
    help_df = create_distance(date,data_lda_pca)
    pref_distance = pd.concat([pref_distance,help_df])    

pref_distance["pred_vote"] = pref_distance[col_alts].idxmin(axis=1)
pref_distance = pref_distance.merge(data_lda_pca[['date','speaker','act_vote']],on=['speaker','date'])
confusion_matrix = pd.crosstab(pref_distance["act_vote"], pref_distance["pred_vote"], rownames=['Actual'], colnames=['Predicted'])
print (confusion_matrix)


    # Show a few examples
print("\n### VISUAL OUTPUT ###\n")

for date in ['1990-10-02','2006-08-08','1993-05-18','2007-05-09','2000-11-15']:
    #date='1991-10-01'
    dataexample = data_lda_pca[(data_lda_pca['d_alt']==1) | (data_lda_pca['votingmember']==1)][data_lda_pca['date']==date]
    #print(dataexample[["speaker"]+col_topics+['PCI1','PCI2']])
    output_plot(date,dataexample)
    
pd.set_option('display.max_rows', 20)
pd.set_option('display.max_columns', 20)
data_lda_pca.sort_values(by="date",inplace=True)
    
    # Greenspan
print("\n### GREENSPAN - HELLINGER DISTANCE ###\n")
pref_distance = pd.DataFrame()
for date in data_lda_pca['date'].unique():
    help_df = create_distance(date,data_lda_pca[(data_lda_pca['speaker']=="greenspan") | (data_lda_pca['d_alt']==1)])
    pref_distance = pd.concat([pref_distance,help_df])   
    
pref_distance["newdate"]=pd.to_datetime(pref_distance['date'])
    
plt.rcParams["figure.figsize"] = [15, 8]
pref_distance.plot(x='newdate', y=['alta','altb','altc'], style=".",title="Hellinger distance Greenspan")
plt.savefig('../output/distance_greenspan.pdf')



# =============================================================================
#     # Show the outcome for a specific speaker
# speaker ='greenspan'
# dataexample = data_lda_pca[data_lda_pca['speaker']=='alta']
# dataexamplealt = data_lda_pca[data_lda_pca['speaker']=='alta']
# 
# 
# data[(data['date']=='2007-09-18') & (data['speaker']=='alta') ]['parsed_cleaned'].tolist()
# data[(data['date']=='2008-03-18') & (data['speaker']=='alta') ]['parsed_cleaned'].tolist()
# data[(data['date']=='2004-05-04') & (data['speaker']=='alta') ]['parsed_cleaned'].tolist()
# data[(data['date']=='1998-12-22') & (data['speaker']=='alta') ]['parsed_cleaned'].tolist()
# 
# plt.figure()
# for i, row in dataexample.iterrows():
#     plt.scatter(row['PCI1'],row['PCI2'], edgecolors='k', c='b')
#     plt.text(row['PCI1'],row['PCI2'], row["date"])
# for i, row in dataexamplealt.iterrows():
#     plt.scatter(row['PCI1'],row['PCI2'], edgecolors='k', c='r')
#     plt.text(row['PCI1'],row['PCI2'], row["date"])
# 
# plt.title( f'History {speaker}')
# plt.savefig(f'../output/fig_history_{speaker}')
# 
# =============================================================================
# =============================================================================
#     # Do a manual check
# pd.set_option('display.max_columns', 500)
# data_lda_pca[data_lda_pca['date']=='1993-05-18'][['speaker']+col_topics]
# newlist=data_lda_pca[(data_lda_pca['date']=='1993-05-18') & (data_lda_pca['d_alt']==1)]['parsed_cleaned'].tolist()[1]
#         
# corpus = [dictionary.doc2bow(newlist)]  
# sent_topics_df = extract_vectors(ldamodel,num_topics,corpus)
# 
# =============================================================================