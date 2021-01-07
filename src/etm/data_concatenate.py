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

def generate_rawtranscripts():
    raw_doc = os.listdir(TRANSCRIPT_PATH)  # as above
    filelist = sorted(raw_doc)  # sort the pdfs in order
    onlyfiles = [f for f in filelist if os.path.isfile(os.path.join(TRANSCRIPT_PATH, f))]  # keep if in correct dir

    raw_text = pd.DataFrame([])  # empty dataframe

    start = timeit.default_timer()
    for i, file in enumerate(filelist):
        print('Document {} of {}: {}'.format(i, len(filelist), file))
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
    print("Documents processed. Time: {}".format(end - start))    
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

    for fidx, infile in enumerate(files):
        if os.path.isfile(os.path.join(BB_PATH, infile)):
            print("{}\t{}".format(fidx, infile))
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
    return docs
    
def contains_punctuation(w):
    return any(char in string.punctuation for char in w)

def contains_numeric(w):
    return any(char.isdigit() for char in w)

def separation(raw_text):

    separation_rule = pd.read_excel(os.path.join(UTILFILE_PATH, 'separation_rules.xlsx'), index_col=0)

    FOMC_separation = pd.DataFrame(columns=['Date', 'Speaker', 'content', 'Section'])

    for i in separation_rule.index:
        print('Running for date {}'.format(i))
        temp1 = raw_text[raw_text["Date"] == i].iloc[separation_rule['FOMC1_start'][i]:separation_rule['FOMC1_end'][i]]
        temp1['Section'] = 1
        if separation_rule['FOMC2_end'][i] == 'end':
            temp2 = raw_text[raw_text["Date"] == i].iloc[separation_rule['FOMC2_start'][i]:]
        else:
            temp2 = raw_text[raw_text["Date"] == i].iloc[
                    separation_rule['FOMC2_start'][i]:separation_rule['FOMC2_end'][i]]
        temp2['Section'] = 2
        FOMC_separation = FOMC_separation.append(temp1, ignore_index=True)
        FOMC_separation = FOMC_separation.append(temp2, ignore_index=True)

    FOMC_separation.to_excel(os.path.join(CACHE_PATH,'raw_text_separated.xlsx'))
    return FOMC_separation


def data_preprocess(docs,DATASET,phrase_itera,th):
    # Tokenize the documents
    init_docs = [re.findall(r'''[\w']+|[.,!?;-~{}`´_<=>:/@*()&'$%#"]''', doc) for doc in docs]
    init_docs = [[w.lower() for w in init_docs[doc] if not contains_punctuation(w)] for doc in range(len(init_docs))] # removes punct and makes lower case.
    init_docs = [[w for w in init_docs[doc] if not contains_numeric(w)] for doc in range(len(init_docs))]  # removes numeric
    init_docs = [[w for w in init_docs[doc] if len(w)>1] for doc in range(len(init_docs))] # removes single character
    

    
    for i in range(phrase_itera):
        print(f"Phrase iteration: {i+1}")
        phrases = Phrases(init_docs, min_count=1, threshold=th, connector_words=ENGLISH_CONNECTOR_WORDS)
        init_docs = [phrases[sent] for sent in init_docs]
        del phrases
    
        # Read stopwords
    with open('stops.txt', 'r') as f:
        stops = f.read().split('\n')
    # Add specific stopwords 
    additional_stopword = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september',
                                   'october', 'november', 'december']
    additional_stopword = additional_stopword + [w[:3] for w in additional_stopword]
    additional_stopword = additional_stopword +['unintelligible']
    firstname = pd.read_excel('util_files/firstnames.xlsx')
    firstname_list = firstname['First name'].dropna().values
    for firstname in firstname_list:
        additional_stopword.append(firstname.lower())
    stops = stops + additional_stopword
    
    init_docs = [[w for w in init_docs[doc] if w not in stops] for doc in range(len(init_docs))]
    
    pkl_file = open(f'{OUTPATH}/{DATASET}/corpus.pkl','wb')
    pickle.dump(init_docs,pkl_file)
        
    init_docs = [" ".join(init_docs[doc]) for doc in range(len(init_docs))] # joins words in doc
    
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
    print('vocabulary size: {}'.format(v_size))  
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
    
    docs_tr = [[word2id[w] for w in docs[idx_permute[idx_d]].split() if w in word2id] for idx_d in range(trSize)]
    docs_ts = [[word2id[w] for w in docs[idx_permute[idx_d+trSize]].split() if w in word2id] for idx_d in range(tsSize)]
    docs_va = [[word2id[w] for w in docs[idx_permute[idx_d+trSize+tsSize]].split() if w in word2id] for idx_d in range(vaSize)]
    
    print('  number of documents (train): {} [this should be equal to {}]'.format(len(docs_tr), trSize))
    print('  number of documents (test): {} [this should be equal to {}]'.format(len(docs_ts), tsSize))
    print('  number of documents (valid): {} [this should be equal to {}]'.format(len(docs_va), vaSize))
    
    # Remove empty documents
    print('removing empty documents...')
    
    def remove_empty(in_docs):
        return [doc for doc in in_docs if doc!=[]]
    
    docs_tr = remove_empty(docs_tr)
    docs_ts = remove_empty(docs_ts)
    docs_va = remove_empty(docs_va)
    
    # Remove test documents with length=1
    docs_ts = [doc for doc in docs_ts if len(doc)>1]
    
    # Split test set in 2 halves
    print('splitting test documents in 2 halves...')
    docs_ts_h1 = [[w for i,w in enumerate(doc) if i<=len(doc)/2.0-1] for doc in docs_ts]
    docs_ts_h2 = [[w for i,w in enumerate(doc) if i>len(doc)/2.0-1] for doc in docs_ts]
    
    # Getting lists of words and doc_indices
    print('creating lists of words...')
    
    def create_list_words(in_docs):
        return [x for y in in_docs for x in y]
    
    words_tr = create_list_words(docs_tr)
    words_ts = create_list_words(docs_ts)
    words_ts_h1 = create_list_words(docs_ts_h1)
    words_ts_h2 = create_list_words(docs_ts_h2)
    words_va = create_list_words(docs_va)
    
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
    
    doc_indices_tr = create_doc_indices(docs_tr)
    doc_indices_ts = create_doc_indices(docs_ts)
    doc_indices_ts_h1 = create_doc_indices(docs_ts_h1)
    doc_indices_ts_h2 = create_doc_indices(docs_ts_h2)
    doc_indices_va = create_doc_indices(docs_va)
    
    print('  len(np.unique(doc_indices_tr)): {} [this should be {}]'.format(len(np.unique(doc_indices_tr)), len(docs_tr)))
    print('  len(np.unique(doc_indices_ts)): {} [this should be {}]'.format(len(np.unique(doc_indices_ts)), len(docs_ts)))
    print('  len(np.unique(doc_indices_ts_h1)): {} [this should be {}]'.format(len(np.unique(doc_indices_ts_h1)), len(docs_ts_h1)))
    print('  len(np.unique(doc_indices_ts_h2)): {} [this should be {}]'.format(len(np.unique(doc_indices_ts_h2)), len(docs_ts_h2)))
    print('  len(np.unique(doc_indices_va)): {} [this should be {}]'.format(len(np.unique(doc_indices_va)), len(docs_va)))
    
    # Number of documents in each set
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
    
    # Create bow representation
    print('creating bow representation...')
    
    def create_bow(doc_indices, words, n_docs, vocab_size):
        return sparse.coo_matrix(([1]*len(doc_indices),(doc_indices, words)), shape=(n_docs, vocab_size)).tocsr()
    
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
    
    # Save vocabulary to file
    path_save = f'{OUTPATH}/{DATASET}/'
    if not os.path.isdir(path_save):
        os.system('mkdir -p ' + path_save)
    
    with open(path_save + 'vocab.pkl', 'wb') as f:
        pickle.dump(vocab, f)
    del vocab
    
    
    # Split bow into token/value pairs
    print('splitting bow into token/value pairs and saving to disk...')
    
    def split_bow(bow_in, n_docs):
        indices = [[w for w in bow_in[doc,:].indices] for doc in range(n_docs)]
        counts = [[c for c in bow_in[doc,:].data] for doc in range(n_docs)]
        return indices, counts
    
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
    
    print('Data ready !!')
    print('*************')

 
    
