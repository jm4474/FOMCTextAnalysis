#!/usr/bin/env python
# coding: utf-8

# ## Model Training and Evaluation
# Author: Oliver Giesecke

# In[ ]:


# Load modules
import os, shutil
import re
import csv
from utils import bigrams, trigram, replace_collocation
from tika import parser
import timeit
import pandas as pd
import string
from nltk.stem import PorterStemmer
import numpy as np
import pickle
import random
from scipy import sparse
import itertools
from scipy.io import savemat, loadmat
import string
from sklearn.feature_extraction.text import CountVectorizer
from gensim.test.utils import datapath
from gensim.models.word2vec import Text8Corpus
from gensim.models.phrases import Phrases
from gensim.models.phrases import ENGLISH_CONNECTOR_WORDS
from gensim.models import Word2Vec
from data_concatenate import *
import gensim.downloader
import pprint
from manetm import etm
pp = pprint.PrettyPrinter()
DATAPATH = os.path.expanduser("~/Dropbox/MPCounterfactual/src/etm/")        
OVERLEAF = os.path.expanduser("~/Dropbox/Apps/Overleaf/FOMC_Summer2019/files")

if not os.path.exists(f"{DATAPATH}/full_results"):
        os.makedirs(f"{DATAPATH}/full_results")

# =============================================================================
# ## #1 Data Preparation
print("Build datasets")

embphrase_itera = 2 # Number o fphrase iterations
embthreshold = "inf" # Threshold value for collocations. If "inf": no collocations
emb_max_df = 1.0 # in a maximum of # % of documents if # is float.
emb_min_df = 1  # choose desired value for min_df // in a minimum of # documents
EMBDATASET = f"BBTSST_min{emb_min_df}_max{emb_max_df}_iter{embphrase_itera}_th{embthreshold}"
build_embdata(emb_max_df,emb_min_df,embphrase_itera,embthreshold,EMBDATASET)

speakerphrase_itera = 2 # Number o fphrase iterations
speakerthreshold = "inf" # Threshold value for collocations. If "inf": no collocations
speakermax_df = 0.7 
speakermin_df = 10
SPEAKERDATA = f"SPEAKERS_min{speakermin_df}_max{speakermax_df}_iter{speakerphrase_itera}_th{speakerthreshold}"
build_speakerdata(speakermax_df,speakermin_df,speakerphrase_itera,speakerthreshold,SPEAKERDATA)

meetphrase_itera = 2 # Number of phrase iterations
meetthreshold = "inf" # Threshold value for collocations. If "inf": no collocations
meetmax_df=1.0
meetmin_df=10
MEEETDATA = f"MEET_min{meetmin_df}_max{meetmax_df}_iter{meetphrase_itera}_th{meetthreshold}"
build_meeting(meetmax_df,meetmin_df,meetphrase_itera,meetthreshold,MEEETDATA)

ts_phrase_itera = 2 # Number o fphrase iterations
ts_threshold = "inf" # Threshold value for collocations. If "inf": no collocations
ts_max_df=1.0
ts_min_df=10
TSDATA = f"TS_min{meetmin_df}_max{meetmax_df}_iter{meetphrase_itera}_th{meetthreshold}"
build_transcriptdata(ts_max_df,ts_min_df,ts_phrase_itera,ts_threshold,TSDATA)

print("*" * 80)
print("Datasets Construction Completed")
print("*" * 80)
print("\n\n")

# =============================================================================
# ## #2 Train Word Embeddings
# Select corpus

# Run Skipgram
print(f"Run model: {EMBDATASET}")
os.system(f"python skipgram_man.py --data_file {DATAPATH}/data/{EMBDATASET}/corpus.pkl --modelfile {DATAPATH}/word2vecmodels/{EMBDATASET} --emb_file {DATAPATH}/embeddings/{EMBDATASET}_emb --dim_rho 300 --iters 100 --window_size 4")
print("*" * 80)
print(f"Embedding Training Completed")
print("*" * 80)
print("\n\n")


