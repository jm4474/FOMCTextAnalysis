from __future__ import print_function
from IPython import get_ipython
get_ipython().magic('reset -sf')

# =============================================================================
# Extract Model Results

import argparse
import torch
import pickle
import numpy as np
import os
import math
import random
import sys
import matplotlib.pyplot as plt
import data
import scipy.io
import pandas as pd

from torch import nn, optim
from torch.nn import functional as F

from etm import ETMECON
from utils import nearest_neighbors, get_topic_coherence, get_topic_diversity

# =============================================================================

class Vars:
    pass
args = Vars()

meetphrase_itera = 2 # Number of phrase iterations
meetthreshold = "inf" # Threshold value for collocations. If "inf": no collocations
meetmax_df=1.0
meetmin_df=10
MEETDATASAMPLE = f"MEET_min{meetmin_df}_max{meetmax_df}_iter{meetphrase_itera}_th{meetthreshold}"

embphrase_itera = 2 # Number o fphrase iterations
embthreshold = "inf" # Threshold value for collocations. If "inf": no collocations
emb_max_df = 1.0 # in a maximum of # % of documents if # is float.
emb_min_df = 1  # choose desired value for min_df // in a minimum of # documents
EMBDATASET = f"BBTSST_min{emb_min_df}_max{emb_max_df}_iter{embphrase_itera}_th{embthreshold}"

DATAPATH = os.path.expanduser("~/Dropbox/MPCounterfactual/src/etm/")

dataset = f"{MEETDATASAMPLE}"
data_path=f"{DATAPATH}/data/{MEETDATASAMPLE}"
emb_path=f"{DATAPATH}/embeddings/{EMBDATASET}_emb"
save_path=f"{DATAPATH}/results"
batch_size = 1000

num_topics = 10
epochs = 10000
mode = 'train'
rho_size = 300
emb_size = 300
train_embeddings = 0
seed = 2019    

lr = 0.005
lr_factor=4.0
optimizer = 'adam'
enc_drop = 0.0
clip = 0.0
nonmono = 10
wdecay = 1.2e-6
anneal_lr = 0
bow_norm = 1

num_words = 15
log_interval = 2
visualize_every = 100
eval_batch_size = 1000
load_from = ""
tc = 1
td = 1

    ### data and file related arguments
args.dataset = dataset #', type=str, default='20ng', help='name of corpus')
args.data_path = data_path #", type=str, default='data/20ng', help='directory containing data')
args.emb_path = emb_path #', type=str, default='data/20ng_embeddings.txt', help='directory containing word embeddings')
args.save_path = save_path #', type=str, default='./results', help='path to save results')
args.batch_size = batch_size #', type=int, default=1000, help='input batch size for training')
    
args.num_topics = num_topics # type=int, default=50, help='number of topics')
args.rho_size = rho_size #', type=int, default=300, help='dimension of rho')
args.emb_size = emb_size #', type=int, default=300, help='dimension of embeddings')
args.train_embeddings = train_embeddings #', type=int, default=0, help='whether to fix rho or train it')
args.seed = seed # Set a seed

### optimization-related arguments
args.lr = lr #', type=float, default=0.005, help='learning rate')
args.lr_factor = lr_factor #', type=float, default=4.0, help='divide learning rate by this...')
args.epochs = epochs #', type=int, default=20, help='number of epochs to train...150 for 20ng 100 for others')
args.mode = mode #', type=str, default='train', help='train or eval or retrieve model')
args.optimizer = optimizer #', type=str, default='adam', help='choice of optimizer')
args.enc_drop = enc_drop #', type=float, default=0.0, help='dropout rate on encoder')
args.clip = clip #', type=float, default=0.0, help='gradient clipping')
args.nonmono = nonmono #', type=int, default=10, help='number of bad hits allowed')
args.wdecay = wdecay #', type=float, default=1.2e-6, help='some l2 regularization')
args.anneal_lr = anneal_lr #', type=int, default=0, help='whether to anneal the learning rate or not')
args.bow_norm = bow_norm  #', type=int, default=1, help='normalize the bows or not')

### evaluation, visualization, and logging-related arguments
args.num_words = num_words #', type=int, default=10, help='number of words for topic viz')
args.log_interval = log_interval #', type=int, default=2, help='when to log training')
args.visualize_every = visualize_every #', type=int, default=10, help='when to visualize results')
args.eval_batch_size = eval_batch_size #', type=int, default=1000, help='input batch size for evaluation')
args.load_from = load_from #', type=str, default='', help='the name of the ckpt to eval from')
args.tc = tc #', type=int, default=0, help='whether to compute topic coherence or not')
args.td = td #', type=int, default=0, help='whether to compute topic diversity or not')
  

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

