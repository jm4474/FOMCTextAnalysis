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

meetphrase_itera = 2 # Number o fphrase iterations
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

print(f"Evaluate model: {model_ckpt}")
etm(f"{TSDATA}",data_path=f"{DATAPATH}/data/{TSDATA}",
    emb_path=f"{DATAPATH}/embeddings/{EMBDATASET}_emb",save_path=f"{DATAPATH}/results",
        mode = 'eval', load_from = f"{ts_ckpt}", train_embeddings = 0 ,num_topics = 10,tc = 1, td = 1)

print(f"Output the topic distribution: {ts_ckpt}")
etm(f"{TSDATA}",data_path=f"{DATAPATH}/data/{TSDATA}",
    emb_path=f"{DATAPATH}/embeddings/{EMBDATASET}_emb",save_path=f"{DATAPATH}/results",
        mode = 'retrieve',load_from = f"{ts_ckpt}", train_embeddings = 0,num_topics = 10)


# =============================================================================
# ## #5 OUTPUT DAA

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
full_data["start_date"] = pd.to_datetime(full_data["start_date"])
full_data.to_stata(f"{DATAPATH}/full_results/{MEEETDATA}.dta",convert_dates={"start_date":"td"})




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
