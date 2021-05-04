### Model Training and Evaluation ###
# Author: Oliver Giesecke 

from IPython import get_ipython
get_ipython().magic('reset -sf')

import os, shutil
import re
import csv
from utils import bigrams, trigram, replace_collocation
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
from gensim.models import Word2Vec
from data_concatenate import *
import gensim.downloader
import pprint
from manetm import etm
from analyze_moneysupply import import_data
import matplotlib.pyplot as plt
import matplotlib.ticker as tkr
pp = pprint.PrettyPrinter()
import datetime
import time

def get_weekly(x):
    x["year"] = x["date"].isocalendar()[0]
    x["week"] = x["date"].isocalendar()[1]
    return x

def getDateRangeFromWeek(p_year,p_week):
    firstdayofweek = datetime.datetime.strptime(f'{p_year}-W{int(p_week )}-1', "%Y-W%W-%w").date()
    lastdayofweek = firstdayofweek + datetime.timedelta(days=6.9)
    return firstdayofweek

# =============================================================================

DATAPATH = os.path.expanduser("~/Dropbox/MPCounterfactual/src/etm/")        
OVERLEAF = os.path.expanduser("~/Dropbox/MPandRiskPremia/CBS_PTS_04172021/files")
PROJECTPATH = os.path.expanduser("~/Dropbox/MPandRiskPremia")
#os.path.expanduser("~/Dropbox/Apps/Overleaf/FOMC_Summer2019/files")

if not os.path.exists(f"{DATAPATH}/full_results"):
        os.makedirs(f"{DATAPATH}/full_results")

# =============================================================================
# #0 Set Parameters
# =============================================================================

# Dataset parameters
embphrase_itera = 2 # Number of phrase iterations
embthreshold = "inf" # Threshold value for collocations. If "inf": no collocations
emb_max_df = 1.0 # in a maximum of # % of documents if # is float.
emb_min_df = 1  # choose desired value for min_df // in a minimum of # documents
EMBDATASET = f"BBTSST_min{emb_min_df}_max{emb_max_df}_iter{embphrase_itera}_th{embthreshold}"

meetphrase_itera = 2 
meetthreshold = "inf"
meetmax_df = 1.0
meetmin_df = 10
MEEETDATA = f"MEET_min{meetmin_df}_max{meetmax_df}_iter{meetphrase_itera}_th{meetthreshold}"

# =============================================================================
# sta_phrase_itera = 2
# sta_threshold = "inf"
# sta_max_df = 1.0
# sta_min_df = 5
# STADATASET = f"STATEMENT_min{sta_min_df}_max{sta_max_df}_iter{sta_phrase_itera}_th{sta_threshold}"
# 
# =============================================================================
# Skipgram parameters
mincount = 2
d_sg = 1
vectorsize = 300
iters = 100
cpus = 16 
neg_samples =  10
windowsize = 4

# Activate code 
d_construct = False
d_estemb = False
d_train = False


# =============================================================================
# #1 Data Preparation
# =============================================================================

if d_construct:
    
    print("*" * 80)
    print("Build datasets")
    
    build_embdata(emb_max_df,emb_min_df,embphrase_itera,embthreshold,EMBDATASET)
    build_meeting(meetmax_df,meetmin_df,meetphrase_itera,meetthreshold,MEEETDATA)
    #build_statement_data(sta_max_df,sta_min_df,sta_phrase_itera,sta_threshold,STADATASET)
    
    print("*" * 80)
    print("Datasets Construction Completed")
    print("*" * 80)
    print("\n")


# =============================================================================
# #2 Train Word Embeddings
# =============================================================================

if d_estemb:
    # Run Skipgram
    print(f"Run model: {EMBDATASET}\n")
       
    sentences = pd.read_pickle(f"{DATAPATH}/data/{EMBDATASET}/corpus.pkl")
    model = gensim.models.Word2Vec(sentences, min_count = mincount, sg = d_sg, vector_size = vectorsize, epochs = iters, workers = cpus, negative = neg_samples, window = windowsize)
    model.save(f"{DATAPATH}/word2vecmodels/{EMBDATASET}")
    
    # Write the embeddings to a file
    with open(f"{DATAPATH}/embeddings/{EMBDATASET}_emb", 'w') as f:
        for v in model.wv.index_to_key:
            vec = list(model.wv[v])
            f.write(v + ' ')
            vec_str = ['%.9f' % val for val in vec]
            vec_str = " ".join(vec_str)
            f.write(vec_str + '\n')
    
    print("*" * 80)
    print(f"Embedding Training Completed")
    print("*" * 80)
    print("\n\n")



# =============================================================================
## #4 TRAIN TOPIC MODELS
# =============================================================================

# =============================================================================
## SPEAKERDATA - Pre-Trained Emb.
# speaker_ckpt = etm(f"{SPEAKERDATA}",data_path=f"{DATAPATH}/data/{SPEAKERDATA}",
#         emb_path=f"{DATAPATH}/embeddings/{EMBDATASET}_emb",save_path=f"{DATAPATH}/results",
#         batch_size = 1000, epochs = 150, num_topics = 10, rho_size = 300,
#         emb_size = 300, t_hidden_size = 800, theta_act = 'relu',
#         train_embeddings = 0,  lr = 0.005,  lr_factor=4.0,
#         mode = 'train', optimizer = 'adam',
#         seed = 2019, enc_drop = 0.0, clip = 0.0,
#         nonmono = 10, wdecay = 1.2e-6, anneal_lr = 0, bow_norm = 1,
#         num_words =10, log_interval = 2, visualize_every = 10, eval_batch_size = 1000,
#         load_from = "", tc = 1, td = 1)
# 
# print(f"Evaluate model: {speaker_ckpt}")
# etm(f"{SPEAKERDATA}",data_path=f"{DATAPATH}/data/{SPEAKERDATA}",
#     emb_path=f"{DATAPATH}/embeddings/{EMBDATASET}_emb",save_path=f"{DATAPATH}/results",
#         mode = 'eval', load_from = f"{speaker_ckpt}", train_embeddings = 0 ,tc = 1, td = 1)
# 
# print(f"Output the topic distribution: {speaker_ckpt}")
# etm(f"{SPEAKERDATA}",data_path=f"{DATAPATH}/data/{SPEAKERDATA}",
#     emb_path=f"{DATAPATH}/embeddings/{EMBDATASET}_emb",save_path=f"{DATAPATH}/results",
#         mode = 'retrieve',load_from = f"{speaker_ckpt}", train_embeddings = 0)
# 
# =============================================================================