print('\n')
# Set the seed
np.random.seed(args.seed)
torch.manual_seed(args.seed)
if torch.cuda.is_available():
    torch.cuda.manual_seed(args.seed)

## #Get data
# 1. vocabulary
vocab, train, valid, test = data.get_data(os.path.join(args.data_path))
vocab_size = len(vocab)
args.vocab_size = vocab_size

# 1. training data
train_tokens = train['tokens']
train_counts = train['counts']
args.num_docs_train = len(train_tokens)

# 2. dev set
valid_tokens = valid['tokens']
valid_counts = valid['counts']
args.num_docs_valid = len(valid_tokens)

# 3. test data
test_tokens = test['tokens']
test_counts = test['counts']
args.num_docs_test = len(test_tokens)
test_1_tokens = test['tokens_1']
test_1_counts = test['counts_1']
args.num_docs_test_1 = len(test_1_tokens)
test_2_tokens = test['tokens_2']
test_2_counts = test['counts_2']
args.num_docs_test_2 = len(test_2_tokens)

# 4. full data
all_tokens = scipy.io.loadmat(os.path.join(args.data_path, 'bow_all_tokens.mat'))['tokens'].squeeze()
all_counts = scipy.io.loadmat(os.path.join(args.data_path, 'bow_all_counts.mat'))['counts'].squeeze()
args.num_docs = len(all_tokens)

# 5. get covariate data
train_df = pd.read_pickle(f"{args.data_path}/data_tr.pkl")
valid_df = pd.read_pickle(f"{args.data_path}/data_va.pkl")
test_df =  pd.read_pickle(f"{args.data_path}/data_ts.pkl")
test_1_df = pd.read_pickle(f"{args.data_path}/data_ts_h1.pkl")
test_2_df = pd.read_pickle(f"{args.data_path}/data_ts_h2.pkl")
all_df = pd.read_pickle(f"{args.data_path}/data_all.pkl")
    
econ_tr = torch.from_numpy(train_df.astype(dtype="float32").to_numpy()).to(device)
econ_valid = torch.from_numpy(valid_df.astype(dtype="float32").to_numpy()).to(device)
econ_test = torch.from_numpy(test_df.astype(dtype="float32").to_numpy()).to(device)
econ_test1 = torch.from_numpy(test_1_df.astype(dtype="float32").to_numpy()).to(device)
econ_test2 = torch.from_numpy(test_2_df.astype(dtype="float32").to_numpy()).to(device)
econ_all = torch.from_numpy(all_df.astype(dtype="float32").to_numpy()).to(device)

### Load pre-trained embeddings.
embeddings = None
if not args.train_embeddings:
    emb_path = args.emb_path
    vect_path = os.path.join(args.data_path.split('/')[0], 'embeddings.pkl')
    vectors = {}
    with open(emb_path, 'rb') as f:
        for l in f:
            line = l.decode().split()
            word = line[0]
            if word in vocab:
                vect = np.array(line[1:]).astype(float)
                vectors[word] = vect
    embeddings = np.zeros((vocab_size, args.emb_size))
    words_found = 0
    for i, word in enumerate(vocab):
        try:
            embeddings[i] = vectors[word]
            words_found += 1
        except KeyError:
            print(f"{word} not in the embeddings")
            embeddings[i] = np.random.normal(scale=0.6, size=(args.emb_size, ))
    embeddings = torch.from_numpy(embeddings).to(device)
    args.embeddings_dim = embeddings.size()

print('=*'*100)
print('Training an Embedded Topic Model on {}'.format(args.dataset.upper()))
print('=*'*100)

## define checkpoint
if not os.path.exists(args.save_path):
    os.makedirs(args.save_path)

if args.mode == 'eval':
    ckpt = args.load_from
else:
    ckpt = os.path.join(args.save_path,
        'etm_{}_K_{}_Htheta_{}_Optim_{}_Clip_{}_ThetaAct_{}_Lr_{}_Bsz_{}_RhoSize_{}_trainEmbeddings_{}'.format(
        args.dataset, args.num_topics, args.t_hidden_size, args.optimizer, args.clip, args.theta_act,
            args.lr, args.batch_size, args.rho_size, args.train_embeddings))

