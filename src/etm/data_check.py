import os, shutil
import re
import csv
import pandas as pd

TRANSCRIPT_PATH = os.path.expanduser("~/Dropbox/MPCounterfactual/src/collection/python/data/transcript_raw_text")
BB_PATH = os.path.expanduser("~/Dropbox/MPCounterfactual/src/collection/python/output/bluebook_raw_text")
STATEMENT_PATH = os.path.expanduser("~/Dropbox/MPCounterfactual/src/derivation/python/output/statements_text_extraction.csv")
OUTPATH = os.path.expanduser("~/Dropbox/MPCounterfactual/src/etm/data")        
SPEAKER_PATH = os.path.expanduser("~/Dropbox/MPCounterfactual/src/analysis/python/output")        
DATAPATH = os.path.expanduser("~/Dropbox/MPCounterfactual/src/etm/")        

if not os.path.exists(f"{DATAPATH}/full_results"):
        os.makedirs(f"{DATAPATH}/full_results")


### SPEAKERS ###
max_df = 0.7 # in a maximum of # % of documents if # is float.
min_df = 10  # choose desired value for min_df // in a minimum of # documents
phrase_itera = 2
threshold = "inf"

DATASET = f"SPEAKERS_{min_df}_iter{phrase_itera}_th{threshold}"
raw_df  = pd.read_pickle(f"raw_data/speaker_data.pkl")

idx_df = pd.read_pickle(f'{OUTPATH}/{DATASET}/original_indices.pkl')
idx_df = idx_df.set_index(0)
idx_df["d"] = 1

data = pd.concat([idx_df,raw_df],axis=1)
data_clean = data[data["d"]==1].reset_index()

dist_df = pd.read_pickle(f'{DATAPATH}/topicdistribution/fomc_pre.pkl')

full_data = pd.concat([data_clean,dist_df],axis=1)
full_data.drop(columns=["content","d"],inplace=True)
full_data.rename(columns=dict(zip([i for i in range(10)],[f"topic_{i}" for i in range(10)])),inplace=True)
full_data.columns
full_data.to_stata(f"{DATAPATH}/full_results/speakers.dta")


### MEETING ###
max_df = 1.0 # in a maximum of # % of documents if # is float.
min_df = 1  # choose desired value for min_df // in a minimum of # documents
phrase_itera = 2
threshold = "inf"

DATASET = f"MEETING_{min_df}_iter{phrase_itera}_th{threshold}"
raw_df  = pd.read_pickle(f"raw_data/meeting_data.pkl")

idx_df = pd.read_pickle(f'{OUTPATH}/{DATASET}/original_indices.pkl')
idx_df = idx_df.set_index(0)
idx_df["d"] = 1

data = pd.concat([idx_df,raw_df],axis=1)
data_clean = data[data["d"]==1].reset_index()

dist_df = pd.read_pickle(f'{DATAPATH}/topicdistribution/meeting_pre.pkl')

full_data = pd.concat([data_clean,dist_df],axis=1)

full_data.drop(columns=["content"],inplace=True)
full_data.rename(columns=dict(zip([i for i in range(10)],[f"topic_{i}" for i in range(10)])),inplace=True)
full_data.columns
full_data.to_stata(f"{DATAPATH}/full_results/meetings.dta")

