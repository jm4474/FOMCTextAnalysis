from IPython import get_ipython
get_ipython().magic('reset -sf')

import os, shutil
import re
import csv
import timeit
import pandas as pd
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
import matplotlib
import matplotlib.pyplot as plt
import random
random.seed(2019)
from utils import bigrams, trigram, replace_collocation

# =============================================================================

STATEMENT_PATH = os.path.expanduser("~/Dropbox/MPCounterfactual/src/derivation/python/output/")
TRANSCRIPT_PATH = os.path.expanduser("~/Dropbox/MPCounterfactual/src/collection/python/output/transcript_raw_text")
BB_PATH = os.path.expanduser("~/Dropbox/MPCounterfactual/src/collection/python/output/bluebook_raw_text")
OUTPATH = os.path.expanduser("~/Dropbox/MPCounterfactual/src/etm/data")        
SPEAKER_PATH = os.path.expanduser("~/Dropbox/MPCounterfactual/src/analysis/python/output")        
ECONDATA = os.path.expanduser("~/Dropbox/MPCounterfactual/src/economic_data")
PROJECTPATH = os.path.expanduser("~/Dropbox/MPCounterfactual/src/etm")

# =============================================================================


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
                #print("No split")
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
    #print("Transcripts processed. Time: {}".format(end - start))    
      
    docs = raw_text.groupby('Date')['content'].sum().to_list()
    return docs,raw_text


def digit_count(line,digits=10):
    numbers = sum(c.isdigit() for c in line)
    boo = numbers> digits
    return boo


def preprocess_longdocs():
    MONTHS = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"]
    short_months = re.compile("(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec) ?\. ?")
    nums3 = re.compile("^\(?[\+|\-]?\s?\d+\.?\,?\d*\.?\d*\)?")
    nums2 = re.compile('^[- \d\.,p\*†]+$')
    nums = re.compile('^ ?(\w )+\w?$')
    num = re.compile('^-?\d+[\.,]?\d*[\.,]?\d+$')
    #sum_suffix = re.compile('( -?\d+\.?\d*[\w%]?){2,}$')
    num_sep = re.compile('[-\d,\.]+ --- [-\d,\.]+ .*[\d%]$')
    rd  = re.compile('\n\n *recent ?.?d ?evelc?op?me?nts?.? *1?\n.?[\(\n]')
    pre  = re.compile('ocr process and were not checked or corrected by staff',re.MULTILINE)
    ir = re.compile('\n(for immediate release)|(for release at \d:\d+).*\n')
    qiv = re.compile('^\(?(\d* ?\-)? ?qiv')
    conf = re.compile('^confidential\s*\(fr\)')
    last = re.compile("^content[\\n]?\s?last[\\n]?\s?modified[\\n]?\s?\d+\/\d+\/\d+")
    
    files = [file for file in sorted(os.listdir(BB_PATH)) if file!=".DS_Store"]
    
    docs = []
    docdates = []
    
    for fidx, infile in enumerate(files):
        if os.path.isfile(os.path.join(BB_PATH, infile)):
            #print("{}\t{}".format(fidx, infile))
            with open(os.path.join(BB_PATH, infile), 'r') as inf:
                content = inf.read()
            try:
                content = re.split(rd, content.lower())[1]
            except:
                content = content.lower()         
            try:
                content = re.split(pre, content)[1]
            except:
                content = content
              
            docdates.append(infile[:10])
           
            newlines = []
            #content = re.sub(r'-\n\s*', '', content) # remove '-' from words that are split at newlines (very low precision, high recall) not done currently
            for idx,line in enumerate(content.split('\n')):
                #print(idx)
                #if idx%1000==999:
                    #print(idx)
                line=line.strip().strip(" *")
                line = re.sub("___+", "", line)
                line = re.sub("p - preliminar", "", line)
                
                if not (len(line) < 3 or nums2.match(line.strip("*").strip())!= None 
                    or nums.match(line.strip("*").strip())!= None
                    or (num.match(line.split()[0].strip("*").strip())!= None and num.match(line.split()[-1].strip("*").strip())!= None)
                    or line.lower().strip() in MONTHS 
                    or re.search(short_months, line.lower()) 
                    or re.search(conf, line.strip()) 
                    or re.search(num_sep, line.lower())
                    or re.search(nums3, line.strip())
                    or re.search(qiv, line)
                    or re.search(last, line)
                    or digit_count(line)):
                    newlines.append(line)             
            docs.append(' '.join(newlines))
    #print("Bluebooks processed")
    return docs,docdates
    