## define model and optimizer
model = ETMECON(args.num_topics, vocab_size, args.t_hidden_size, args.rho_size, args.emb_size,
                args.theta_act, embeddings, args.train_embeddings, econ_tr, args.enc_drop).to(device)

print('model: {}'.format(model))

if args.optimizer == 'adam':
    optimizer = optim.Adam(model.parameters(), lr=args.lr, weight_decay=args.wdecay)
elif args.optimizer == 'adagrad':
    optimizer = optim.Adagrad(model.parameters(), lr=args.lr, weight_decay=args.wdecay)
elif args.optimizer == 'adadelta':
    optimizer = optim.Adadelta(model.parameters(), lr=args.lr, weight_decay=args.wdecay)
elif args.optimizer == 'rmsprop':
    optimizer = optim.RMSprop(model.parameters(), lr=args.lr, weight_decay=args.wdecay)
elif args.optimizer == 'asgd':
    optimizer = optim.ASGD(model.parameters(), lr=args.lr, t0=0, lambd=0., weight_decay=args.wdecay)
else:
    print('Defaulting to vanilla SGD')
    optimizer = optim.SGD(model.parameters(), lr=args.lr)

def train(epoch):
    model.train()
    acc_loss = 0
    acc_kl_theta_loss = 0
    cnt = 0
    indices = torch.randperm(args.num_docs_train)
    indices = torch.split(indices, args.batch_size)
    for idx, ind in enumerate(indices):
        optimizer.zero_grad()
        model.zero_grad()
        data_batch = data.get_batch(train_tokens, train_counts, ind, args.vocab_size, device)
        sums = data_batch.sum(1).unsqueeze(1)
        if args.bow_norm:
            normalized_data_batch = data_batch / sums
        else:
            normalized_data_batch = data_batch
        recon_loss = model(data_batch, normalized_data_batch,econ_tr)
        total_loss = recon_loss 
        total_loss.backward()

        if args.clip > 0:
            torch.nn.utils.clip_grad_norm_(model.parameters(), args.clip)
        optimizer.step()

        acc_loss += torch.sum(recon_loss).item()
        #acc_kl_theta_loss += torch.sum(kld_theta).item()
        cnt += 1

        if idx % args.log_interval == 0 and idx > 0:
            cur_loss = round(acc_loss / cnt, 2)
            #cur_kl_theta = round(acc_kl_theta_loss / cnt, 2)
            #cur_real_loss = round(cur_loss + cur_kl_theta, 2)

            print('Epoch: {} .. batch: {}/{} .. LR: {} Rec_loss: {} '.format(
                epoch, idx, len(indices), optimizer.param_groups[0]['lr'], cur_loss))

    cur_loss = round(acc_loss / cnt, 2)
    cur_kl_theta = round(acc_kl_theta_loss / cnt, 2)
    cur_real_loss = round(cur_loss + cur_kl_theta, 2)
    print('*'*100)
    print('Epoch----->{} .. LR: {} .. KL_theta: {} .. Rec_loss: {} .. NELBO: {}'.format(
            epoch, optimizer.param_groups[0]['lr'], cur_kl_theta, cur_loss, cur_real_loss))
    print('*'*100)

def visualize(m, show_emb=True):
    if not os.path.exists('./results'):
        os.makedirs('./results')

    m.eval()

    queries = ['money', 'inflation', 'price']

    ## visualize topics using monte carlo
    with torch.no_grad():
        print('#'*100)
        print('Visualize topics...')
        topics_words = []
        gammas = m.get_beta()
        for k in range(args.num_topics):
            gamma = gammas[k]
            top_words = list(gamma.cpu().numpy().argsort()[-args.num_words+1:][::-1])
            topic_words = [vocab[a] for a in top_words]
            topics_words.append(' '.join(topic_words))
            print('Topic {}: {}'.format(k, topic_words))

        if show_emb:
            ## visualize word embeddings by using V to get nearest neighbors
            print('#'*100)
            print('Visualize word embeddings by using output embedding matrix')
            try:
                embeddings = m.rho.weight  # Vocab_size x E
            except:
                embeddings = m.rho         # Vocab_size x E
            neighbors = []
            for word in queries:
                print('word: {} .. neighbors: {}'.format(
                    word, nearest_neighbors(word, embeddings, vocab)))
            print('#'*100)