# =============================================================================
# ## #3  Get Pre-Trained Word Embeddings

sel_mod = "glove-wiki-gigaword-300"
glove_vectors = gensim.downloader.load(sel_mod)

with open(f'{DATAPATH}/data/{SPEAKERDATA}/vocab.pkl', 'rb') as f:
     vocab = pickle.load(f)

# Write the embeddings to a file
with open(f"{DATAPATH}/embeddings/{EMBDATASET}_pre", 'w') as f:
    for v in glove_vectors.index_to_key:
        if v in vocab:
            vec = list(glove_vectors[v])
            f.write(v + ' ')
            vec_str = ['%.9f' % val for val in vec]
            vec_str = " ".join(vec_str)
            f.write(vec_str + '\n')

with open(f'{DATAPATH}/data/{MEEETDATA}/vocab.pkl', 'rb') as f:
     vocab = pickle.load(f)

# Write the embeddings to a file
with open(f"{DATAPATH}/embeddings/{MEEETDATA}_pre", 'w') as f:
    for v in glove_vectors.index_to_key:
        if v in vocab:
            vec = list(glove_vectors[v])
            f.write(v + ' ')
            vec_str = ['%.9f' % val for val in vec]
            vec_str = " ".join(vec_str)
            f.write(vec_str + '\n')
print("*" * 80)
print(f"Embeddings Extracted")
print("*" * 80)
print("\n\n")


# =============================================================================
# ## #4 TRAIN TOPIC MODELS

## SPEAKERDATA - Pre-Trained Emb.

speaker_ckpt = etm(f"{SPEAKERDATA}",data_path=f"{DATAPATH}/data/{SPEAKERDATA}",
        emb_path=f"{DATAPATH}/embeddings/{EMBDATASET}_emb",save_path=f"{DATAPATH}/results",
        batch_size = 1000, epochs = 150, num_topics = 10, rho_size = 300,
        emb_size = 300, t_hidden_size = 800, theta_act = 'relu',
        train_embeddings = 0,  lr = 0.005,  lr_factor=4.0,
        mode = 'train', optimizer = 'adam',
        seed = 2019, enc_drop = 0.0, clip = 0.0,
        nonmono = 10, wdecay = 1.2e-6, anneal_lr = 0, bow_norm = 1,
        num_words =10, log_interval = 2, visualize_every = 10, eval_batch_size = 1000,
        load_from = "", tc = 1, td = 1)

print(f"Evaluate model: {speaker_ckpt}")
etm(f"{SPEAKERDATA}",data_path=f"{DATAPATH}/data/{SPEAKERDATA}",
    emb_path=f"{DATAPATH}/embeddings/{EMBDATASET}_emb",save_path=f"{DATAPATH}/results",
        mode = 'eval', load_from = f"{speaker_ckpt}", train_embeddings = 0 ,tc = 1, td = 1)

print(f"Output the topic distribution: {speaker_ckpt}")
etm(f"{SPEAKERDATA}",data_path=f"{DATAPATH}/data/{SPEAKERDATA}",
    emb_path=f"{DATAPATH}/embeddings/{EMBDATASET}_emb",save_path=f"{DATAPATH}/results",
        mode = 'retrieve',load_from = f"{speaker_ckpt}", train_embeddings = 0)


## MEETINGS - Pre-Trained Emb.

meeting_ckpt = etm(f"{MEEETDATA}",data_path=f"{DATAPATH}/data/{MEEETDATA}",
        emb_path=f"{DATAPATH}/embeddings/{EMBDATASET}_emb",save_path=f"{DATAPATH}/results",
        batch_size = 1000, epochs = 1000, num_topics = 10, rho_size = 300,
        emb_size = 300, t_hidden_size = 800, theta_act = 'relu',
        train_embeddings = 0,  lr = 0.005,  lr_factor=4.0,
        mode = 'train', optimizer = 'adam',
        seed = 2019, enc_drop = 0.0, clip = 0.0,
        nonmono = 10, wdecay = 1.2e-6, anneal_lr = 0, bow_norm = 1,
        num_words =10, log_interval = 2, visualize_every = 10, eval_batch_size = 1000,
        load_from = "", tc = 1, td = 1)

