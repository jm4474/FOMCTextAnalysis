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


DATAPATH = os.path.expanduser("~/Dropbox/MPCounterfactual/src/etm/")        

# Show datasets:
print( os.listdir(f"{DATAPATH}/data"))

# Run Skipgram
for corpus in ['BBTSST_10_iter2_th2']:
    print(f"Run model: {corpus}")
    os.system(f"python skipgram_man.py --data_file {DATAPATH}/data/{corpus}/corpus.pkl --modelfile {DATAPATH}/word2vecmodels/{corpus} --emb_file {DATAPATH}/embeddings/{corpus}_emb --dim_rho 300 --iters 50 --window_size 4")


# Pre-trained model
import gensim.downloader
print(list(gensim.downloader.info()['models'].keys()))

glove_vectors = gensim.downloader.load("glove-wiki-gigaword-300")
glove_vectors.most_similar('inflation')

# Model Evaluation
corpus = 'BBTSST_10_iter2_th2'
model = gensim.models.Word2Vec.load(f"{DATAPATH}/word2vecmodels/{corpus}.model").wv
model.most_similar('inflation')