def evaluate(m, source, tc=False, td=False):
    """Compute perplexity on document completion.
    """
    m.eval()
    with torch.no_grad():
        if source == 'val':
            indices = torch.split(torch.tensor(range(args.num_docs_valid)), args.eval_batch_size)
            tokens = valid_tokens
            counts = valid_counts
        else:
            indices = torch.split(torch.tensor(range(args.num_docs_test)), args.eval_batch_size)
            tokens = test_tokens
            counts = test_counts

        ## get \beta here
        beta = m.get_beta()

        ### do dc and tc here
        acc_loss = 0
        cnt = 0
        indices_1 = torch.split(torch.tensor(range(args.num_docs_test_1)), args.eval_batch_size)
        for idx, ind in enumerate(indices_1):
            ## get theta from first half of docs
            data_batch_1 = data.get_batch(test_tokens, test_counts, ind, args.vocab_size, device)
            sums_1 = data_batch_1.sum(1).unsqueeze(1)
            if args.bow_norm:
                normalized_data_batch_1 = data_batch_1 / sums_1
            else:
                normalized_data_batch_1 = data_batch_1
            theta = m.get_theta(econ_test)

            ## get prediction loss using second half
            data_batch_2 = data.get_batch(test_2_tokens, test_2_counts, ind, args.vocab_size, device)
            sums_2 = data_batch_2.sum(1).unsqueeze(1)
            res = torch.mm(theta, beta)
            preds = torch.log(res)
            recon_loss = -(preds * data_batch_2).sum(1)

            loss = recon_loss / sums_2.squeeze()
            loss = loss.mean().item()
            acc_loss += loss
            cnt += 1
        cur_loss = acc_loss / cnt
        ppl_dc = round(math.exp(cur_loss), 1)
        print('*'*100)
        print('{} Doc Completion PPL: {}'.format(source.upper(), ppl_dc))
        #print('*'*100)
        if tc or td:
            beta = beta.data.cpu().numpy()
            if tc:
                #print('Computing topic coherence...')
                get_topic_coherence(beta, train_tokens, vocab)
            if td:
                #print('Computing topic diversity...')
                get_topic_diversity(beta, 25)
        return ppl_dc

if args.mode == 'train':
    ## train model on data
    best_epoch = 0
    best_val_ppl = 1e9
    all_val_ppls = []
    print('\n')
    print('Visualizing model quality before training...')
    visualize(model)
    print('\n')
    for epoch in range(1, args.epochs):
        train(epoch)
        
        val_ppl = evaluate(model, 'val')
        if val_ppl < best_val_ppl:
            with open(ckpt, 'wb') as f:
                torch.save(model, f)
            best_epoch = epoch
            best_val_ppl = val_ppl
        else:
            ## check whether to anneal lr
            lr = optimizer.param_groups[0]['lr']
            if args.anneal_lr and (len(all_val_ppls) > args.nonmono and val_ppl > min(all_val_ppls[:-args.nonmono]) and lr > 1e-5):
                optimizer.param_groups[0]['lr'] /= args.lr_factor
        if epoch % args.visualize_every == 0:
            visualize(model)
        all_val_ppls.append(val_ppl)
    with open(ckpt, 'rb') as f:
        model = torch.load(f)
    model = model.to(device)
    val_ppl = evaluate(model, 'val')
    
elif args.mode == "retrieve":
    with open(ckpt, 'rb') as f:
        model = torch.load(f)
    model = model.to(device)
    model.eval()

    with torch.no_grad():
        ## Retrieve the topic distribution 

        ## get most used topics
        indices = torch.tensor(range(args.num_docs))
        thetaAvg = torch.zeros(1, args.num_topics).to(device)
        thetaWeightedAvg = torch.zeros(1, args.num_topics).to(device)
        ind = [idx for idx in range(args.num_docs)]
        
        
        data_batch = data.get_batch(all_tokens, all_counts, ind, args.vocab_size, device)
        sums = data_batch.sum(1).unsqueeze(1)
        
        if args.bow_norm:
            normalized_data_batch = data_batch / sums
        else:
            normalized_data_batch = data_batch
        theta, _ = model.get_theta(normalized_data_batch)
        
        x_np = theta.numpy()
        
        x_df = pd.DataFrame(x_np)
        x_df.to_pickle(f'{ckpt}tpdist.pkl')
    
        print(f"\nTopic distributions for {args.dataset} saved")
           
      
    ## visualize topics using monte carlo
    with torch.no_grad():
        print('#'*100)
        print('Visualize topics...')
        topics_data = []
        gammas = model.get_beta()
        for k in range(args.num_topics):
            gamma = gammas[k]
            top_words = list(gamma.cpu().numpy().argsort()[-12+1:][::-1])
            topic_words = [vocab[a] for a in top_words]
            topics_data.append([k,topic_words])    
            print([k,topic_words])
        
        with open(f'{ckpt}topics.pkl', 'wb') as f:
            pickle.dump(topics_data, f)        
    
    
 
