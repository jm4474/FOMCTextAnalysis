from sklearn.feature_extraction.text import CountVectorizer
import numpy as np
import pickle
import random
from scipy import sparse
import itertools
from scipy.io import savemat, loadmat
import os
import pandas as pd
import argparse


parser = argparse.ArgumentParser(description='The Embedded Topic Model')



# Maximum / minimum document frequency
max_df = 1.0
min_df = 10  # choose desired value for min_df
parser.add_argument('--dataset', type=str, default='both_full', help='data source in {bluebook, transcipt, both_subsampled} -- or anything else for both_full')

args = parser.parse_args()

for date in open("dates").readlines():
    
    date=date.strip()

    print("\n\n\n ***** Preparing {} ***** \n".format(date))

    # Output path
    output_dir = os.path.join('../data/fomc', args.dataset, "min_df_{}".format(min_df))
    path_save = os.path.join(output_dir, date)
    if not os.path.isdir(path_save):
        os.system('mkdir -p ' + path_save)
    else:
        print("{} exists!".format(path_save))
        continue
        
    vocab = pickle.load(open(os.path.join(output_dir, "vocab.pkl"), 'rb'))
    word2id = dict([(w, j) for j, w in enumerate(vocab)])
    id2word = dict([(j, w) for j, w in enumerate(vocab)])
    #print(vocab)

    # Read stopwords
    with open('stops.txt', 'r') as f:
        stops = f.read().split('\n')

    # Read data
    print('reading text file...')
    data_file = '../../analysis/python/output/lda_dataset.csv'
    docs = pd.read_csv(data_file)
    print(docs.shape)



    if args.dataset=="bluebook":
        docs = docs.loc[~docs['FOMC_Section'].isin(['2.0'])]
        print(docs.shape)
        docs = docs.loc[docs['content'].str.contains(' ')]
    if args.dataset=="transcript":
        docs = docs.loc[docs['FOMC_Section'].isin(['2.0'])]
        print(docs.shape)
        docs = docs.loc[docs['content'].str.contains(' ')]
    if args.dataset=="both_subsampled":
        tmp1 = docs.loc[docs['FOMC_Section'].isin(['2.0'])]
        tmp2 = docs.loc[~docs['FOMC_Section'].isin(['2.0'])]
        tmp1 = tmp1.loc[tmp1['content'].str.contains(' ')]
        tmp2 = tmp2.loc[tmp2['content'].str.contains(' ')]
        tmp1 = tmp1.sample(tmp2.shape[0])
        tmp1 = tmp1.append(tmp2, ignore_index=True)
        docs = tmp1
        
    print(docs.shape)

    docs = docs.loc[docs['date']==date]

    # Remove empty and length 1 documents
    docs = docs[docs['content'].apply(lambda x: len(str(x).split(" ")) > 2)]
    
    docs = docs[['content','speaker_id','speaker', 'act_vote']]
    docs.to_csv(os.path.join(path_save, "{}.csv".format(date)), index=False)

    docs = [d for d in list(docs['content'])]
    docs = [d.lower().replace('alternative a ', 'alternative_a ').replace('alternative b ', 'alternative_b ').replace('alternative c ', 'alternative_c ') \
            for d in docs]

    print(len(docs))

    num_docs = len(docs)
    docs_tr = [[word2id[w] for w in docs[idx_d].split() if w in word2id] for idx_d in range(num_docs)]
    del docs

    print('  number of documents (train): {} [this should be equal to {}]'.format(len(docs_tr), num_docs))


    # Getting lists of words and doc_indices
    print('creating lists of words...')

    def create_list_words(in_docs):
        return [x for y in in_docs for x in y]

    words_tr = create_list_words(docs_tr)

    print('  len(words_tr): ', len(words_tr))

    # Get doc indices
    print('getting doc indices...')

    def create_doc_indices(in_docs):
        aux = [[j for i in range(len(doc))] for j, doc in enumerate(in_docs)]
        return [int(x) for y in aux for x in y]

    doc_indices_tr = create_doc_indices(docs_tr)

    print('  len(np.unique(doc_indices_tr)): {} [this should be {}]'.format(len(np.unique(doc_indices_tr)), len(docs_tr)))

    # Number of documents in each set
    n_docs_tr = len(docs_tr)


    # Remove unused variables
    del docs_tr


    # Create bow representation
    print('creating bow representation...')

    def create_bow(doc_indices, words, n_docs, vocab_size):
        return sparse.coo_matrix(([1]*len(doc_indices),(doc_indices, words)), shape=(n_docs, vocab_size)).tocsr()

    bow_tr = create_bow(doc_indices_tr, words_tr, n_docs_tr, len(vocab))

    # Save vocabulary to file
    with open(os.path.join(path_save, 'vocab.pkl'), 'wb') as f:
        pickle.dump(vocab, f)
    del vocab

    # Split bow intro token/value pairs
    print('splitting bow intro token/value pairs and saving to disk...')

    def split_bow(bow_in, n_docs):
        indices = [[w for w in bow_in[doc,:].indices] for doc in range(n_docs)]
        counts = [[c for c in bow_in[doc,:].data] for doc in range(n_docs)]
        return indices, counts

    bow_tr_tokens, bow_tr_counts = split_bow(bow_tr, n_docs_tr)
    savemat(os.path.join(path_save, 'bow_tr_tokens.mat'), {'tokens': bow_tr_tokens}, do_compression=True)
    savemat(os.path.join(path_save, 'bow_tr_counts.mat'), {'counts': bow_tr_counts}, do_compression=True)


    print('Data ready !!')
    print('*************')