def contains_punctuation(w):
    return any(char in string.punctuation for char in w)

def contains_numeric(w):
    return any(char.isdigit() for char in w)

def remove_empty(in_docs,docindex=[], doctype=""):
    newdocs = [doc for doc in in_docs if doc!=[]]        
    newindex = []
    try:
        newindex = [docindex[docidx] for docidx,doc in enumerate(in_docs) if doc!=[]]
    except:
        print("No index given")
    if len(newdocs) != len(newindex):
        raise Exception("Length of index and data does not match") 
    if doctype == "test":
    # Remove test documents with length=1
        newdocs = [doc for doc in newdocs if len(doc)>1]
        testindex = []
        try:
            testindex = [newindex[docidx] for docidx,doc in enumerate(newdocs) if doc!=[]]
        except:
            print("No index given")
        if len(newdocs) != len(testindex):
            raise Exception("Length of index and data does not match") 
        newindex = testindex
    return newdocs,newindex
    
def data_preprocess(docs,docindex,data,DATASET,max_df,min_df):
    print("\n"+"*"*80)
    init_docs = docs.to_list()
    
    # Create count vectorizer
    print('counting document frequency of words...')
    cvectorizer = CountVectorizer(min_df=min_df, max_df=max_df, stop_words=None)
    cvz = cvectorizer.fit_transform(init_docs).sign()
    
    # Get vocabulary
    print('building the vocabulary...')
    sum_counts = cvz.sum(axis=0)
    v_size = sum_counts.shape[1]
    sum_counts_np = np.zeros(v_size, dtype=int)
    for v in range(v_size):
        sum_counts_np[v] = sum_counts[0,v]
    word2id = dict([(w, cvectorizer.vocabulary_.get(w)) for w in cvectorizer.vocabulary_])
    id2word = dict([(cvectorizer.vocabulary_.get(w), w) for w in cvectorizer.vocabulary_])
    del cvectorizer
    print('vocabulary size: {}'.format(len(list(set(" ".join(init_docs).split())))))  
    # Sort elements in vocabulary
    idx_sort = np.argsort(sum_counts_np)
    vocab_aux = [id2word[idx_sort[cc]] for cc in range(v_size)]  
    # Filter out stopwords (if any)
    print('vocabulary size after removing stopwords from list: {}'.format(len(vocab_aux)))
    
    # Create dictionary and inverse dictionary
    vocab = vocab_aux
    del vocab_aux
    word2id = dict([(w, j) for j, w in enumerate(vocab)])
    id2word = dict([(j, w) for j, w in enumerate(vocab)])
    
    # Split in train/test/valid
    print('tokenizing documents and splitting into train/test/valid...')
    num_docs = cvz.shape[0]
    trSize = int(np.floor(0.85*num_docs))
    tsSize = int(np.floor(0.10*num_docs))
    vaSize = int(num_docs - trSize - tsSize)
    del cvz
    idx_permute = np.random.permutation(num_docs).astype(int)
    
    # Remove words not in train_data
    vocab = list(set([w for idx_d in range(trSize) for w in docs[idx_permute[idx_d]].split() if w in word2id]))
    word2id = dict([(w, j) for j, w in enumerate(vocab)])
    id2word = dict([(j, w) for j, w in enumerate(vocab)])
    print('  vocabulary after removing words not in train: {}'.format(len(vocab)))
    
    docs_all = [[word2id[w] for w in init_docs[idx_d].split() if w in word2id] for idx_d in range(num_docs)]    
    docs_tr = [[word2id[w] for w in init_docs[idx_permute[idx_d]].split() if w in word2id] for idx_d in range(trSize)]
    docs_ts = [[word2id[w] for w in init_docs[idx_permute[idx_d+trSize]].split() if w in word2id] for idx_d in range(tsSize)]
    docs_va = [[word2id[w] for w in init_docs[idx_permute[idx_d+trSize+tsSize]].split() if w in word2id] for idx_d in range(vaSize)]
    
    print('  number of documents: {} [this should be equal to {}]'.format(len(docs_all), num_docs))
    print('  number of documents (train): {} [this should be equal to {}]'.format(len(docs_tr), trSize))
    print('  number of documents (test): {} [this should be equal to {}]'.format(len(docs_ts), tsSize))
    print('  number of documents (valid): {} [this should be equal to {}]'.format(len(docs_va), vaSize))
    
    idx_all= [idx_permute[idx_d] for idx_d in range(num_docs)]    
    idx_tr = [idx_permute[idx_d] for idx_d in range(trSize)]
    idx_ts = [idx_permute[idx_d] for idx_d in range(tsSize)]
    idx_va = [idx_permute[idx_d] for idx_d in range(vaSize)]
        
    # Remove empty documents
    print('removing empty documents...')
    docs_all,idx_all = remove_empty(docs_all, idx_all)
    docs_tr,idx_tr = remove_empty(docs_tr, idx_tr)
    docs_ts,idx_ts = remove_empty(docs_ts, idx_ts, doctype = "test")
    docs_va,idx_va = remove_empty(docs_va, idx_va)
    
    # Split test set in 2 halves
    print('splitting test documents in 2 halves...')
    docs_ts_h1 = [[w for i,w in enumerate(doc) if i<=len(docs_ts)/2.0-1] for doc in docs_ts]
    docs_ts_h2 = [[w for i,w in enumerate(doc) if i>len(docs_ts)/2.0-1] for doc in docs_ts]
    
    idx_ts_h1 = [i for idx,i in enumerate(idx_ts) if idx <= len(idx_ts)/2.0-1]
    idx_ts_h2 = [i for idx,i in enumerate(idx_ts) if idx > len(idx_ts)/2.0-1]
    
    # Getting lists of words and doc_indices
    print('creating lists of words...')
    
    def create_list_words(in_docs):
        return [x for y in in_docs for x in y]
    
    words_all = create_list_words(docs_all)
    words_tr = create_list_words(docs_tr)
    words_ts = create_list_words(docs_ts)
    words_ts_h1 = create_list_words(docs_ts_h1)
    words_ts_h2 = create_list_words(docs_ts_h2)
    words_va = create_list_words(docs_va)
    
    print('  len(words_tr): ', len(words_all))
    print('  len(words_tr): ', len(words_tr))
    print('  len(words_ts): ', len(words_ts))
    print('  len(words_ts_h1): ', len(words_ts_h1))
    print('  len(words_ts_h2): ', len(words_ts_h2))
    print('  len(words_va): ', len(words_va))
    
    # Get doc indices
    print('getting doc indices...')
    
    def create_doc_indices(in_docs):
        aux = [[j for i in range(len(doc))] for j, doc in enumerate(in_docs)]
        return [int(x) for y in aux for x in y]
    
    doc_indices_all = create_doc_indices(docs_all)
    doc_indices_tr = create_doc_indices(docs_tr)
    doc_indices_ts = create_doc_indices(docs_ts)
    doc_indices_ts_h1 = create_doc_indices(docs_ts_h1)
    doc_indices_ts_h2 = create_doc_indices(docs_ts_h2)
    doc_indices_va = create_doc_indices(docs_va)
    
    print('  len(np.unique(doc_indices_all)): {} [this should be {}]'.format(len(np.unique(doc_indices_all)), len(docs_all)))
    print('  len(np.unique(doc_indices_tr)): {} [this should be {}]'.format(len(np.unique(doc_indices_tr)), len(docs_tr)))
    print('  len(np.unique(doc_indices_ts)): {} [this should be {}]'.format(len(np.unique(doc_indices_ts)), len(docs_ts)))
    print('  len(np.unique(doc_indices_ts_h1)): {} [this should be {}]'.format(len(np.unique(doc_indices_ts_h1)), len(docs_ts_h1)))
    print('  len(np.unique(doc_indices_ts_h2)): {} [this should be {}]'.format(len(np.unique(doc_indices_ts_h2)), len(docs_ts_h2)))
    print('  len(np.unique(doc_indices_va)): {} [this should be {}]'.format(len(np.unique(doc_indices_va)), len(docs_va)))
    
    # Number of documents in each set
    n_docs_all = len(docs_all)
    n_docs_tr = len(docs_tr)
    n_docs_ts = len(docs_ts)
    n_docs_ts_h1 = len(docs_ts_h1)
    n_docs_ts_h2 = len(docs_ts_h2)
    n_docs_va = len(docs_va)
    
    # Remove unused variables
    del docs_tr
    del docs_ts
    del docs_ts_h1
    del docs_ts_h2
    del docs_va
    
    # Save vocabulary to file
    path_save = f'{OUTPATH}/{DATASET}/'
    if not os.path.isdir(path_save):
        os.system('mkdir -p ' + path_save)
    #print("money" in vocab)    
    with open(path_save + 'vocab.pkl', 'wb') as f:
        pickle.dump(vocab, f)
        
    # Save corpus
    corpus = [[w for w in doc.split(' ') ]for doc in docs.to_list()]
    with open(path_save + 'corpus.pkl', 'wb') as f:
        pickle.dump(corpus, f)
        

    # Create covariates
    if not isinstance(data, type(None)):
        print('create covariates...')
        data_all = data.iloc[idx_all]
        data_tr = data.iloc[idx_tr]
        data_ts = data.iloc[idx_ts]
        data_va = data.iloc[idx_va]
        data_ts_h1 = data.iloc[idx_ts_h1]
        data_ts_h2 = data.iloc[idx_ts_h1]
                
        data_all.to_pickle(f"{path_save}/data_all.pkl")
        data_tr.to_pickle(f"{path_save}/data_tr.pkl")
        data_ts.to_pickle(f"{path_save}/data_ts.pkl")
        data_va.to_pickle(f"{path_save}/data_va.pkl")
        data_ts_h1.to_pickle(f"{path_save}/data_ts_h1.pkl")
        data_ts_h2.to_pickle(f"{path_save}/data_ts_h2.pkl")
        
    # Create bow representation
    print('creating bow representation...')
    
    def create_bow(doc_indices, words, n_docs, vocab_size):
        return sparse.coo_matrix(([1]*len(doc_indices),(doc_indices, words)), shape=(n_docs, vocab_size)).tocsr()
    
    bow_all = create_bow(doc_indices_all, words_all, n_docs_all, len(vocab))
    bow_tr = create_bow(doc_indices_tr, words_tr, n_docs_tr, len(vocab))
    bow_ts = create_bow(doc_indices_ts, words_ts, n_docs_ts, len(vocab))
    bow_ts_h1 = create_bow(doc_indices_ts_h1, words_ts_h1, n_docs_ts_h1, len(vocab))
    bow_ts_h2 = create_bow(doc_indices_ts_h2, words_ts_h2, n_docs_ts_h2, len(vocab))
    bow_va = create_bow(doc_indices_va, words_va, n_docs_va, len(vocab))
    
    del words_tr
    del words_ts
    del words_ts_h1
    del words_ts_h2
    del words_va
    del doc_indices_tr
    del doc_indices_ts
    del doc_indices_ts_h1
    del doc_indices_ts_h2
    del doc_indices_va
    del vocab
    
    # Split bow into token/value pairs
    print('splitting bow into token/value pairs and saving to disk...')
    
    def split_bow(bow_in, n_docs):
        indices = [[w for w in bow_in[doc,:].indices] for doc in range(n_docs)]
        counts = [[c for c in bow_in[doc,:].data] for doc in range(n_docs)]
        return indices, counts
    
    bow_all_tokens, bow_all_counts = split_bow(bow_all, n_docs_all)
    savemat(path_save + 'bow_all_tokens.mat', {'tokens': bow_all_tokens}, do_compression=True)
    savemat(path_save + 'bow_all_counts.mat', {'counts': bow_all_counts}, do_compression=True)
    del bow_all
    del bow_all_tokens
    del bow_all_counts
    
    bow_tr_tokens, bow_tr_counts = split_bow(bow_tr, n_docs_tr)
    savemat(path_save + 'bow_tr_tokens.mat', {'tokens': bow_tr_tokens}, do_compression=True)
    savemat(path_save + 'bow_tr_counts.mat', {'counts': bow_tr_counts}, do_compression=True)
    del bow_tr
    del bow_tr_tokens
    del bow_tr_counts
    
    bow_ts_tokens, bow_ts_counts = split_bow(bow_ts, n_docs_ts)
    savemat(path_save + 'bow_ts_tokens.mat', {'tokens': bow_ts_tokens}, do_compression=True)
    savemat(path_save + 'bow_ts_counts.mat', {'counts': bow_ts_counts}, do_compression=True)
    del bow_ts
    del bow_ts_tokens
    del bow_ts_counts
    
    bow_ts_h1_tokens, bow_ts_h1_counts = split_bow(bow_ts_h1, n_docs_ts_h1)
    savemat(path_save + 'bow_ts_h1_tokens.mat', {'tokens': bow_ts_h1_tokens}, do_compression=True)
    savemat(path_save + 'bow_ts_h1_counts.mat', {'counts': bow_ts_h1_counts}, do_compression=True)
    del bow_ts_h1
    del bow_ts_h1_tokens
    del bow_ts_h1_counts
    
    bow_ts_h2_tokens, bow_ts_h2_counts = split_bow(bow_ts_h2, n_docs_ts_h2)
    savemat(path_save + 'bow_ts_h2_tokens.mat', {'tokens': bow_ts_h2_tokens}, do_compression=True)
    savemat(path_save + 'bow_ts_h2_counts.mat', {'counts': bow_ts_h2_counts}, do_compression=True)
    del bow_ts_h2
    del bow_ts_h2_tokens
    del bow_ts_h2_counts
    
    bow_va_tokens, bow_va_counts = split_bow(bow_va, n_docs_va)
    savemat(path_save + 'bow_va_tokens.mat', {'tokens': bow_va_tokens}, do_compression=True)
    savemat(path_save + 'bow_va_counts.mat', {'counts': bow_va_counts}, do_compression=True)
    del bow_va
    del bow_va_tokens
    del bow_va_counts
    
    print(f'{DATASET} ready !!')
    print('*' * 80)

