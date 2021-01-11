#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 11 13:49:50 2021

@author: olivergiesecke
"""

import os, shutil
import re
import csv
from utils import bigrams, trigram, replace_collocation
from tika import parser
import timeit
import pandas as pd
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

TRANSCRIPT_PATH = os.path.expanduser("~/Dropbox/MPCounterfactual/src/collection/python/data/transcript_raw_text")
BB_PATH = os.path.expanduser("~/Dropbox/MPCounterfactual/src/collection/python/output/bluebook_raw_text")
STATEMENT_PATH = os.path.expanduser("~/Dropbox/MPCounterfactual/src/derivation/python/output/statements_text_extraction.csv")
OUTPATH = os.path.expanduser("~/Dropbox/MPCounterfactual/src/etm/data")        
SPEAKER_PATH = os.path.expanduser("~/Dropbox/MPCounterfactual/src/analysis/python/output")        


def generate_rawtranscripts():
    raw_doc = os.listdir(TRANSCRIPT_PATH)  # as above
    filelist = sorted(raw_doc)  # sort the pdfs in order
    onlyfiles = [f for f in filelist if os.path.isfile(os.path.join(TRANSCRIPT_PATH, f))]  # keep if in correct dir

    raw_text = pd.DataFrame([])  # empty dataframe

    start = timeit.default_timer()
    for i, file in enumerate(filelist):
        #print('Document {} of {}: {}'.format(i, len(filelist), file))
        with open(os.path.join(TRANSCRIPT_PATH, file), 'r') as inf:
            parsed = inf.read()
        
        try:
            pre  = re.compile("Transcript\s?of\s?(?:the:?)?\s?Federal\s?Open\s?Market\s?Committee",re.IGNORECASE)
            parsed = re.split(pre,parsed)[1]    
        except:  
            try:
                pre  = re.compile("Transcript\s?of\s?(?:Telephone:?)?\s?Conference\s?Call",re.IGNORECASE)
                parsed = re.split(pre,parsed)[1] 
            except:  
                print("No split")
                parsed = parsed  
        interjections = re.split('\nMR. |\nMS. |\nCHAIRMAN |\nVICE CHAIRMAN ', parsed)  # split the entire string by the names (looking for MR, MS, Chairman or Vice Chairman)
        temp_df = pd.DataFrame(columns=['Date', 'Speaker', 'content'])  # create a temporary dataframe
        interjections = [interjection.replace('\n', ' ') for interjection in
                         interjections]  # replace \n linebreaks with spaces
        temp = [re.split('(^\S*)', interjection.lstrip()) for interjection in
                interjections]  # changed to this split because sometimes (rarely) there was not a period, either other punctuation or whitespace
        speaker = []
        content = []
        for interjection in temp:
            speaker.append(interjection[1].strip(string.punctuation))
            content.append(interjection[2])
        temp_df['Speaker'] = speaker
        temp_df['content'] = content  # save interjections
        temp_df['Date'] = file[:10]
        raw_text = pd.concat([raw_text, temp_df], axis=0)
    end = timeit.default_timer()   
    #raw_text.to_excel(os.path.join(CACHE_PATH,'raw_text.xlsx'))  # save as raw_text.xlsx
    print("Transcripts processed. Time: {}".format(end - start))    
    docs = raw_text.groupby('Date')['content'].sum().to_list()
    return docs,raw_text