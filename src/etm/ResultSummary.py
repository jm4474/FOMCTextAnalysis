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
pp = pprint.PrettyPrinter()
DATAPATH = os.path.expanduser("~/Dropbox/MPCounterfactual/src/etm/")        
OVERLEAF = os.path.expanduser("~/Dropbox/Apps/Overleaf/FOMC_Summer2019/files")  


# ## #1 Data Preparation
# 
# The training of the model requires potentially two datasets:
# 1. corpus of documents for the training of word embeddings,
# 2. pre-processed speaker data from the transcripts (Greenspan era).
# 
# The former is used to train word embedding in isolation on a larger corpus than the what is used for the training of topics. Thus far this consists of transcripts (for the entire period from 1976-2013) + all bluebooks + statements, shortly denoted by ```BBTSST```. Latter is used for the training of topics and the main interest of inquiry.
# 
# Apart from the exact scope of the corpus, the data pre-processing requires to make a few important choices. In particular, it requires to specify:
# - treatment of stop words,
# - whether collocations are being formed (parameter: ```threshold```),
# - number of tokens that form collocation (parameter: ```phrase_itera```),
# - treatment very frequent and infrequent words (parameter: ```min_df``` and ```max_df```)
# 
# The data pre-processing is implemented in the module ```data_concatenate``` and can either be called or executed independently.
# 

# In[ ]:


max_df = 0.7 # in a maximum of # % of documents if # is float.
min_df = 10  # choose desired value for min_df // in a minimum of # documents
phrase_itera = 2 # Number o fphrase iterations
threshold = "inf" # Threshold value for collocations. If "inf": no collocations

print("Build datasets")
build_embdata(max_df,min_df,phrase_itera,threshold)
build_speakerdata(max_df,min_df,phrase_itera,threshold)
max_df=1.0
min_df=1
build_meeting(max_df,min_df,phrase_itera,threshold)
   
print("Datasets complete")


# ## #2 Train Word Embeddings
# 
# We follow Mikolov et. al (2013) to train word embeddings.   
# 
# Subsequently we save the model and word vectors.
# 
# 

# In[13]:


# Datasets available:
pp.pprint([file for file in os.listdir(f"{DATAPATH}/data/") if file!=".DS_Store"])


# In[14]:


# Select corpus
corpus = 'BBTSST_10_iter2_thinf'

# Run Skipgram
print(f"Run model: {corpus}")
os.system(f"python skipgram_man.py --data_file {DATAPATH}/data/{corpus}/corpus.pkl --modelfile {DATAPATH}/word2vecmodels/{corpus} --emb_file {DATAPATH}/embeddings/{corpus}_emb --dim_rho 300 --iters 50 --window_size 4")
print(f"Training completed")


# ## #2 Evaluate Word Embeddings 
# This is a visual inspection of the word vectors for different models for common domain specific terms.

# In[32]:


# Available models
pp.pprint([file for file in os.listdir(f"{DATAPATH}/word2vecmodels/") if file!=".DS_Store" and re.search("model$",file)])
# Select models
man_models = ['BBTSST_10_iter2_thinf',"BBTSST_10_iter2_th80"]


# In[ ]:


# Pre-trained model
#pp.pprint(list(gensim.downloader.info()['models'].keys()))
sel_mod = "glove-wiki-gigaword-300"
glove_vectors = gensim.downloader.load(sel_mod)

with open(f'{DATAPATH}/data/SPEAKERS_10_iter2_thinf/vocab.pkl', 'rb') as f:
     vocab = pickle.load(f)

# Write the embeddings to a file
with open(f"{DATAPATH}/embeddings/preSPEAKERS_10_iter2_thinf", 'w') as f:
    for v in glove_vectors.index_to_key:
        if v in vocab:
            vec = list(glove_vectors[v])
            f.write(v + ' ')
            vec_str = ['%.9f' % val for val in vec]
            vec_str = " ".join(vec_str)
            f.write(vec_str + '\n')

with open(f'{DATAPATH}/data/MEETING_1_iter2_thinf/vocab.pkl', 'rb') as f:
     vocab = pickle.load(f)

# Write the embeddings to a file
with open(f"{DATAPATH}/embeddings/preMEETING_1_iter2_thinf", 'w') as f:
    for v in glove_vectors.index_to_key:
        if v in vocab:
            vec = list(glove_vectors[v])
            f.write(v + ' ')
            vec_str = ['%.9f' % val for val in vec]
            vec_str = " ".join(vec_str)
            f.write(vec_str + '\n')
# In[33]:


# Load models
models = []
for mod in man_models:
    models.append(gensim.models.Word2Vec.load(f"{DATAPATH}/word2vecmodels/{mod}.model").wv)