def statements_raw():
    data = pd.read_csv(f"{STATEMENT_PATH}/statements_text_extraction.csv")
    docs = data["statement"].to_list()
    docdates = data["meeting_end_date"].to_list()
    print("Statements processed")
    return docs,docdates

def word_count(df,name):
    df["date"] = pd.to_datetime(df["date"])
    df["year"] = df["date"].dt.year
    
    df_year = df.groupby(['year'])["content"].agg(lambda x: ' '.join(x)).reset_index()["content"]
    df_year_date = df.groupby(['year'])["content"].agg(lambda x: ' '.join(x)).reset_index()['year'].to_list()
    df_year = data_clean(df_year,df_year.index)

    # produce doc stats
    token_counts_yr = [len(doc) for doc in df_year["cleaned_content"].to_list()]
    fig, ax = plt.subplots()
    ax.plot(df_year_date,token_counts_yr)
    plt.savefig(f"{PROJECTPATH}/output/{name}_yearly.png")

    df_date = df.groupby(['date'])["content"].agg(lambda x: ' '.join(x)).reset_index()["content"]
    df_date_date = df.groupby(['date'])["content"].agg(lambda x: ' '.join(x)).reset_index()['date'].to_list()
    df_date = data_clean(df_date,df_date.index)

    # produce doc stats
    token_counts = [len(doc) for doc in df_date["cleaned_content"].to_list()]
    del ax
    del fig
    fig, ax = plt.subplots()
    df_date_date = [np.datetime64(dat) for dat in df_date_date]
    ax.plot(df_date_date,token_counts)
    plt.savefig(f"{PROJECTPATH}/output/{name}_mymeeting.png")
    plt.suptitle(name)
    return df_year, token_counts_yr        