print(f"Evaluate model: {meeting_ckpt}")
etm(f"{MEEETDATA}",data_path=f"{DATAPATH}/data/{MEEETDATA}",
    emb_path=f"{DATAPATH}/embeddings/{EMBDATASET}_emb",save_path=f"{DATAPATH}/results",
        mode = 'eval', load_from = f"{meeting_ckpt}", train_embeddings = 0 ,tc = 1, td = 1)

print(f"Output the topic distribution: {meeting_ckpt}")
etm(f"{MEEETDATA}",data_path=f"{DATAPATH}/data/{MEEETDATA}",
    emb_path=f"{DATAPATH}/embeddings/{EMBDATASET}_emb",save_path=f"{DATAPATH}/results",
        mode = 'retrieve',load_from = f"{meeting_ckpt}", train_embeddings = 0)

## MEETINGS - Pre-Trained Emb. - Sample 

MEETDATASAMPLE = f"{MEEETDATA}sampled"
nr_topics = 10
meeting_ckptsampled = etm(f"{MEETDATASAMPLE}",data_path=f"{DATAPATH}/data/{MEETDATASAMPLE}",
        emb_path=f"{DATAPATH}/embeddings/{EMBDATASET}_emb",save_path=f"{DATAPATH}/results",
        batch_size = 1000, epochs = 1000, num_topics = nr_topics, rho_size = 300,
        emb_size = 300, t_hidden_size = 800, theta_act = 'relu',
        train_embeddings = 0,  lr = 0.005,  lr_factor=4.0,
        mode = 'train', optimizer = 'adam',
        seed = 2019, enc_drop = 0.0, clip = 0.0,
        nonmono = 10, wdecay = 1.2e-6, anneal_lr = 0, bow_norm = 1,
        num_words = 15, log_interval = 2, visualize_every = 100, eval_batch_size = 1000,
        load_from = "", tc = 1, td = 1)

print(f"Evaluate model: {meeting_ckptsampled}")
etm(f"{MEETDATASAMPLE}",data_path=f"{DATAPATH}/data/{MEETDATASAMPLE}",
    emb_path=f"{DATAPATH}/embeddings/{EMBDATASET}_emb",save_path=f"{DATAPATH}/results",
        mode = 'eval', load_from = f"{meeting_ckptsampled}", train_embeddings = 0 ,tc = 1, td = 1,num_topics = nr_topics)

print(f"Output the topic distribution: {meeting_ckptsampled}")
etm(f"{MEETDATASAMPLE}",data_path=f"{DATAPATH}/data/{MEETDATASAMPLE}",
    emb_path=f"{DATAPATH}/embeddings/{EMBDATASET}_emb",save_path=f"{DATAPATH}/results",
        mode = 'retrieve',load_from = f"{meeting_ckptsampled}", train_embeddings = 0,num_topics = nr_topics)


## TRANSCRIPTS - Pre-Trained Emb.

ts_ckpt = etm(f"{TSDATA}",data_path=f"{DATAPATH}/data/{TSDATA}",
        emb_path=f"{DATAPATH}/embeddings/{EMBDATASET}_emb",save_path=f"{DATAPATH}/results",
        batch_size = 1000, epochs = 1000, num_topics = 10, rho_size = 300,
        emb_size = 300, t_hidden_size = 800, theta_act = 'relu',
        train_embeddings = 0,  lr = 0.005,  lr_factor=4.0,
        mode = 'train', optimizer = 'adam',
        seed = 2019, enc_drop = 0.0, clip = 0.0,
        nonmono = 10, wdecay = 1.2e-6, anneal_lr = 0, bow_norm = 1,
        num_words =10, log_interval = 2, visualize_every = 10, eval_batch_size = 1000,
        load_from = "", tc = 1, td = 1)

