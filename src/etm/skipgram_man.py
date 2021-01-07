import gensim
import pickle
import os
import numpy as np
import argparse

parser = argparse.ArgumentParser(description='The Embedded Topic Model')

### data and file related arguments
parser.add_argument('--data_file', type=str, default='', help='a pickle containing a list of list with the corpus')
parser.add_argument('--emb_file', type=str, default='embeddings.txt', help='file to save the word embeddings')
parser.add_argument('--dim_rho', type=int, default=300, help='dimensionality of the word embeddings')
parser.add_argument('--min_count', type=int, default=2, help='minimum term frequency (to define the vocabulary)')
parser.add_argument('--sg', type=int, default=1, help='whether to use skip-gram')
parser.add_argument('--workers', type=int, default=25, help='number of CPU cores')
parser.add_argument('--modelfile', type=str, default="", help='path to save the model')
parser.add_argument('--negative_samples', type=int, default=10, help='number of negative samples')
parser.add_argument('--window_size', type=int, default=4, help='window size to determine context')
parser.add_argument('--iters', type=int, default=50, help='number of iterations')

args = parser.parse_args()

# Gensim code to obtain the embeddings
with open(args.data_file, 'rb') as f:
    sentences = pickle.load(f)

model = gensim.models.Word2Vec(sentences, min_count=args.min_count, sg=args.sg, vector_size=args.dim_rho,epochs=args.iters, workers=args.workers, negative=args.negative_samples, window=args.window_size)

if args.modelfile !="":
    model.save(f"{args.modelfile}.model")

# Write the embeddings to a file
with open(args.emb_file, 'w') as f:
    for v in model.wv.index_to_key:
        vec = list(model.wv[v])
        f.write(v + ' ')
        vec_str = ['%.9f' % val for val in vec]
        vec_str = " ".join(vec_str)
        f.write(vec_str + '\n')