def build_embdata(max_df,min_df,phrase_itera,threshold,DATASET):
    bb_docs,docdates = preprocess_longdocs() 
    bb_df = pd.DataFrame(zip(docdates,bb_docs),columns=["date","content"])
    word_count(bb_df,"bluebook")
    
    transcript_docs,raw_text = generate_rawtranscripts()
    transcripts_pr = raw_text.groupby(['Date'])["content"].agg(lambda x: ' '.join(x)).reset_index()["content"].to_list()
    transcripts_dates = raw_text.groupby(['Date'])["content"].agg(lambda x: ' '.join(x)).reset_index()['Date'].to_list()
    transcript_df = pd.DataFrame(zip(transcripts_dates,transcripts_pr),columns=["date","content"])
    word_count(transcript_df,"transcript")
        
    statement_docs,docdates = statements_raw()
    statement_df = pd.DataFrame(zip(docdates,statement_docs),columns=["date","content"])
    word_count(statement_df,"statements")
    
    if not os.path.exists(f"{OUTPATH}/{DATASET}"):
        os.makedirs(f"{OUTPATH}/{DATASET}")
        
    docs = bb_docs + transcript_docs + statement_docs
    
    df_cleancontent = data_clean(pd.Series(docs),pd.Series(docs).index)
    
    data_preprocess(df_cleancontent['cleaned_content'],
                    df_cleancontent.index,None,DATASET,max_df,min_df)
    