print(f"Evaluate model: {ts_ckpt}")
etm(f"{TSDATA}",data_path=f"{DATAPATH}/data/{TSDATA}",
    emb_path=f"{DATAPATH}/embeddings/{EMBDATASET}_emb",save_path=f"{DATAPATH}/results",
        mode = 'eval', load_from = f"{ts_ckpt}", train_embeddings = 0 ,num_topics = 10,tc = 1, td = 1)

print(f"Output the topic distribution: {ts_ckpt}")
etm(f"{TSDATA}",data_path=f"{DATAPATH}/data/{TSDATA}",
    emb_path=f"{DATAPATH}/embeddings/{EMBDATASET}_emb",save_path=f"{DATAPATH}/results",
        mode = 'retrieve',load_from = f"{ts_ckpt}", train_embeddings = 0,num_topics = 10)


# =============================================================================
# ## #5 OUTPUT DATA

## SPEAKERDATA

raw_df  = pd.read_pickle(f"raw_data/{SPEAKERDATA}.pkl")

idx_df = pd.read_pickle(f'{OUTPATH}/{SPEAKERDATA}/original_indices.pkl')
idx_df = idx_df.set_index(0)
idx_df["d"] = 1

data = pd.concat([idx_df,raw_df],axis=1)
data_clean = data[data["d"]==1].reset_index()
dist_df = pd.read_pickle(f'{speaker_ckpt}tpdist.pkl')

full_data = pd.concat([data_clean,dist_df],axis=1)
full_data.drop(columns=["content","d"],inplace=True)
full_data.rename(columns=dict(zip([i for i in range(10)],[f"topic_{i}" for i in range(10)])),inplace=True)
full_data["start_date"] = pd.to_datetime(full_data["start_date"])
full_data.to_stata(f"{DATAPATH}/full_results/{SPEAKERDATA}.dta",convert_dates={"start_date":"td"})


### MEETING ###

# Retrieve raw data
raw_df  = pd.read_pickle(f"raw_data/{MEEETDATA}.pkl")

idx_df = pd.read_pickle(f'{OUTPATH}/{MEEETDATA}/original_indices.pkl')
idx_df = idx_df.set_index(0)
idx_df["d"] = 1

data = pd.concat([idx_df,raw_df],axis=1)
data_clean = data[data["d"]==1].reset_index()
dist_df = pd.read_pickle(f'{meeting_ckpt}tpdist.pkl')

full_data = pd.concat([data_clean,dist_df],axis=1)
full_data.drop(columns=["content"],inplace=True)
full_data.rename(columns=dict(zip([i for i in range(10)],[f"topic_{i}" for i in range(10)])),inplace=True)
full_data["date"] = full_data["start_date"]
full_data.to_stata(f"{DATAPATH}/full_results/{MEEETDATA}.dta",convert_dates={"date":"td"})
full_data.to_pickle(f"{DATAPATH}/full_results/{MEEETDATA}.pkl")

### MEETING SAMPLED ###

# Retrieve raw data
raw_df  = pd.read_pickle(f"raw_data/{MEETDATASAMPLE}.pkl")
idx_df = pd.read_pickle(f'{OUTPATH}/{MEETDATASAMPLE}/original_indices.pkl')
idx_df = idx_df.set_index(0)
idx_df["d"] = 1

data = pd.concat([idx_df,raw_df],axis=1)
data_clean = data[data["d"]==1].reset_index()
dist_df = pd.read_pickle(f'{meeting_ckptsampled}tpdist.pkl')