def statements_raw():
    data = pd.read_csv(STATEMENT_PATH)
    docs = data["statement"].to_list()
    return docs

TRANSCRIPT_PATH = os.path.expanduser("~/Dropbox/MPCounterfactual/src/collection/python/data/transcript_raw_text")
BB_PATH = os.path.expanduser("~/Dropbox/MPCounterfactual/src/collection/python/output/bluebook_raw_text")
STATEMENT_PATH = os.path.expanduser("~/Dropbox/MPCounterfactual/src/derivation/python/output/statements_text_extraction.csv")
OUTPATH = os.path.expanduser("~/Dropbox/MPCounterfactual/src/etm/data")        
UTILFILE_PATH = os.path.expanduser("~/Dropbox/MPCounterfactual/src/etm/util_files")        

# Maximum / minimum document frequency
max_df = 0.7 # in a maximum of # % of documents if # is float.
min_df = 10  # choose desired value for min_df // in a minimum of # documents
phrase_itera = 2
threshold = 10

bb_docs = preprocess_longdocs()
docs,raw_text = generate_rawtranscripts()

statement_docs = statements_raw()

DATASET = f"BBTSST_{min_df}_iter{phrase_itera}_th{threshold}"
if not os.path.exists(f"{OUTPATH}/{DATASET}"):
    os.makedirs(f"{OUTPATH}/{DATASET}")
docs = bb_docs + transcript_docs + statement_docs
data_preprocess(docs,DATASET,phrase_itera,threshold)
print("f{DATASET} complete!")   


# =============================================================================
# Pre-process
raw_text 

# =============================================================================





# =============================================================================
#     
# DATASET = f"BBTS_{min_df}_iter{phrase_itera}_th{threshold}"
# if not os.path.exists(f"{OUTPATH}/{DATASET}"):
#     os.makedirs(f"{OUTPATH}/{DATASET}")
# docs = bb_docs + transcript_docs 
# data_preprocess(docs,DATASET,phrase_itera,threshold)
#   
# DATASET = f"TS_{min_df}_iter{phrase_itera}_th{threshold}"
# if not os.path.exists(f"{OUTPATH}/{DATASET}"):
#     os.makedirs(f"{OUTPATH}/{DATASET}")
# docs = transcript_docs 
# data_preprocess(docs,DATASET,phrase_itera,threshold)
#     
# =============================================================================