def sampling(dfraw , max_words = 80000):
    df = pd.DataFrame(dfraw) 
    df["year"]  = df.index.get_level_values("start_date").year
    
    df_year = df.groupby(["year"])["cleaned_content"].agg(lambda x: ' '.join(x)).reset_index()["cleaned_content"].to_list()
    df_year_date = df.groupby(["year"])["cleaned_content"].agg(lambda x: ' '.join(x)).reset_index()['year'].to_list()
    
    token_counts_yr = [len(doc.split(" ")) for doc in df_year]

    fig, ax = plt.subplots()
    ax.plot(df_year_date,token_counts_yr)    
    # Sampling probailities by year
    
    sampling_pr = {}
    for idx,yr in enumerate(df_year_date):
        sampling_pr.update({yr:min(1,max_words/token_counts_yr[idx])})
        
    meeting_text = [txt.split(" ") for txt in df["cleaned_content"].to_list()]
    meeting_years = df['year'].to_list()
    meeting_dates = list(df.index.get_level_values("start_date"))

    meeting_text = [random.sample(txt, int(len(txt) * sampling_pr[meeting_years[idx]]) ) for idx,txt in enumerate(meeting_text)]
    meeting_cnts = [len(txt) for txt in meeting_text]
    meeting_text = [" ".join(meeting_text[doc]) for doc in range(len(meeting_text))] # joins words in doc
    
    df_cts = pd.DataFrame(zip(meeting_years,meeting_cnts),columns=["year","cnts"]).groupby("year")["cnts"].sum()
    df_cts.plot()

    return pd.DataFrame(meeting_text,columns=["sampled_content"],index=df.index) 

