import torch
import torch.nn.functional as F 
import numpy as np 
import math 

from torch import nn

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class ETMECON(nn.Module):
    def __init__(self, num_topics, vocab_size, rho_size, emsize, embeddings=None, 
                 train_embeddings=True, econ_vars=None, enc_drop=0.5):
        super(ETMECON, self).__init__()

        ## define hyperparameters
        self.num_topics = num_topics
        self.vocab_size = vocab_size 
        self.rho_size = rho_size
        self.enc_drop = enc_drop
        self.emsize = emsize
        self.t_drop = nn.Dropout(enc_drop)

        ## define the word embedding matrix \rho
        if train_embeddings:
            self.rho = nn.Linear(rho_size, vocab_size, bias=False)
        else:
            num_embeddings, emsize = embeddings.size()
            rho = nn.Embedding(num_embeddings, emsize)
            self.rho = embeddings.clone().float().to(device)
            
        ## define the gamma parameters - choice parameters
        num_econ, econsize = econ_vars.size()
        self.gammas = nn.Linear(econsize, num_topics, bias=False)
        
        ## define the matrix containing the topic embeddings
        self.alphas = nn.Linear(rho_size, num_topics, bias=False) #nn.Parameter(torch.randn(rho_size, num_topics))

    def get_beta(self):
        try:
            logit = self.alphas(self.rho.weight) # torch.mm(self.rho, self.alphas)
        except:
            logit = self.alphas(self.rho)
        beta = F.softmax(logit, dim=0).transpose(1, 0) ## softmax over vocab dimension
        return beta
    
    def get_theta(self,econ_vars):
        logit = self.gammas(econ_vars)
        # print(logit)
        theta = F.softmax(logit, dim=1) ## softmax over topic dimension
        return theta

    def decode(self, theta, beta):
        res = torch.mm(theta, beta)
        preds = torch.log(res+1e-6)
        return preds 

    def forward(self, bows, normalized_bows, econ_vars, aggregate=True):
        ## get \theta
        theta = self.get_theta(econ_vars)
        
        ## get \beta
        beta = self.get_beta()

        ## get prediction loss
        preds = self.decode(theta, beta)
        recon_loss = -(preds * bows).sum(1)
        if aggregate:
            recon_loss = recon_loss.mean()
        return recon_loss , theta , beta , preds