## MEETINGS - Pre-Trained Emb.
if d_train:
    meeting_ckpt = etm(f"{MEEETDATA}",data_path=f"{DATAPATH}/data/{MEEETDATA}",
            emb_path=f"{DATAPATH}/embeddings/{EMBDATASET}_emb",save_path=f"{DATAPATH}/results",
            batch_size = 1000, epochs = 2000, num_topics = 10, rho_size = 300,
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




# =============================================================================
## #5 OUTPUT DATA
# =============================================================================

# =============================================================================
# ## SPEAKERDATA
# raw_df  = pd.read_pickle(f"raw_data/{SPEAKERDATA}.pkl")
# 
# idx_df = pd.read_pickle(f'{OUTPATH}/{SPEAKERDATA}/original_indices.pkl')
# idx_df = idx_df.set_index(0)
# idx_df["d"] = 1
# 
# data = pd.concat([idx_df,raw_df],axis=1)
# data_clean = data[data["d"]==1].reset_index()
# dist_df = pd.read_pickle(f'{speaker_ckpt}tpdist.pkl')
# 
# full_data = pd.concat([data_clean,dist_df],axis=1)
# full_data.drop(columns=["content","d"],inplace=True)
# full_data.rename(columns=dict(zip([i for i in range(10)],[f"topic_{i}" for i in range(10)])),inplace=True)
# full_data["start_date"] = pd.to_datetime(full_data["start_date"])
# full_data.to_stata(f"{DATAPATH}/full_results/{SPEAKERDATA}.dta",convert_dates={"start_date":"td"})
# 
# =============================================================================

### MEETING ###


qe_dates = pd.read_excel(f"{DATAPATH}/raw_data/qedates.xlsx")
qe_dates["dates"] = qe_dates["Date"].apply(lambda x: np.datetime64(f"{x[-4:]}-{x[3:5]}-{x[:2]}" ))

sushko_dates = qe_dates["dates"].to_list()

meet_data = pd.read_pickle(f"{DATAPATH}/data/{MEEETDATA}/rawdata.pkl")
meet_data.reset_index(inplace=True)
meet_data.drop(columns=['cleaned_content','sampled_content'],inplace=True)

meet_topics = pd.read_pickle(f"{DATAPATH}/results/{MEEETDATA}_topics.pkl")
top_dic = dict(zip([item[0] + 1 for item in meet_topics ],[", ".join(item[1]) for item in meet_topics ] ))

meet_topicdstr = pd.read_pickle(f"{DATAPATH}/results/{MEEETDATA}_tpdist.pkl")
meet_topicdstr.rename(columns=dict(zip([i for i in range(10)],[f"topic_{i+1}" for i in range(10)])),inplace=True)

meet_full = pd.concat([meet_data,meet_topicdstr],axis=1)

section1 = meet_full[meet_full["Section"]==1].copy()
section2 = meet_full[meet_full["Section"]==2].copy()
section3 = meet_full[meet_full["Section"]==3].copy()

for i in range(1,11):
    section1[f"topic_{i}"] = section1[f"topic_{i}"] * 100
    section2[f"topic_{i}"] = section2[f"topic_{i}"] * 100
    section3[f"topic_{i}"] = section3[f"topic_{i}"] * 100


for k in range(1,11):
    print(f"Topic: {k}")
    fig = plt.figure(figsize=(20,9))
    axs = fig.add_subplot(1,1,1)
    plt.subplots_adjust(.1,.20,1,.95)
    section1.plot.scatter('start_date',f'topic_{k}',color="dodgerblue",ax=axs,label="Section 1")
    section2.plot.scatter('start_date',f'topic_{k}',color="red",ax=axs,label="Section 2")
    plt.figtext(0.10, 0.05, f"Topic {k} words: {top_dic[k]}", ha="left", fontsize=20)
    axs.set_xlabel("Meeting Day",fontsize=20)
    axs.set_ylabel(f"Topic {k}",fontsize=20)
    axs.yaxis.set_major_formatter(tkr.FuncFormatter(lambda x, p: f"{x:.2f}"))
    axs.grid(linestyle=':')
    axs.tick_params(which='both',labelsize=20,axis="y")
    axs.tick_params(which='both',labelsize=20,axis="x")
    axs.legend( prop={'size': 20})
    plt.savefig(f"{OVERLEAF}/fig_transcript_topic_{k}.pdf")

for k in range(1,11):
    print(f"Topic: {k}")
    fig = plt.figure(figsize=(20,9))
    axs = fig.add_subplot(1,1,1)
    plt.subplots_adjust(.1,.20,1,.95)
    section2.plot.scatter('start_date',f'topic_{k}',color="red",ax=axs,label="Section 2")
    section3.plot.scatter('start_date',f'topic_{k}',color="dodgerblue",ax=axs,label="Section 3")
    plt.figtext(0.10, 0.05, f"Topic {k} words: {top_dic[k]}", ha="left", fontsize=20)
    axs.set_xlabel("Meeting Day",fontsize=20)
    axs.set_ylabel(f"Topic {k}",fontsize=20)
    axs.yaxis.set_major_formatter(tkr.FuncFormatter(lambda x, p: f"{x:.2f}"))
    axs.grid(linestyle=':')
    axs.tick_params(which='both',labelsize=20,axis="y")
    axs.tick_params(which='both',labelsize=20,axis="x")
    axs.legend( prop={'size': 20})
    plt.savefig(f"{OVERLEAF}/fig_statement_topic_{k}.pdf")

reshaped = meet_full.pivot_table(index ='start_date', columns="Section", values = [f"topic_{i}" for i in range(1,11)]).reset_index()
reshaped.fillna(0,inplace=True)
reshaped[reshaped[('start_date',  '')] > "2007-01-01" ].plot.scatter( x = (   'topic_2', 2.0), y =     (   'topic_2', 3.0))

# =============================================================================
# CONSTRUCT DATA FOR THE ANALYSIS
# =============================================================================

meetingdates,qe_dic,ivm_df,datavix,data_yield,data_grouped,swaptions_df = import_data()

    # CONCATENATE MARKET DATA
market_df = datavix.merge(swaptions_df.reset_index(), on = "date", how = "outer")
market_df["weekday"] = market_df["date"].apply(lambda x : x.weekday())    
market_df.drop(columns = "weekday",inplace=True)

df1 = section1[[ 'end_date'] + [f"topic_{i}" for i in range(1,11)]].rename(columns = dict(zip([f"topic_{i}" for i in range(1,11)],[f"dis_topic_{i}" for i in range(1,11)]))).set_index('end_date')
df2 = section2[[ 'end_date'] + [f"topic_{i}" for i in range(1,11)]].rename(columns = dict(zip([f"topic_{i}" for i in range(1,11)],[f"pol_topic_{i}" for i in range(1,11)]))).set_index('end_date')
df3 = section3[[ 'end_date'] + [f"topic_{i}" for i in range(1,11)]].rename(columns = dict(zip([f"topic_{i}" for i in range(1,11)],[f"sta_topic_{i}" for i in range(1,11)]))).set_index('end_date')
meeting_type = meet_full[['end_date',"event_type"]].drop_duplicates().set_index('end_date')
df = pd.concat([meeting_type,df1,df2,df3],axis = 1).reset_index()
df["weekday"] = df["end_date"].apply(lambda x : x.weekday())    
df = df[df["weekday"]!=6].copy()
df.drop(columns = "weekday",inplace=True)
df.loc[:,"d_MP"] = np.nan
df.loc[df["event_type"] == "Meeting","d_MP"] = 1
del df1, df2, df3, meeting_type

data_export = market_df.merge(df.rename(columns = {"end_date":"date"}),on="date",how="outer")
data_export.sort_values(by = "date",inplace=True)
data_export = data_export[(data_export["date"] >= "2002-01-01") & (data_export["date"] <= "2016-01-01")].copy().reset_index(drop=True)

# Assign eventdates
data_export.loc[:,"event_time"] = np.nan
data_export.loc[:,"event_window"] = np.nan
j = 1
for idx,row in data_export.iterrows():
    if not np.isnan(row["d_MP"]):
        date = row["date"]
        print(date)
        data_export.loc[data_export["date"] == date,"event_time"] = 1
        data_export.loc[data_export["date"] == date,"event_window"] = j 
        for i in range(1,9):
            newdate_b = date + datetime.timedelta(days=-i )
            newdate_f = date + datetime.timedelta(days= i )
            
            data_export.loc[idx - i,"event_window"] = j
            data_export.loc[idx + i,"event_window"] = j
            data_export.loc[idx - i,"event_time"] = -i + 1
            data_export.loc[idx + i,"event_time"] = i + 1
        j += 1            

data_export = data_export[~data_export["date"].isna()].copy()

cols = [ 'dis_topic_1', 'dis_topic_2', 'dis_topic_3', 'dis_topic_4',
       'dis_topic_5', 'dis_topic_6', 'dis_topic_7', 'dis_topic_8',
       'dis_topic_9', 'dis_topic_10', 'pol_topic_1', 'pol_topic_2',
       'pol_topic_3', 'pol_topic_4', 'pol_topic_5', 'pol_topic_6',
       'pol_topic_7', 'pol_topic_8', 'pol_topic_9', 'pol_topic_10',
       'sta_topic_1', 'sta_topic_2', 'sta_topic_3', 'sta_topic_4',
       'sta_topic_5', 'sta_topic_6', 'sta_topic_7', 'sta_topic_8',
       'sta_topic_9', 'sta_topic_10']


import requests
import io


dls = "https://www.financialresearch.gov/financial-stress-index/data/fsi.csv?"
datafsi = requests.get(dls)
datafsi = datafsi.content
datafsi = pd.read_csv(io.StringIO(datafsi.decode('utf-8'))).rename(columns={"Date":"date"})
datafsi["date"] = pd.to_datetime(datafsi["date"])


m_topics = data_export.groupby("event_window")[cols].mean().reset_index()
data_export = data_export.drop(columns = cols).merge(m_topics,on = "event_window",how="left")
data_export = data_export.merge(datafsi,on="date",how="left")
data_export.rename(columns=dict(zip(data_export.columns,[col.replace(" ","_") for col in data_export.columns])) ).to_stata(f"{PROJECTPATH}/int/stata_analysis.dta", write_index=False,convert_dates={"date":"td"})


# =============================================================================
# INTRODUCTION
# =============================================================================
matplotlib.rc('xtick', labelsize=20) 
matplotlib.rc('ytick', labelsize=20) 
plt.rcParams.update({'font.size': 20})

dates = ["2020-03-03","2020-03-15","2020-03-23"]

startdate = "2020-02-22"
enddate = "2020-04-15"

fig, ax = plt.subplots(1,figsize=(24,14))
fig.tight_layout(rect=[0.05, 0.05, 1, 0.95])
datavix[(datavix["date"]>=startdate) & 
          (datavix["date"]<=enddate)].plot(
              x ="date", y= 'MOVE INDEX',c="blue",ax=ax,label="MOVE Index",style='-o',linewidth=2,markersize=12)
datavix[(datavix["date"]>=startdate) & 
          (datavix["date"]<=enddate)].plot(
              x ="date", y= 'VIX INDEX',c="red",ax=ax,label="VIX Index",style='-s',linewidth=2,markersize=12)
fortmatstring = "{:.1f}"
ax.yaxis.set_major_formatter(tkr.FuncFormatter(lambda x,p: fortmatstring.format(x)))
ax.grid(linestyle=':')
ax.set_xlabel("")
ax.legend(loc="upper left")
plt.savefig(f"{OVERLEAF}/fig_covid.pdf")


fig, ax = plt.subplots(1,figsize=(24,14))
fig.tight_layout(rect=[0.05, 0.05, 1, 0.95])
datavix[(datavix["date"]>=startdate) & 
          (datavix["date"]<=enddate)].plot(
              x ="date", y= 'MOVE INDEX',c="blue",ax=ax,label="MOVE Index",style='-o',linewidth=2,markersize=12)
datavix[(datavix["date"]>=startdate) & 
          (datavix["date"]<=enddate)].plot(
              x ="date", y= 'VIX INDEX',c="red",ax=ax,label="VIX Index",style='-s',linewidth=2,markersize=12)
for qedate in dates:
    plt.axvline(np.datetime64(qedate),c="purple")

fortmatstring = "{:.1f}"
ax.yaxis.set_major_formatter(tkr.FuncFormatter(lambda x,p: fortmatstring.format(x)))
ax.grid(linestyle=':')
ax.set_xlabel("")
ax.legend(loc="upper left")
plt.savefig(f"{OVERLEAF}/fig_covid.eps")

              

    # COVID PURCHASES

data_grouped["date"] = data_grouped["date"].apply(lambda x:np.datetime64(x))
datavix["date"] = pd.to_datetime(datavix["date"])
newdata = datavix.merge(data_grouped,on = "date",how="outer")

fig, ax = plt.subplots(1,figsize=(24,14))
fig.tight_layout(rect=[0.05, 0.05, 1, 0.95])
newdata[(newdata["date"]>=startdate) & 
          (newdata["date"]<=enddate)].plot.line(
              x ="date", y=  'MOVE INDEX',c="green",ax=ax,label="MOVE Index",style='-o')
fortmatstring = "{:.1f}"
ax1 = ax.twinx()
newdata[(newdata["date"]>=startdate) & 
         (newdata["date"]<=enddate)].plot.line( x='date', y = 'd1_tsy', color = "black", ax=ax1,label="Treasury Sec.",style='-o')
newdata[(newdata["date"]>=startdate) & 
         (newdata["date"]<=enddate)].plot.line( x='date', y = 'd1_mbs', color = "red", ax=ax1,label="MBS",style='-o')
newdata[(newdata["date"]>=startdate) & 
         (newdata["date"]<=enddate)].plot.line( x='date', y = 'd1_agency', color = "blue", ax=ax1,label="Agency MBS",style='-o')
ax.yaxis.set_major_formatter(tkr.FuncFormatter(lambda x,p: fortmatstring.format(x)))
ax.grid(linestyle=':')
lines, labels = ax.get_legend_handles_labels()
lines2, labels2 = ax1.get_legend_handles_labels()
ax.legend(lines + lines2, labels + labels2, loc=0)

# =============================================================================
# VAR
# =============================================================================

rel_path = "~/Dropbox/AggregateDemandInflation"


cols = [['date','VIX INDEX'],['date.1',  'MOVE INDEX'],["date.2",  "MLT1US10 Index"]]
vix = pd.DataFrame([])
for col in cols:
    print(col)
    new = pd.read_excel(f"{rel_path}/Data/raw/fred/longts.xlsx",sheet_name="data")[col]
    new.rename(columns = {col[0]:"date",col[1]:col[1].strip()},inplace=True)
    new = new[~new["date"].isna()].copy()
    new["date"] = pd.to_datetime(new["date"])
    new.set_index("date",inplace=True)   
    vix = pd.concat([new,vix],axis=1)
vix.reset_index(inplace=True)

    ### IV Indices
cols = [['date', 'SPX INDEX'], ['date.1', 'LUATTRUU INDEX'],
        ['date.2','SPBDU1BT Index'], ['date.3', 'FEDL01 Index']]

returns = pd.DataFrame([])
for col in cols:
    print(col)
    new = pd.read_excel(f"{rel_path}/Data/raw/fred/bondandequityreturns.xlsx",sheet_name="data")[col]
    new.rename(columns = {col[0]:"date",col[1]:col[1].strip()},inplace=True)
    new = new[~new["date"].isna()].copy()
    new["date"] = pd.to_datetime(new["date"])
    new.set_index("date",inplace=True)   
    returns = pd.concat([new,returns],axis=1)
    

returns.reset_index(inplace=True)
returns = returns.merge(vix,on="date",how="outer")
returns["year"] = returns["date"].apply(lambda x:x.year)
returns["month"] = returns["date"].apply(lambda x:x.month)
returns = returns[~returns["SPX INDEX"].isna()].copy()
# Create log returns
for col in ['SPBDU1BT Index', 'LUATTRUU INDEX', 'SPX INDEX', "MLT1US10 Index"]:
    returns[f"ln_{col.replace(' ','_')}" ] = returns[col].apply(lambda x: np.log(x))
    returns[f"lnr_{col.replace(' ','_')}" ] = returns[f"ln_{col.replace(' ','_')}" ]  - returns[f"ln_{col.replace(' ','_')}" ].shift(1)
    returns[f"r_{col.replace(' ','_')}" ] = returns[f"{col}" ]  / returns[f"{col}" ].shift(1) - 1
    returns[f"lnr2_{col.replace(' ','_')}" ] = returns[f"lnr_{col.replace(' ','_')}" ].apply(lambda x: x**2)
    returns[f"r2_{col.replace(' ','_')}" ] = returns[f"r_{col.replace(' ','_')}" ].apply(lambda x: x**2)
        
returns["day"] = 1    
variance_m = returns.groupby(["year","month"])[[f"lnr2_{col.replace(' ','_')}" for col in ['SPBDU1BT Index', 'LUATTRUU INDEX', 'SPX INDEX',"MLT1US10 Index"]] + [f"r2_{col.replace(' ','_')}" for col in ['SPBDU1BT Index', 'LUATTRUU INDEX', 'SPX INDEX',"MLT1US10 Index"]] + ["day"]].sum().reset_index()
variance_m.rename(columns = {"lnr2_SPBDU1BT_Index":"var_10try","lnr2_LUATTRUU_INDEX":"var_trypf",  "lnr2_SPX_INDEX":"var_sp500","lnr2_MLT1US10_Index":"var_10future"},inplace=True)
for col in [ 'r2_SPBDU1BT_Index', 'r2_LUATTRUU_INDEX',
       'r2_SPX_INDEX', 'r2_MLT1US10_Index']:
    variance_m[col] =    variance_m.apply(lambda x: x[col] * 252 / x["day"],axis=1)

iv_eom = returns.loc[returns.groupby(["year","month"])["date"].idxmax(),["year","month",'MOVE INDEX', 'VIX INDEX']].reset_index().rename(columns = {'MOVE INDEX':"eom_MOVE", 'VIX INDEX':"eom_VIX"})
iv_mean = returns.groupby(["year","month"])[['MOVE INDEX', 'VIX INDEX']].mean().reset_index().rename(columns = {'MOVE INDEX':"mean_MOVE", 'VIX INDEX':"mean_VIX"})

full_data = variance_m.merge(iv_eom,on=["year","month"],how = "outer").merge(iv_mean,on=["year","month"],how = "outer").drop(columns="index")
full_data["date"] = full_data.apply(lambda x: np.datetime64(f"{x['year']:.0f}-{x['month']:02.0f}-01"),axis=1)
for col in ['var_10try', 'var_trypf', 'var_sp500', 'var_10future','eom_MOVE', 'eom_VIX', 'mean_MOVE', 'mean_VIX']:
    full_data[col] = full_data[col].apply(lambda x: np.log(x))    


fred_md = pd.read_pickle(os.path.expanduser("~/Dropbox/DeepAssetPricingData/raw/fred_md_current.pkl"))[["PAYEMS",'INDPRO',"FEDFUNDS","sasdate"]]
# Create log and log differences
for col in ["PAYEMS",'INDPRO']:
    fred_md[f"ln_{col}"] = fred_md[f"{col}"].apply(lambda x:np.log(x))
    fred_md[f"dln_{col}"] = fred_md[f"ln_{col}"] - fred_md[f"ln_{col}"].shift(1)
    
fred_md["year"] = fred_md["sasdate"].apply(lambda x:x.year)
fred_md["month"] = fred_md["sasdate"].apply(lambda x:x.month)

data_analysis = fred_md[["year","month","dln_PAYEMS",'dln_INDPRO',"ln_PAYEMS",'ln_INDPRO',"FEDFUNDS"]].merge(full_data[['year', 'month', 'var_10try', 'var_trypf', 'var_sp500', 'var_10future',
       'eom_MOVE', 'eom_VIX', 'mean_MOVE', 'mean_VIX']],on=['year', 'month'],how= "outer")

for lag in range(1,5):
    for col in ['var_10try', 'var_trypf', 'var_sp500',
       'var_10future', 'eom_MOVE', 'eom_VIX', 'mean_MOVE', 'mean_VIX']:
        data_analysis[f"l{lag}_{col}"] = data_analysis[f"{col}"].shift(lag) 

data_analysis["constant"] = 1
data_analysis["date"] = data_analysis.apply(lambda x: np.datetime64(f"{x['year']:.0f}-{x['month']:02.0f}-01"),axis=1)

startdate = "2000-01-01"
enddate = "2019-12-31"
data_analysis = data_analysis[(data_analysis["date"]  >= startdate) & (data_analysis["date"]  <= enddate )].copy()

from python_nw import newey
for col in ['l1_eom_VIX','l2_eom_VIX','l3_eom_VIX','l4_eom_VIX']:
    data_analysis.fillna(method="ffill",inplace=True)

results = newey(data_analysis["dln_INDPRO"],data_analysis[["constant"] + ['l1_eom_VIX','l2_eom_VIX','l3_eom_VIX','l4_eom_VIX']],0)
results.beta[1:].mean() * 100

results = newey(data_analysis["dln_INDPRO"],data_analysis[["constant"] + ['l1_eom_VIX','l2_eom_VIX','l3_eom_VIX','l4_eom_VIX',
                                                                      'l1_var_sp500','l2_var_sp500','l3_var_sp500','l4_var_sp500']],0)
print(results.beta[1:5].mean() * 100) 
print(results.beta[5:].mean() * 100)

results = newey(data_analysis["dln_INDPRO"],data_analysis[["constant"] + [f'l{i}_eom_MOVE' for i in range(1,5)]],0)
print(results.beta[1:].mean() * 100)

results = newey(data_analysis["dln_INDPRO"],data_analysis[["constant"] + [f'l{i}_mean_MOVE' for i in range(1,5)] + [f'l{i}_mean_VIX' for i in range(1,5)]],0)
print(results.beta[1:5].mean() * 100)
print(results.beta[5:].mean() * 100)

results = newey(data_analysis["dln_INDPRO"],data_analysis[["constant"] +
                                                      [f'l{i}_mean_VIX' for i in range(1,5)] + 
                                                      [f'l{i}_var_sp500' for i in range(1,5)] + 
                                                      [f'l{i}_mean_MOVE' for i in range(1,5)] +
                                                      [f'l{i}_var_trypf' for i in range(1,5)]],0)
print(results.beta[1:5].mean() * 100)
print(results.beta[5:9].mean() * 100)
print(results.beta[9:13].mean() * 100)
print(results.beta[13:17].mean() * 100)

newdata = data_analysis[["year","month","ln_PAYEMS",'ln_INDPRO',"FEDFUNDS"]].rename(columns = {'ln_INDPRO':"lipm",'ln_PAYEMS':"lempm","FEDFUNDS":"ffr"})
newdata.to_csv(f"{PROJECTPATH}/int/newdata.csv",index=False)

materdates = newdata.apply(lambda x : int(f"{x['year']:.0f}{x['month']:02.0f}"),axis=1)
materdates.to_csv(f"{PROJECTPATH}/int/materdates.csv",index=False)


datafsi["year"] = datafsi["date"].apply(lambda x:x.year)
datafsi["month"] = datafsi["date"].apply(lambda x:x.month)

newdata = datafsi[(datafsi["date"]>=startdate) & (datafsi["date"]<=enddate) ].groupby(["year","month"])["OFR FSI"].mean().reset_index().rename(columns = {"OFR FSI":"mean_FSI"})
#newdata["mean_FSI"].to_csv(f"{PROJECTPATH}/int/ls_level1.csv",index=False)

data_analysis['mean_VIX'].to_csv(f"{PROJECTPATH}/int/ls_level1.csv",index=False)
data_analysis['mean_MOVE'].to_csv(f"{PROJECTPATH}/int/ls_cme_rvar.csv",index=False)
data_analysis['var_sp500'].to_csv(f"{PROJECTPATH}/int/ls_var_sp500.csv",index=False)
data_analysis['var_trypf'].to_csv(f"{PROJECTPATH}/int/ls_var_trypf.csv",index=False)



fig, ax = plt.subplots(1,figsize=(24,14))
fig.tight_layout(rect=[0.05, 0.05, 1, 0.95])
data_analysis.plot.line(x ="date", y=  'mean_MOVE',c="green",ax=ax,label="MOVE Index",style='-o')
ax1 = ax.twinx()
data_analysis.plot.line(x ="date", y=  'var_trypf',c="blue",ax=ax1,label="Bond Vola",style='-o')
fortmatstring = "{:.1f}"
ax.yaxis.set_major_formatter(tkr.FuncFormatter(lambda x,p: fortmatstring.format(x)))
ax.grid(linestyle=':')

fig, ax = plt.subplots(1,figsize=(24,14))
fig.tight_layout(rect=[0.05, 0.05, 1, 0.95])
data_analysis.plot.line(x ="date", y=  'mean_VIX',c="green",ax=ax,label="VIX Index",style='-o')
ax1 = ax.twinx()
data_analysis.plot.line(x ="date", y=  'var_sp500',c="blue",ax=ax1,label="Equity Vola",style='-o')
fortmatstring = "{:.1f}"
ax.yaxis.set_major_formatter(tkr.FuncFormatter(lambda x,p: fortmatstring.format(x)))
ax.grid(linestyle=':')




# =============================================================================
# VISUALIZATION
# =============================================================================


source ="Office of Financial Research. 'OFR Financial Stress Index.'"
title = "OFR Financial Stress Index"
ylabel = "Index"


startdate = "2006-01-01"
enddate = "2016-01-01"

fig, ax = plt.subplots(1,figsize=(24,14))
fig.tight_layout(rect=[0.05, 0.05, 1, 0.95])
datafsi[(datafsi["date"]>=startdate) & 
          (datafsi["date"]<=enddate)].plot(
              x ="date", y=  'OFR FSI',c="blue",ax=ax,label="OFR FSI (l-axis)",style='-o',lw=2,markerfacecolor="blue",markersize=6)
fortmatstring = "{:.1f}"
ax1 = ax.twinx()
section2[(section2["start_date"]>=startdate) & 
         (section2["start_date"]<=enddate) & 
         (section2["event_type"]=="Meeting") ].plot.line(
             x='start_date', y = 'topic_2', color = "black", ax=ax1,label="Section 2 - Topic 2 (r-axis)",style='-o')
ax.yaxis.set_major_formatter(tkr.FuncFormatter(lambda x,p: fortmatstring.format(x)))
ax.grid(linestyle=':')
lines, labels = ax.get_legend_handles_labels()
lines2, labels2 = ax1.get_legend_handles_labels()
ax1.legend(lines + lines2, labels + labels2, loc=0)
plt.savefig(f"{OVERLEAF}/fig_fsi.pdf")


    # WEEKLY VOLATILITY
datavix['scale_MOVEINDEX'] = datavix['MOVE INDEX'] / 3
datavix = datavix.apply(get_weekly,axis=1)
datavix_w =  datavix.groupby(["year","week"])["VIX INDEX",'scale_MOVEINDEX'].mean().reset_index()
datavix_w["date"] = datavix_w.apply(lambda x: getDateRangeFromWeek(int(x["year"]), x["week"]) ,axis=1)  
datavix_w["date"] = pd.to_datetime(datavix_w["date"])


    ### Bond Market Volatility ###

fig, ax = plt.subplots(1,figsize=(24,14))
fig.tight_layout(rect=[0.05, 0.05, 1, 0.95])
datavix_w[(datavix_w["date"]>=startdate) & 
          (datavix_w["date"]<=enddate)].plot(
              x ="date", y=  'scale_MOVEINDEX',c="blue",ax=ax,label="MOVE Index (l-axis)",style='-o',lw=2,markerfacecolor="blue",markersize=6)
fortmatstring = "{:.1f}"
ax1 = ax.twinx()
section2[(section2["start_date"]>=startdate) & 
         (section2["start_date"]<=enddate) & 
         (section2["event_type"]=="Meeting") ].plot.line(
             x='start_date', y = 'topic_2', color = "black", ax=ax1,label="Section 2 - Topic 2 (r-axis)",style='-o')
ax.yaxis.set_major_formatter(tkr.FuncFormatter(lambda x,p: fortmatstring.format(x)))
ax.grid(linestyle=':')
ax.set_ylim(10,90)
ax1.set_ylim(-5,45)
lines, labels = ax.get_legend_handles_labels()
lines2, labels2 = ax1.get_legend_handles_labels()
ax1.legend(lines + lines2, labels + labels2, loc=0)
plt.savefig(f"{OVERLEAF}/fig_ratevol.pdf")

    ### Equity Market Volatility ###
    
fig, ax = plt.subplots(1,figsize=(24,14))
fig.tight_layout(rect=[0.05, 0.05, 1, 0.95])
datavix_w[(datavix_w["date"]>=startdate) & 
          (datavix_w["date"]<=enddate)].plot(
              x ="date", y=  "VIX INDEX",c="red",ax=ax,label="VIX Index (l-axis)",style='-o',lw=2,markerfacecolor="red",markersize=6)
fortmatstring = "{:.1f}"
ax1 = ax.twinx()
section2[(section2["start_date"]>=startdate) & 
         (section2["start_date"]<=enddate) & 
         (section2["event_type"]=="Meeting") ].plot.line(x='start_date',
                                                         y = 'topic_2', color = "black",
                                                         ax=ax1,label="Section 2 - Topic 2 (r-axis)",style='-o',lw=2,markerfacecolor="black",markersize=12)
ax.set_ylim(0,80)
ax1.set_ylim(-10,50)
ax.yaxis.set_major_formatter(tkr.FuncFormatter(lambda x,p: fortmatstring.format(x)))
ax.grid(linestyle=':')
lines, labels = ax.get_legend_handles_labels()
lines2, labels2 = ax1.get_legend_handles_labels()
ax1.legend(lines + lines2, labels + labels2, loc=0)
plt.savefig(f"{OVERLEAF}/fig_equityvol.pdf")



    # Including Sushko Dates

fig, ax = plt.subplots(1,figsize=(24,14))
fig.tight_layout(rect=[0.05, 0.05, 1, 0.95])
datavix_w[(datavix_w["date"]>=startdate) & 
          (datavix_w["date"]<=enddate)].plot(
              x ="date", y=  "scale_MOVEINDEX",c="green",ax=ax,label="VIX Index (right-axis)")
fortmatstring = "{:.1f}"
ax1 = ax.twinx()
section2[(section2["start_date"]>=startdate) & 
         (section2["start_date"]<=enddate) & 
         (section2["event_type"]=="Meeting") ].plot.line(x='start_date',
                                                         y = 'topic_2', color = "black", ax=ax1,label="Section 2 - Topic 2",style='-o')

for qedate in sushko_dates:
    plt.axvline(qedate,c="purple")
ax.yaxis.set_major_formatter(tkr.FuncFormatter(lambda x,p: fortmatstring.format(x)))
ax.grid(linestyle=':')
lines, labels = ax.get_legend_handles_labels()
lines2, labels2 = ax1.get_legend_handles_labels()
ax1.legend(lines + lines2, labels + labels2, loc=0)








# =============================================================================
# fig, ax = plt.subplots(1,figsize=(12,7))
# fig.tight_layout(rect=[0.05, 0.05, 1, 0.95])
# #newdata[(newdata["date"]>=startdate) & (newdata["date"]<=enddate)].plot(x ="date", y=  "d1_tsy",ax=ax,c="blue",alpha=.6) 
# data_yield[(data_yield["date"]>=startdate) & (data_yield["date"]<=enddate)].plot(x ="date", y=  "dgs10ffr",ax=ax,label="10y-ffr Spread (left-axis)")
# fortmatstring = "{:.1f}"
# ax1 = ax.twinx()
# #datavix[(datavix["date"]>=startdate) & (datavix["date"]<=enddate)].plot(x ="date", y=  "VIX INDEX",c="red",alpha=.6,ax=ax1) 
# datavix[(datavix["date"]>=startdate) & (datavix["date"]<=enddate)].plot(x ="date", y=  "VIX1Y Index",c="red",alpha=.6,ax=ax1,label="VIX1Y Index (right-axis)")
# datavix[(datavix["date"]>=startdate) & (datavix["date"]<=enddate)].plot(x ="date", y=  'scale_MOVEINDEX',c="green",alpha=.6,ax=ax1,label="MOVE Index (right-axis)")
# section2.plot.scatter(x='start_date',y=f'topic_2',color="black",ax=ax1,label="Section 2")
# for qedate in list(qe_dic.values()):
#     plt.axvline(qedate,c="purple")
# ax.yaxis.set_major_formatter(tkr.FuncFormatter(lambda x,p: fortmatstring.format(x)))
# ax.grid(linestyle=':')
# # added these three lines
# lines, labels = ax.get_legend_handles_labels()
# lines2, labels2 = ax1.get_legend_handles_labels()
# ax1.legend(lines + lines2, labels + labels2, loc=0)
# 
# =============================================================================


# =============================================================================
# =============================================================================
# 
# fig, ax = plt.subplots(1,figsize=(24,14))
# fig.tight_layout(rect=[0.05, 0.05, 1, 0.95])
# datavix_w[(datavix_w["date"]>=startdate) & (datavix_w["date"]<=enddate)].plot(x ="date", y=  "VIX1Y Index",c="green",ax=ax,label="VIX1Y Index (right-axis)")
# fortmatstring = "{:.1f}"
# ax1 = ax.twinx()
# section2[(section2["start_date"]>=startdate) & (section2["start_date"]<=enddate) & (section2["event_type"]=="Meeting") ].plot.line(x='start_date',
#                                                                                                                                    y = 'topic_2', color = "black", ax=ax1,label="Section 2 - Topic 2",style='-o')
# ax.set_ylim(10,60)
# ax1.set_ylim(-10,50)
# for qedate in list(qe_dic.values()):
#     plt.axvline(qedate,c="purple")
# ax.yaxis.set_major_formatter(tkr.FuncFormatter(lambda x,p: fortmatstring.format(x)))
# ax.grid(linestyle=':')
# lines, labels = ax.get_legend_handles_labels()
# lines2, labels2 = ax1.get_legend_handles_labels()
# ax1.legend(lines + lines2, labels + labels2, loc=0)
# 
# 
# 
# fig, ax = plt.subplots(1,figsize=(12,7))
# fig.tight_layout(rect=[0.05, 0.05, 1, 0.95])
# #newdata[(newdata["date"]>=startdate) & (newdata["date"]<=enddate)].plot(x ="date", y=  "d1_tsy",ax=ax,c="blue",alpha=.6) 
# datavix_w[(datavix_w["date"]>=startdate) & (datavix_w["date"]<=enddate)].plot(x ="date", y=  'scale_MOVEINDEX',c="green",alpha=.6,ax=ax,label="MOVE Index (right-axis)")
# fortmatstring = "{:.1f}"
# ax1 = ax.twinx()
# section2[(section2["start_date"]>=startdate) & (section2["start_date"]<=enddate) & (section2["event_type"]=="Meeting") ].plot.line(x='start_date', y = 'topic_2', color = "black", ax=ax1,label="Section 2",style='-o')
# section3[(section3["start_date"]>=startdate) & (section3["start_date"]<=enddate) & (section3["event_type"]=="Meeting") ].plot.line(x='start_date', y = 'topic_2', color = "grey", ax=ax1,label="Section 3",style='-o')
# for qedate in list(qe_dic.values()):
#     plt.axvline(qedate,c="purple")
# ax.yaxis.set_major_formatter(tkr.FuncFormatter(lambda x,p: fortmatstring.format(x)))
# ax.grid(linestyle=':')
# lines, labels = ax.get_legend_handles_labels()
# lines2, labels2 = ax1.get_legend_handles_labels()
# ax1.legend(lines + lines2, labels + labels2, loc=0)
# 
# 
# 
# 
# 
# # =============================================================================
# # ## 7 MN Logit
# import statsmodels.api as sm
# import pandas as pd
# import numpy as np
# 
# DATAPATH = os.path.expanduser("~/Dropbox/MPCounterfactual/src/etm/")        
# OVERLEAF = os.path.expanduser("~/Dropbox/Apps/Overleaf/FOMC_Summer2019/files")
# topics = pd.read_stata("full_results/MEET_min10_max1.0_iter2_thinf.dta") 
# topics.rename(columns=dict(zip([f"topic_{k}" for k in range(10)],[f"topic_{k+1}" for k in range(10)] )),inplace=True)
# topics.drop(columns=["level_0","index", "d"],inplace=True)
# topics = topics[topics["start_date"]!="2009-09-16"]
# 
# econdata = pd.read_pickle("../economic_data/final_data/econmarketdata.pkl")
# data = topics.merge(econdata,left_on="start_date",right_on="date",how="inner")
# 
# for k in range(1,11):
#     data[f"lns{k}s5"] = np.log(data[f"topic_{k}"]) - np.log(data[f"topic_5"])
# 
# for k in range(1,11):
#     data[f"s{k}s5"] = data[f"topic_{k}"]  / data[f"topic_5"]
# 
# 
# data["constant"] = 1
# 
# covs = "l1d_UNRATE l2d_UNRATE l1dln_PCEPI l2dln_PCEPI l1dln_INDPRO l2dln_INDPRO d14ln_spindx d28_SVENY01 d28_SVENY10 TEDRATE SVENY01 SVENY10 BAA10Y AAA10Y"
# covs_list = covs.split(" ")
# 
# 
# 
# est_section1 = data.loc[data["Section"] == 1,[f"s{k}s5" for k in range(1,11) ]]
# res_df = pd.DataFrame([])
# for k in [1,2,3,4,6,7,8,9,10]:
#     print(f"\n ************** Topic: {k} ***********************\n")
#     model = sm.OLS(data.loc[data["Section"] == 1,f"lns{k}s5"], data.loc[data["Section"] == 1,["constant"]+covs_list])
#     results = model.fit()
#     print(results.summary())
# 
#     ef_dict = []
#     for var in covs_list:
#         est_section1[f"mr_{var}"] = est_section1[f"s{k}s5"]  * results.params[var]
#         ef_dict.append(est_section1[f"mr_{var}"].mean())
#     aux_df = pd.DataFrame(data=ef_dict,columns=[f"AMX T{k}"],index=list(results.params.keys())[1:])       
#     res_df = pd.concat([res_df,aux_df],axis=1)
#     
# labels = {"l1d_UNRATE":"Lag 1 dURate","l2d_UNRATE": "Lag 2 dURate","l1dln_PCEPI": "Lag 1 dlnPCEPI",
#           "l2dln_PCEPI": "Lag 2 dlnPCEPI","l1dln_INDPRO":"Lag 1 dlnIP","l2dln_INDPRO": "Lag 2 dlnIP",
#           "d7ln_spindx": "7 day Return S\&P500","d14ln_spindx":"14 day Return S\&P500",
#           "EQUITYCAPE": "Equity Cape","TEDRATE": "Ted Spread","SVENY01": "Tr. 1yr Yield",
#           "d28_SVENY01": "$\Delta$ Tr. 1yr Yield","d28_SVENY10": "$\Delta$ Tr. 10yr Yield",
#           "SVENY10": "Tr. 10yr Yield", "BAA10Y": "BAA Credit Spread","AAA10Y": "AAA Credit Spread"}
# res_df = res_df.reset_index().replace({"index":labels}).set_index("index")
# 
# print(res_df.to_latex(escape=False))
# res_df.to_latex(f"{OVERLEAF}/section1_avgmr.tex",escape=False,float_format="{:0.3f}".format )
# 
# 
# 
# 
# est_section1 = data.loc[data["Section"] == 2,[f"s{k}s5" for k in range(1,11) ]]
# res_df = pd.DataFrame([])
# for k in [1,2,3,4,6,7,8,9,10]:
#     print(f"\n ************** Topic: {k} ***********************\n")
#     model = sm.OLS(data.loc[data["Section"] == 2,f"lns{k}s5"], data.loc[data["Section"] == 2,["constant"]+covs_list])
#     results = model.fit()
#     print(results.summary())
# 
#     ef_dict = []
#     for var in covs_list:
#         est_section1[f"mr_{var}"] = est_section1[f"s{k}s5"]  * results.params[var]
#         ef_dict.append(est_section1[f"mr_{var}"].mean())
#     aux_df = pd.DataFrame(data=ef_dict,columns=[f"AMX T{k}"],index=list(results.params.keys())[1:])       
#     res_df = pd.concat([res_df,aux_df],axis=1)
#     
# labels = {"l1d_UNRATE":"Lag 1 dURate","l2d_UNRATE": "Lag 2 dURate","l1dln_PCEPI": "Lag 1 dlnPCEPI",
#           "l2dln_PCEPI": "Lag 2 dlnPCEPI","l1dln_INDPRO":"Lag 1 dlnIP","l2dln_INDPRO": "Lag 2 dlnIP",
#           "d7ln_spindx": "7 day Return S\&P500","d14ln_spindx":"14 day Return S\&P500",
#           "EQUITYCAPE": "Equity Cape","TEDRATE": "Ted Spread","SVENY01": "Tr. 1yr Yield",
#           "d28_SVENY01": "$\Delta$ Tr. 1yr Yield","d28_SVENY10": "$\Delta$ Tr. 10yr Yield",
#           "SVENY10": "Tr. 10yr Yield", "BAA10Y": "BAA Credit Spread","AAA10Y": "AAA Credit Spread"}
# res_df = res_df.reset_index().replace({"index":labels}).set_index("index")
# 
# print(res_df.to_latex(escape=False))
# res_df.to_latex(f"{OVERLEAF}/section2_avgmr.tex",escape=False,float_format="{:0.3f}".format )
# 
# =============================================================================
# 
# =============================================================================



# =============================================================================
# 
# 
# # Retrieve raw data
# raw_df  = pd.read_pickle(f"raw_data/{MEEETDATA}.pkl")
# 
# idx_df = pd.read_pickle(f'{OUTPATH}/{MEEETDATA}/original_indices.pkl')
# idx_df = idx_df.set_index(0)
# idx_df["d"] = 1
# 
# data = pd.concat([idx_df,raw_df],axis=1)
# data_clean = data[data["d"]==1].reset_index()
# dist_df = pd.read_pickle(f'{meeting_ckpt}tpdist.pkl')
# 
# full_data = pd.concat([data_clean,dist_df],axis=1)
# full_data.drop(columns=["content"],inplace=True)
# 
# full_data["date"] = full_data["start_date"]
# full_data.to_stata(f"{DATAPATH}/full_results/{MEEETDATA}.dta",convert_dates={"date":"td"})
# full_data.to_pickle(f"{DATAPATH}/full_results/{MEEETDATA}.pkl")
# 
# ### MEETING SAMPLED ###
# 
# # Retrieve raw data
# raw_df  = pd.read_pickle(f"raw_data/{MEETDATASAMPLE}.pkl")
# idx_df = pd.read_pickle(f'{OUTPATH}/{MEETDATASAMPLE}/original_indices.pkl')
# idx_df = idx_df.set_index(0)
# idx_df["d"] = 1
# 
# data = pd.concat([idx_df,raw_df],axis=1)
# data_clean = data[data["d"]==1].reset_index()
# dist_df = pd.read_pickle(f'{meeting_ckptsampled}tpdist.pkl')
# 
# full_data = pd.concat([data_clean,dist_df],axis=1)
# full_data.drop(columns=["content"],inplace=True)
# full_data.rename(columns=dict(zip([i for i in range(10)],[f"topic_{i}" for i in range(10)])),inplace=True)
# full_data["date"] = pd.to_datetime(full_data["date"])
# full_data.to_stata(f"{DATAPATH}/full_results/{MEETDATASAMPLE}.dta",convert_dates={"date":"td"})
# full_data.to_pickle(f"{DATAPATH}/full_results/{MEETDATASAMPLE}.pkl")
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
# =============================================================================
# # =============================================================================
# # ## #3  Get Pre-Trained Word Embeddings
# 
# sel_mod = "glove-wiki-gigaword-300"
# glove_vectors = gensim.downloader.load(sel_mod)
# 
# with open(f'{DATAPATH}/data/{SPEAKERDATA}/vocab.pkl', 'rb') as f:
#      vocab = pickle.load(f)
# 
# # Write the embeddings to a file
# with open(f"{DATAPATH}/embeddings/{EMBDATASET}_pre", 'w') as f:
#     for v in glove_vectors.index_to_key:
#         if v in vocab:
#             vec = list(glove_vectors[v])
#             f.write(v + ' ')
#             vec_str = ['%.9f' % val for val in vec]
#             vec_str = " ".join(vec_str)
#             f.write(vec_str + '\n')
# 
# with open(f'{DATAPATH}/data/{MEEETDATA}/vocab.pkl', 'rb') as f:
#      vocab = pickle.load(f)
# 
# # Write the embeddings to a file
# with open(f"{DATAPATH}/embeddings/{MEEETDATA}_pre", 'w') as f:
#     for v in glove_vectors.index_to_key:
#         if v in vocab:
#             vec = list(glove_vectors[v])
#             f.write(v + ' ')
#             vec_str = ['%.9f' % val for val in vec]
#             vec_str = " ".join(vec_str)
#             f.write(vec_str + '\n')
# print("*" * 80)
# print(f"Embeddings Extracted")
# print("*" * 80)
# print("\n\n")
# =============================================================================


# =============================================================================
# ## MEETINGS - Pre-Trained Emb. - Sample 
# MEETDATASAMPLE = f"{MEEETDATA}sampled"
# nr_topics = 10
# meeting_ckptsampled = etm(f"{MEETDATASAMPLE}",data_path=f"{DATAPATH}/data/{MEETDATASAMPLE}",
#         emb_path=f"{DATAPATH}/embeddings/{EMBDATASET}_emb",save_path=f"{DATAPATH}/results",
#         batch_size = 1000, epochs = 1000, num_topics = nr_topics, rho_size = 300,
#         emb_size = 300, t_hidden_size = 800, theta_act = 'relu',
#         train_embeddings = 0,  lr = 0.005,  lr_factor=4.0,
#         mode = 'train', optimizer = 'adam',
#         seed = 2019, enc_drop = 0.0, clip = 0.0,
#         nonmono = 10, wdecay = 1.2e-6, anneal_lr = 0, bow_norm = 1,
#         num_words = 15, log_interval = 2, visualize_every = 100, eval_batch_size = 1000,
#         load_from = "", tc = 1, td = 1)
# 
# print(f"Evaluate model: {meeting_ckptsampled}")
# etm(f"{MEETDATASAMPLE}",data_path=f"{DATAPATH}/data/{MEETDATASAMPLE}",
#     emb_path=f"{DATAPATH}/embeddings/{EMBDATASET}_emb",save_path=f"{DATAPATH}/results",
#         mode = 'eval', load_from = f"{meeting_ckptsampled}", train_embeddings = 0 ,tc = 1, td = 1,num_topics = nr_topics)
# 
# print(f"Output the topic distribution: {meeting_ckptsampled}")
# etm(f"{MEETDATASAMPLE}",data_path=f"{DATAPATH}/data/{MEETDATASAMPLE}",
#     emb_path=f"{DATAPATH}/embeddings/{EMBDATASET}_emb",save_path=f"{DATAPATH}/results",
#         mode = 'retrieve',load_from = f"{meeting_ckptsampled}", train_embeddings = 0,num_topics = nr_topics)
# 
# =============================================================================

# =============================================================================
# ## TRANSCRIPTS - Pre-Trained Emb.
# 
# ts_ckpt = etm(f"{TSDATA}",data_path=f"{DATAPATH}/data/{TSDATA}",
#         emb_path=f"{DATAPATH}/embeddings/{EMBDATASET}_emb",save_path=f"{DATAPATH}/results",
#         batch_size = 1000, epochs = 1000, num_topics = 10, rho_size = 300,
#         emb_size = 300, t_hidden_size = 800, theta_act = 'relu',
#         train_embeddings = 0,  lr = 0.005,  lr_factor=4.0,
#         mode = 'train', optimizer = 'adam',
#         seed = 2019, enc_drop = 0.0, clip = 0.0,
#         nonmono = 10, wdecay = 1.2e-6, anneal_lr = 0, bow_norm = 1,
#         num_words =10, log_interval = 2, visualize_every = 10, eval_batch_size = 1000,
#         load_from = "", tc = 1, td = 1)
# 
# print(f"Evaluate model: {ts_ckpt}")
# etm(f"{TSDATA}",data_path=f"{DATAPATH}/data/{TSDATA}",
#     emb_path=f"{DATAPATH}/embeddings/{EMBDATASET}_emb",save_path=f"{DATAPATH}/results",
#         mode = 'eval', load_from = f"{ts_ckpt}", train_embeddings = 0 ,num_topics = 10,tc = 1, td = 1)
# 
# print(f"Output the topic distribution: {ts_ckpt}")
# etm(f"{TSDATA}",data_path=f"{DATAPATH}/data/{TSDATA}",
#     emb_path=f"{DATAPATH}/embeddings/{EMBDATASET}_emb",save_path=f"{DATAPATH}/results",
#         mode = 'retrieve',load_from = f"{ts_ckpt}", train_embeddings = 0,num_topics = 10)
# =============================================================================
# =============================================================================
# ts_phrase_itera = 2 
# ts_threshold = "inf"
# ts_max_df= 1.0
# ts_min_df = 10
# TSDATA = f"TS_min{meetmin_df}_max{meetmax_df}_iter{meetphrase_itera}_th{meetthreshold}"
# build_transcriptdata(ts_max_df,ts_min_df,ts_phrase_itera,ts_threshold,TSDATA) 
# =============================================================================
# =============================================================================
# speakerphrase_itera = 2 # Number o fphrase iterations
# speakerthreshold = "inf" # Threshold value for collocations. If "inf": no collocations
# speakermax_df = 0.7 
# speakermin_df = 10
# SPEAKERDATA = f"SPEAKERS_min{speakermin_df}_max{speakermax_df}_iter{speakerphrase_itera}_th{speakerthreshold}"
# build_speakerdata(speakermax_df,speakermin_df,speakerphrase_itera,speakerthreshold,SPEAKERDATA)
# =============================================================================