def data_clean(rawdocs,doc_index,th="inf",phrase_itera=2):
    docs = rawdocs.to_list()
    
    # Tokenize the documents
    init_docs = [re.findall(r'''[\w']+|[.,!?;-~{}`´_<=>:/@*()&'$%#"]''', doc) for doc in docs]
    init_docs = [[w.lower() for w in init_docs[doc] if not contains_punctuation(w)] for doc in range(len(init_docs))] # removes punct and makes lower case.
    init_docs = [[w for w in init_docs[doc] if not contains_numeric(w)] for doc in range(len(init_docs))]  # removes numeric
    init_docs = [[w for w in init_docs[doc] if len(w)>1] for doc in range(len(init_docs))] # removes single character
    
    '''
    # Create collocations
    if str(th) == "inf":
        pass
    else:
        for i in range(phrase_itera):
            print(f"Phrase iteration: {i+1}")
            phrases = Phrases(init_docs, min_count=1, threshold=th, connector_words=ENGLISH_CONNECTOR_WORDS)
            init_docs = [phrases[sent] for sent in init_docs]
            del phrases
    '''
    # Read stopwords
    with open('/Users/olivergiesecke/Dropbox/MPCounterfactual/src/etm/stops.txt', 'r') as f:
        stops = f.read().split('\n')
    
    # Add specific stopwords 
    additional_stopword = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september',
                           'october', 'november', 'december',"recessed","laugther","reception","dinner","martin","terrace",
                           "memo","memos","ll","don","panel","appendix","left","shown","chairman","president","chair","brian",
                           "moskow","guynn","mr","madam","blue","red","roll","california",'pianalto', 'poole', 'warsh',
                           'bernanke', 'hoenig', 'duke', 'bies',"laughter","handout","line",'williams',"unintelligible","lorie"]
    
    additional_stopword = additional_stopword + [w[:3] for w in additional_stopword]
    firstname = pd.read_excel(f'{PROJECTPATH}/util_files/firstnames.xlsx')
    firstname_list = firstname['First name'].dropna().values
    for firstname in firstname_list:
        additional_stopword.append(firstname.lower())
    stops = stops + additional_stopword
    init_docs = [[w for w in init_docs[doc] if w not in stops] for doc in range(len(init_docs))]
    init_docs = [" ".join(init_docs[doc]) for doc in range(len(init_docs))] # joins words in doc
    
    if len(init_docs) != len(doc_index):
        raise Exception("Length of index and data does not match")
    
    output_df = pd.DataFrame(init_docs,columns=["cleaned_content"],index=doc_index)
    return output_df