# All models
model_title = man_models + [sel_mod]
models = models + [glove_vectors]
print("Use following models:")
pp.pprint(model_title)


# In[34]:


pp = pprint.PrettyPrinter(width=80, compact=True)
keywords = ['inflation','employment','interest','price','growth','output']
for idx,model in enumerate(models):
    print("*"*80)
    print(f"{model_title[idx]} Word Vectors")
    print("*"*80)
    for key in keywords:
        msw = [v[0] for v in model.most_similar(key)]
        print(f"{key}:")
        pp.pprint(msw)
    print("\n")


# In[36]:


# Latex Export of results
for idx,model in enumerate(models):
    fulldata =pd.DataFrame([])
    for key in keywords:
        msw = [v[0] for v in model.most_similar(key)]
        data = pd.DataFrame(msw,columns=[key])
        fulldata = pd.concat([data,fulldata],axis=1)
         
    #print(fulldata.to_latex())
    fulldata.to_latex(f"{OVERLEAF}/emb_{model_title[idx]}.tex")

# =============================================================================
# TRAIN TOPIC MODELS
    
# Joint training of embeddings
os.system(f'python main.py --mode train --dataset fomc_joint --data_path {DATAPATH}/data/SPEAKERS_10_iter2_th80 --num_topics 10 --train_embeddings 1 --epochs 100')
model = "etm_fomc_joint_K_10_Htheta_800_Optim_adam_Clip_0.0_ThetaAct_relu_Lr_0.005_Bsz_1000_RhoSize_300_trainEmbeddings_1"
print(f"Evaluate model: {model}")
os.system(f'python main.py --mode eval --dataset fomc_joint --data_path {DATAPATH}/data/SPEAKERS_10_iter2_th80 --num_topics 10 --train_embeddings 1 --tc 1 --td 1 --load_from {DATAPATH}/results/{model}')
# Joint training of embeddings

# Pre-trained embeddings
os.system(f'python main.py --mode train --dataset fomc_pre --data_path {DATAPATH}/data/SPEAKERS_10_iter2_thinf --emb_path {DATAPATH}/embeddings/BBTSST_10_iter2_thinf_emb --num_topics 10 --train_embeddings 0 --epochs 100')
model = "etm_fomc_pre_K_10_Htheta_800_Optim_adam_Clip_0.0_ThetaAct_relu_Lr_0.005_Bsz_1000_RhoSize_300_trainEmbeddings_0"
print(f"Evaluate model: {model}")
os.system(f'python main.py --mode eval --dataset fomc_pre --data_path {DATAPATH}/data/SPEAKERS_10_iter2_thinf --num_topics 10 --emb_path {DATAPATH}/embeddings/BBTSST_10_iter2_thinf_emb --train_embeddings 0 --tc 1 --td 1 --load_from {DATAPATH}/results/{model}')

# Glove pre-trained embeddings
os.system(f'python main.py --mode train --dataset fomc_impemb --data_path {DATAPATH}/data/SPEAKERS_10_iter2_thinf --emb_path {DATAPATH}/embeddings/preSPEAKERS_10_iter2_thinf --num_topics 10 --train_embeddings 0 --epochs 100')
model = "etm_fomc_impemb_K_10_Htheta_800_Optim_adam_Clip_0.0_ThetaAct_relu_Lr_0.005_Bsz_1000_RhoSize_300_trainEmbeddings_0"
print(f"Evaluate model: {model}")
os.system(f'python main.py --mode eval --dataset fomc_impemb --data_path {DATAPATH}/data/SPEAKERS_10_iter2_thinf --num_topics 10 --emb_path {DATAPATH}/embeddings/preSPEAKERS_10_iter2_thinf --train_embeddings 0 --tc 1 --td 1 --load_from {DATAPATH}/results/{model}')

# Pre-trained embeddings -- meetings
os.system(f'python main.py --mode train --dataset meeting_pre --data_path {DATAPATH}/data/MEETING_1_iter2_thinf --emb_path {DATAPATH}/embeddings/preMEETING_1_iter2_thinf  --num_topics 10 --train_embeddings 0 --epochs 100')
model = "etm_meeting_pre_K_10_Htheta_800_Optim_adam_Clip_0.0_ThetaAct_relu_Lr_0.005_Bsz_1000_RhoSize_300_trainEmbeddings_0"
print(f"Evaluate model: {model}")
os.system(f'python main.py --mode eval --dataset meeting_pre --data_path {DATAPATH}/data/MEETING_1_iter2_thinf --num_topics 10 --emb_path --emb_path {DATAPATH}/embeddings/preMEETING_1_iter2_thinf  --train_embeddings 0 --tc 1 --td 1 --load_from {DATAPATH}/results/{model}')
 