full_data = pd.concat([data_clean,dist_df],axis=1)
full_data.drop(columns=["content"],inplace=True)
full_data.rename(columns=dict(zip([i for i in range(10)],[f"topic_{i}" for i in range(10)])),inplace=True)
full_data["date"] = pd.to_datetime(full_data["date"])
full_data.to_stata(f"{DATAPATH}/full_results/{MEETDATASAMPLE}.dta",convert_dates={"date":"td"})
full_data.to_pickle(f"{DATAPATH}/full_results/{MEETDATASAMPLE}.pkl")

# =============================================================================
# ## 6 Visualize

import matplotlib.pyplot as plt
import matplotlib.ticker as tkr

meetphrase_itera = 2 # Number of phrase iterations
meetthreshold = "inf" # Threshold value for collocations. If "inf": no collocations
meetmax_df=1.0
meetmin_df=10
MEEETDATA = f"MEET_min{meetmin_df}_max{meetmax_df}_iter{meetphrase_itera}_th{meetthreshold}"

# Load data
full_data = pd.read_pickle(f"{DATAPATH}/full_results/{MEEETDATA}.pkl")
full_data.rename(columns=dict(zip([f"topic_{k}" for k in range(10)],[f"topic_{k+1}" for k in range(10)] )),inplace=True)
meeting_ckpt = f"{DATAPATH}/results/etm_MEET_min10_max1.0_iter2_thinf_K_10_Htheta_800_Optim_adam_Clip_0.0_ThetaAct_relu_Lr_0.005_Bsz_1000_RhoSize_300_trainEmbeddings_0"

# Retrieve topics
with open(f'{meeting_ckpt}topics.pkl', 'rb') as f:
    meet_topics = pickle.load(f)
    top_dic = dict(zip([item[0] for item in meet_topics ],[", ".join(item[1]) for item in meet_topics ] ))
# Check topics
for item in meet_topics:
    print(f'{item[0]+1}: {", ".join(item[1])}')


section1 = full_data[full_data["Section"]==1].copy()
section2 = full_data[full_data["Section"]==2].copy()

k = 0

for k in range(1,11):
    fig = plt.figure(figsize=(20,9))
    axs = fig.add_subplot(1,1,1)
    plt.subplots_adjust(.1,.20,1,.95)
    section1.plot.scatter('start_date',f'topic_{k}',color="dodgerblue",ax=axs,label="Section 1")
    section2.plot.scatter('start_date',f'topic_{k}',color="red",ax=axs,label="Section 2")
    plt.figtext(0.10, 0.05, f"Topic {k} words: {top_dic[k-1]}", ha="left", fontsize=20)
    axs.set_xlabel("Meeting Day",fontsize=20)
    axs.set_ylabel(f"Topic {k}",fontsize=20)
    axs.yaxis.set_major_formatter(tkr.FuncFormatter(lambda x, p: f"{x:.2f}"))
    axs.grid(linestyle=':')
    axs.tick_params(which='both',labelsize=20,axis="y")
    axs.tick_params(which='both',labelsize=20,axis="x")
    axs.legend( prop={'size': 20})
    plt.savefig(f'output/transcript_topic_{k}.pdf')
    try:
        #plt.savefig(f'{OVERLEAF}/files/transcript_topic_{k}.eps', format='eps')
        plt.savefig(f'{OVERLEAF}/transcript_topic_{k}.pdf')
    except:
        print("Invalid Overleaf Path")
        
# Meetings Sampled

# Retrieve topics
full_data = pd.read_pickle(f"{DATAPATH}/full_results/{MEETDATASAMPLE}.pkl")
full_data.rename(columns=dict(zip([f"topic_{k}" for k in range(12)],[f"topic_{k+1}" for k in range(12)] )),inplace=True)

with open(f'{meeting_ckptsampled}topics.pkl', 'rb') as f:
    meet_topics = pickle.load(f)
    top_dic = dict(zip([item[0] + 1 for item in meet_topics ],[", ".join(item[1]) for item in meet_topics ] ))