def build_meeting(max_df,min_df,phrase_itera,threshold,DATASET):
    # Pre-process
    link = pd.read_csv(f"{STATEMENT_PATH}/meeting_derived_file.csv")[['start_date', 'end_date',"event_type"]].drop_duplicates()
    for col in ['start_date', 'end_date']:
        link[col] = pd.to_datetime(link[col])
        
    speakers_full = pd.read_pickle(f"{SPEAKER_PATH}/speaker_data_full.pkl")    
    econdata = pd.read_pickle(f"{ECONDATA}/final_data/econmarketdata.pkl")
    MS_text = speakers_full.groupby(["start_date",'Section'])["content"].agg(lambda x: ' '.join(x)).reset_index()
    MS_text = MS_text.merge(link,left_on = 'start_date', right_on = 'start_date',how = "left" )
    MS_data = MS_text.merge(econdata,left_on="start_date",right_on="date",how="left") 
    
    MS_data.drop(columns="date",inplace=True)
    MS_data.set_index(["start_date","Section"],inplace=True)
    df_cleancontent = data_clean(MS_data["content"],MS_data.index)
    MS_cleaned = pd.concat([MS_data,df_cleancontent], axis = 1)
    MS_cleaned.drop(columns="content",inplace=True)
       
    # Do sampling
    part1 = MS_cleaned.loc[MS_cleaned.index.get_level_values("Section")==1,"cleaned_content"]
    part1_sampled = sampling(part1,max_words = 80000)
   
    part2 = MS_cleaned.loc[MS_cleaned.index.get_level_values("Section")==2,"cleaned_content"]
    part2_sampled = sampling(part2,max_words = 30000)
    
    MS_cleanedsampled = pd.concat([MS_cleaned, part1_sampled], axis=1).rename(columns={"sampled_content":"sampled_content1"})
    MS_cleanedsampled = pd.concat([MS_cleanedsampled, part2_sampled], axis=1).rename(columns={"sampled_content":"sampled_content2"})
    MS_cleanedsampled["sampled_content"] = MS_cleanedsampled["sampled_content1"]
    MS_cleanedsampled["sampled_content"].update(MS_cleanedsampled["sampled_content2"])
    MS_cleanedsampled.drop(columns=["sampled_content1","sampled_content2"],inplace=True)
    
    
    statements_df = pd.read_csv(f"{STATEMENT_PATH}/statements_text_extraction.csv")[['meeting_end_date','release_date', 'statement']]
    for col in ['meeting_end_date','release_date']:
        statements_df[col] = pd.to_datetime(statements_df[col])
    statements_df = statements_df.merge(link,left_on = 'meeting_end_date', right_on = 'end_date',how = "left" )
    statements_df.loc[:,"Section"] = 3
    statements_df.drop(columns = ["meeting_end_date"],inplace=True)
    statements_df  = statements_df.merge(econdata,left_on="start_date",right_on="date",how="left") 
    statements_df.set_index(["start_date","Section"],inplace=True)
    df_cleancontent = data_clean(statements_df["statement"],statements_df.index)
    df_cleancontent["sampled_content"] = df_cleancontent["cleaned_content"].apply(common_phrase)
    stat_clean_df = pd.concat([df_cleancontent,statements_df.drop(columns = "statement") ],axis=1)
    stat_clean_df.drop(columns="date",inplace=True)
    
    fulldata = pd.concat([MS_cleanedsampled,stat_clean_df],axis=0)
    
    
    # Do cleaning
    if not os.path.exists(f"{OUTPATH}/{DATASET}"):
        os.makedirs(f"{OUTPATH}/{DATASET}")    
    fulldata.to_pickle(f"{OUTPATH}/{DATASET}/rawdata.pkl")
     
    colsel = ['SVENY01','d28_SVENY01','SVENY10','d14_SVENY10',
              'AAA10Y', 'BAA10Y','d28_AAA10Y', 'd28_BAA10Y',
              'spindx', 'vwretx', 'vwindx', 'TEDRATE', 'EQUITYCAPE', 
              'd_UNRATE', 'l1d_UNRATE', 'l2d_UNRATE',
              'dln_INDPRO', 'l1dln_INDPRO', 'l2dln_INDPRO',
              'dln_PCEPI', 'l1dln_PCEPI', 'l2dln_PCEPI', 
              'd14ln_spindx', 'd28ln_spindx', 'd7ln_spindx', 
              'd14ln_vwindx', 'd28ln_vwindx', 'd7ln_vwindx']
    
    data_preprocess(fulldata['sampled_content'],
                    fulldata.index,
                    fulldata[colsel],
                    f"{DATASET}",max_df,min_df)
    