else:
    with open(ckpt, 'rb') as f:
        model = torch.load(f)
    model = model.to(device)
    model.eval()

    with torch.no_grad():
        ## get document completion perplexities
        test_ppl = evaluate(model, 'test', tc=args.tc, td=args.td)

        ## get most used topics
        indices = torch.tensor(range(args.num_docs_train))
        indices = torch.split(indices, args.batch_size)
        thetaAvg = torch.zeros(1, args.num_topics).to(device)
        thetaWeightedAvg = torch.zeros(1, args.num_topics).to(device)
        cnt = 0
        for idx, ind in enumerate(indices):
            data_batch = data.get_batch(train_tokens, train_counts, ind, args.vocab_size, device)
            sums = data_batch.sum(1).unsqueeze(1)
            cnt += sums.sum(0).squeeze().cpu().numpy()
            if args.bow_norm:
                normalized_data_batch = data_batch / sums
            else:
                normalized_data_batch = data_batch
            theta, _ = model.get_theta(normalized_data_batch)
            thetaAvg += theta.sum(0).unsqueeze(0) / args.num_docs_train
            weighed_theta = sums * theta
            thetaWeightedAvg += weighed_theta.sum(0).unsqueeze(0)
            if idx % 100 == 0 and idx > 0:
                print('batch: {}/{}'.format(idx, len(indices)))
        thetaWeightedAvg = thetaWeightedAvg.squeeze().cpu().numpy() / cnt
        print('\nThe 10 most used topics are {}'.format(thetaWeightedAvg.argsort()[::-1][:10]))

        ## show topics
        beta = model.get_beta()
        topic_indices = list(np.random.choice(args.num_topics, 10)) # 10 random topics
        print('\n')
        for k in range(args.num_topics):#topic_indices:
            gamma = beta[k]
            top_words = list(gamma.cpu().numpy().argsort()[-args.num_words+1:][::-1])
            topic_words = [vocab[a] for a in top_words]
            print('Topic {}: {}'.format(k, topic_words))

        if args.train_embeddings:
            ## show etm embeddings
            try:
                rho_etm = model.rho.weight.cpu()
            except:
                rho_etm = model.rho.cpu()
            queries = ['inflation','employment','interest','price','growth','output']
            print('\n')
            print('ETM embeddings...')
            for word in queries:
                print('word: {} .. etm neighbors: {}'.format(word, nearest_neighbors(word, rho_etm, vocab)))
            print('\n')


if args.mode == "train":
    pass #return ckpt
    
model.eval()
with torch.no_grad():
            ## get document 
    new = pd.DataFrame(model.get_theta(econ_tr).numpy())

new.sum(1)    




'''    
data_batch = train_counts
sums = data_batch.sum(1).unsqueeze(1)
if args.bow_norm:
    normalized_data_batch = data_batch / sums
else:
    normalized_data_batch = data_batch
    recon_loss = model(data_batch, normalized_data_batch,econ_tr)
    
from etm import ETMECON

## define model and optimizer

model = ETMECON(args.num_topics, vocab_size, args.t_hidden_size, args.rho_size, args.emb_size,
                args.theta_act, embeddings, args.train_embeddings, econ_tr, args.enc_drop).to(device)


model.train()
acc_loss = 0
acc_kl_theta_loss = 0
cnt = 0
indices = torch.randperm(args.num_docs_train)
indices = torch.split(indices, args.batch_size)
for idx, ind in enumerate(indices):
    optimizer.zero_grad()
    model.zero_grad()
    data_batch = data.get_batch(train_tokens, train_counts, ind, args.vocab_size, device)
    sums = data_batch.sum(1).unsqueeze(1)
    if args.bow_norm:
        normalized_data_batch = data_batch / sums
    else:
        normalized_data_batch = data_batch
    recon_loss = model(data_batch, normalized_data_batch,econ_tr)

model(data_batch, normalized_data_batch,econ_tr)

model.get_theta(econ_tr)


model.eval()
with torch.no_grad():
            ## get document 
    new = pd.DataFrame(model.get_theta(econ_tr).numpy())

new.sum(1)
'''