# Check topics
for item in top_dic.keys():
    print(f'{item}: {top_dic[item]}')

section1 = full_data[full_data["Section"]==1].copy()
section2 = full_data[full_data["Section"]==2].copy()

k = 0

for k in range(1,11):
    fig = plt.figure(figsize=(20,9))
    axs = fig.add_subplot(1,1,1)
    plt.subplots_adjust(.1,.20,1,.95)
    section1.plot.scatter('date',f'topic_{k}',color="dodgerblue",ax=axs,label="Section 1")
    section2.plot.scatter('date',f'topic_{k}',color="red",ax=axs,label="Section 2")
    plt.figtext(0.10, 0.05, f"Topic {k} words: {top_dic[k]}", ha="left", fontsize=20)
    axs.set_xlabel("Meeting Day",fontsize=20)
    axs.set_ylabel(f"Topic {k}",fontsize=20)
    axs.yaxis.set_major_formatter(tkr.FuncFormatter(lambda x, p: f"{x:.2f}"))
    axs.grid(linestyle=':')
    axs.tick_params(which='both',labelsize=20,axis="y")
    axs.tick_params(which='both',labelsize=20,axis="x")
    axs.legend( prop={'size': 20})
    plt.savefig(f'output/transcriptsampled_topic_{k}.pdf')
    try:
        #plt.savefig(f'{OVERLEAF}/files/transcript_topic_{k}.eps', format='eps')
        plt.savefig(f'{OVERLEAF}/transcriptsampled_topic_{k}.pdf')
    except:
        print("Invalid Overleaf Path")

# =============================================================================
# ## 7 MN Logit
import statsmodels.api as sm
import pandas as pd
import numpy as np

DATAPATH = os.path.expanduser("~/Dropbox/MPCounterfactual/src/etm/")        
OVERLEAF = os.path.expanduser("~/Dropbox/Apps/Overleaf/FOMC_Summer2019/files")
topics = pd.read_stata("full_results/MEET_min10_max1.0_iter2_thinf.dta") 
topics.rename(columns=dict(zip([f"topic_{k}" for k in range(10)],[f"topic_{k+1}" for k in range(10)] )),inplace=True)
topics.drop(columns=["level_0","index", "d"],inplace=True)
topics = topics[topics["start_date"]!="2009-09-16"]

econdata = pd.read_pickle("../economic_data/final_data/econmarketdata.pkl")
data = topics.merge(econdata,left_on="start_date",right_on="date",how="inner")
data.rename(columns={"m_cape":"EQUITYCAPE"},inplace=True)

for k in range(1,11):
    data[f"lns{k}s5"] = np.log(data[f"topic_{k}"]) - np.log(data[f"topic_5"])

for k in range(1,11):
    data[f"s{k}s5"] = data[f"topic_{k}"]  / data[f"topic_5"]


data["constant"] = 1

covs = "l1d_UNRATE l2d_UNRATE l1dln_PCEPI l2dln_PCEPI l1dln_INDPRO l2dln_INDPRO d14ln_spindx d28_SVENY01 d28_SVENY10 TEDRATE SVENY01 SVENY10 BAA10Y AAA10Y"
covs_list = covs.split(" ")



est_section1 = data.loc[data["Section"] == 1,[f"s{k}s5" for k in range(1,11) ]]
res_df = pd.DataFrame([])
for k in [1,2,3,4,6,7,8,9,10]:
    print(f"\n ************** Topic: {k} ***********************\n")
    model = sm.OLS(data.loc[data["Section"] == 1,f"lns{k}s5"], data.loc[data["Section"] == 1,["constant"]+covs_list])
    results = model.fit()
    print(results.summary())

    ef_dict = []
    for var in covs_list:
        est_section1[f"mr_{var}"] = est_section1[f"s{k}s5"]  * results.params[var]
        ef_dict.append(est_section1[f"mr_{var}"].mean())
    aux_df = pd.DataFrame(data=ef_dict,columns=[f"AMX T{k}"],index=list(results.params.keys())[1:])       
    res_df = pd.concat([res_df,aux_df],axis=1)
    