def build_speaker(max_df,min_df,phrase_itera,threshold,DATASET):
    # Pre-process
    link = pd.read_csv(f"{STATEMENT_PATH}/meeting_derived_file.csv")[['start_date', 'end_date',"event_type"]].drop_duplicates()
    for col in ['start_date', 'end_date']:
        link[col] = pd.to_datetime(link[col])
        
    speakers_full = pd.read_pickle(f"{SPEAKER_PATH}/speaker_data_full.pkl")    
    econdata = pd.read_pickle(f"{ECONDATA}/final_data/econmarketdata.pkl")
    speakers_full = speakers_full.merge(link,left_on = 'start_date', right_on = 'start_date',how = "left" )
    MS_data = speakers_full.merge(econdata,left_on="start_date",right_on="date",how="left") 
    
    MS_data.drop(columns="date",inplace=True)
    MS_data.set_index(["start_date","Section"],inplace=True)
    df_cleancontent = data_clean(MS_data["content"],MS_data.index)
    MS_cleaned = pd.concat([MS_data,df_cleancontent], axis = 1)
    MS_cleaned.drop(columns="content",inplace=True)
       
    # Do cleaning
    if not os.path.exists(f"{OUTPATH}/{DATASET}"):
        os.makedirs(f"{OUTPATH}/{DATASET}")    
    MS_cleaned.to_pickle(f"{OUTPATH}/{DATASET}/rawdata.pkl")
     
    colsel = ['SVENY01','d28_SVENY01','SVENY10','d14_SVENY10',
              'AAA10Y', 'BAA10Y','d28_AAA10Y', 'd28_BAA10Y',
              'spindx', 'vwretx', 'vwindx', 'TEDRATE', 'EQUITYCAPE', 
              'd_UNRATE', 'l1d_UNRATE', 'l2d_UNRATE',
              'dln_INDPRO', 'l1dln_INDPRO', 'l2dln_INDPRO',
              'dln_PCEPI', 'l1dln_PCEPI', 'l2dln_PCEPI', 
              'd14ln_spindx', 'd28ln_spindx', 'd7ln_spindx', 
              'd14ln_vwindx', 'd28ln_vwindx', 'd7ln_vwindx']
    
    data_preprocess(MS_cleaned['cleaned_content'],
                    MS_cleaned.index,
                    MS_cleaned[colsel],
                    f"{DATASET}",max_df,min_df)
    
    
def common_phrase(new):
    phrases = ["federal reserve issues fomc statement release share information received",
               "frb press release fomc statement release date release",
               "fomc statement release share information received",
               "frb press release fomc statement board discount rate action release date release"]
    
    for phrase in phrases:
        new = re.sub(f"^{phrase} ","",new)
    
    new = re.sub(f"federal open market committee","",new)
    
    return new
                            
    
def build_statement_data(max_df,min_df,phrase_itera,threshold,DATASET):
    # Pre-process
    statements_df = pd.read_csv(f"{STATEMENT_PATH}/statements_text_extraction.csv")[['release_date', 'statement']]

    statements_df.set_index(["release_date"],inplace=True)
    df_cleancontent = data_clean(statements_df["statement"],statements_df.index)
    df_cleancontent["cleaned_content"] = df_cleancontent["cleaned_content"].apply(common_phrase)
    
    cleaned_statement = df_cleancontent.copy()
    del statements_df, df_cleancontent
    
    # Do cleaning
    if not os.path.exists(f"{OUTPATH}/{DATASET}"):
        os.makedirs(f"{OUTPATH}/{DATASET}")    
    cleaned_statement.to_pickle(f"{OUTPATH}/{DATASET}/rawdata.pkl")
        
    data_preprocess(cleaned_statement['cleaned_content'],cleaned_statement.index,None,f"{DATASET}",max_df,min_df)

     
def build_transcriptdata(max_df,min_df,phrase_itera,threshold,DATASET):
    transcript_docs,raw_text = generate_rawtranscripts()

    if not os.path.exists(f"{OUTPATH}/{DATASET}"):
        os.makedirs(f"{OUTPATH}/{DATASET}")
    data_preprocess(transcript_docs ,DATASET,phrase_itera,max_df,min_df,threshold)
    print(f"{DATASET} complete!")   

    
def main():
    # Maximum / minimum document frequency
    max_df = 1.0 # in a maximum of # % of documents if # is float.
    min_df = 10  # choose desired value for min_df // in a minimum of # documents
    phrase_itera = 2
    threshold = "inf"
    DATASET = f"BBTSST_min{min_df}_max{max_df}_iter{phrase_itera}_th{threshold}"
    build_embdata(max_df,min_df,phrase_itera,threshold,DATASET)

    phrase_itera = 2
    threshold = "inf"
    max_df = 1.0
    min_df = 10
    DATASET = f"MEET_min{min_df}_max{max_df}_iter{phrase_itera}_th{threshold}"
    build_meeting(max_df,min_df,phrase_itera,threshold,DATASET)
    
    
    phrase_itera = 2
    threshold = "inf"
    max_df = 1.0
    min_df = 10
    DATASET = f"SPEAKER_min{min_df}_max{max_df}_iter{phrase_itera}_th{threshold}"
    build_speaker(max_df,min_df,phrase_itera,threshold,DATASET)
    
    #phrase_itera = 2
    #threshold = "inf"
    #max_df = 1.0
    #min_df = 5
    #DATASET = f"STATEMENT_min{min_df}_max{max_df}_iter{phrase_itera}_th{threshold}"
    #build_statement_data(max_df,min_df,phrase_itera,threshold,DATASET)
    
    
if __name__ == "__main__":
    main()
    
    
    