labels = {"l1d_UNRATE":"Lag 1 dURate","l2d_UNRATE": "Lag 2 dURate","l1dln_PCEPI": "Lag 1 dlnPCEPI",
          "l2dln_PCEPI": "Lag 2 dlnPCEPI","l1dln_INDPRO":"Lag 1 dlnIP","l2dln_INDPRO": "Lag 2 dlnIP",
          "d7ln_spindx": "7 day Return S\&P500","d14ln_spindx":"14 day Return S\&P500",
          "EQUITYCAPE": "Equity Cape","TEDRATE": "Ted Spread","SVENY01": "Tr. 1yr Yield",
          "d28_SVENY01": "$\Delta$ Tr. 1yr Yield","d28_SVENY10": "$\Delta$ Tr. 10yr Yield",
          "SVENY10": "Tr. 10yr Yield", "BAA10Y": "BAA Credit Spread","AAA10Y": "AAA Credit Spread"}
res_df = res_df.reset_index().replace({"index":labels}).set_index("index")

print(res_df.to_latex(escape=False))
res_df.to_latex(f"{OVERLEAF}/section1_avgmr.tex",escape=False,float_format="{:0.3f}".format )




est_section1 = data.loc[data["Section"] == 2,[f"s{k}s5" for k in range(1,11) ]]
res_df = pd.DataFrame([])
for k in [1,2,3,4,6,7,8,9,10]:
    print(f"\n ************** Topic: {k} ***********************\n")
    model = sm.OLS(data.loc[data["Section"] == 2,f"lns{k}s5"], data.loc[data["Section"] == 2,["constant"]+covs_list])
    results = model.fit()
    print(results.summary())

    ef_dict = []
    for var in covs_list:
        est_section1[f"mr_{var}"] = est_section1[f"s{k}s5"]  * results.params[var]
        ef_dict.append(est_section1[f"mr_{var}"].mean())
    aux_df = pd.DataFrame(data=ef_dict,columns=[f"AMX T{k}"],index=list(results.params.keys())[1:])       
    res_df = pd.concat([res_df,aux_df],axis=1)
    
labels = {"l1d_UNRATE":"Lag 1 dURate","l2d_UNRATE": "Lag 2 dURate","l1dln_PCEPI": "Lag 1 dlnPCEPI",
          "l2dln_PCEPI": "Lag 2 dlnPCEPI","l1dln_INDPRO":"Lag 1 dlnIP","l2dln_INDPRO": "Lag 2 dlnIP",
          "d7ln_spindx": "7 day Return S\&P500","d14ln_spindx":"14 day Return S\&P500",
          "EQUITYCAPE": "Equity Cape","TEDRATE": "Ted Spread","SVENY01": "Tr. 1yr Yield",
          "d28_SVENY01": "$\Delta$ Tr. 1yr Yield","d28_SVENY10": "$\Delta$ Tr. 10yr Yield",
          "SVENY10": "Tr. 10yr Yield", "BAA10Y": "BAA Credit Spread","AAA10Y": "AAA Credit Spread"}
res_df = res_df.reset_index().replace({"index":labels}).set_index("index")

print(res_df.to_latex(escape=False))
res_df.to_latex(f"{OVERLEAF}/section2_avgmr.tex",escape=False,float_format="{:0.3f}".format )

# 
# =============================================================================




# =============================================================================
# 
# # Glove pre-trained embeddings
# os.system(f'python main.py --mode train --dataset fomc_impemb --data_path {DATAPATH}/data/SPEAKERS_10_iter2_thinf --emb_path {DATAPATH}/embeddings/preSPEAKERS_10_iter2_thinf --num_topics 10 --train_embeddings 0 --epochs 100')
# model = "etm_fomc_impemb_K_10_Htheta_800_Optim_adam_Clip_0.0_ThetaAct_relu_Lr_0.005_Bsz_1000_RhoSize_300_trainEmbeddings_0"
# print(f"Evaluate model: {model}")
# os.system(f'python main.py --mode eval --dataset fomc_impemb --data_path {DATAPATH}/data/SPEAKERS_10_iter2_thinf --num_topics 10 --emb_path {DATAPATH}/embeddings/preSPEAKERS_10_iter2_thinf --train_embeddings 0 --tc 1 --td 1 --load_from {DATAPATH}/results/{model}')
# 
# # Pre-trained embeddings -- meetings
# os.system(f'python main.py --mode train --dataset meeting_pre --data_path {DATAPATH}/data/MEETING_1_iter2_thinf --emb_path {DATAPATH}/embeddings/preMEETING_1_iter2_thinf  --num_topics 10 --train_embeddings 0 --epochs 100')
# model = "etm_meeting_pre_K_10_Htheta_800_Optim_adam_Clip_0.0_ThetaAct_relu_Lr_0.005_Bsz_1000_RhoSize_300_trainEmbeddings_0"
# print(f"Evaluate model: {model}")
# os.system(f'python main.py --mode eval --dataset meeting_pre --data_path {DATAPATH}/data/MEETING_1_iter2_thinf --num_topics 10 --emb_path {DATAPATH}/embeddings/preMEETING_1_iter2_thinf --train_embeddings 0 --tc 1 --td 1 --load_from {DATAPATH}/results/{model}')
# 
# =============================================================================

# =============================================================================
# ## # DO MODEL EVALUATION OF EMBEDDINGS
# # Load models
# models = []
# for mod in man_models:
#     models.append(gensim.models.Word2Vec.load(f"{DATAPATH}/word2vecmodels/{mod}.model").wv)
# 
# # All models
# model_title = man_models + [sel_mod]
# models = models + [glove_vectors]
# print("Use following models:")
# pp.pprint(model_title)
# 
# pp = pprint.PrettyPrinter(width=80, compact=True)
# keywords = ['inflation','employment','interest','price','growth','output']
# for idx,model in enumerate(models):
#     print("*"*80)
#     print(f"{model_title[idx]} Word Vectors")
#     print("*"*80)
#     for key in keywords:
#         msw = [v[0] for v in model.most_similar(key)]
#         print(f"{key}:")
#         pp.pprint(msw)
#     print("\n")
#
# # Latex Export of results
# for idx,model in enumerate(models):
#     fulldata =pd.DataFrame([])
#     for key in keywords:
#         msw = [v[0] for v in model.most_similar(key)]
#         data = pd.DataFrame(msw,columns=[key])
#         fulldata = pd.concat([data,fulldata],axis=1)
#          
#     #print(fulldata.to_latex())
#     fulldata.to_latex(f"{OVERLEAF}/emb_{model_title[idx]}.tex")
# 
# =============================================================================

# =============================================================================
#     
# # Joint training of embeddings
# os.system(f'python main.py --mode train --dataset fomc_joint --data_path {DATAPATH}/data/SPEAKERS_10_iter2_th80 --num_topics 10 --train_embeddings 1 --epochs 100')
# model = "etm_fomc_joint_K_10_Htheta_800_Optim_adam_Clip_0.0_ThetaAct_relu_Lr_0.005_Bsz_1000_RhoSize_300_trainEmbeddings_1"
# print(f"Evaluate model: {model}")
# os.system(f'python main.py --mode eval --dataset fomc_joint --data_path {DATAPATH}/data/SPEAKERS_10_iter2_th80 --num_topics 10 --train_embeddings 1 --tc 1 --td 1 --load_from {DATAPATH}/results/{model}')
# # Joint training of embeddings
# =============================================================================
