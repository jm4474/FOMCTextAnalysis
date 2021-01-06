import pandas as pd
from Constant import CACHE_PATH
import os

path = os.path.join(CACHE_PATH, 'FOMC_token_separated_col.xlsx')
df = pd.read_excel(path)

FOMC1 = df[df['Section'] == 1]
FOMC2 = df[df['Section'] == 2]

word_list = []
for line in FOMC1['content']:
    try:
        words = line.split(' ')
        for word in words:
            if word not in word_list:
                word_list.append(word)
    except AttributeError:
        pass


from VB_estimate import vb_estimate
from estimation import band
import numpy as np
import pandas as pd
from timeit import default_timer
from Constant import *
import pickle
import matplotlib.pyplot as plt

maxit = 20
topic_num = 40
maxit_NMF = 1000
draw_num = 120
eps = 1e-6

print('Reading cached data')
with open(os.path.join(MATRIX_PATH, 'FOMC1_text_onlyTF.pkl'), 'rb') as f:
    FOMC1_text = pickle.load(f)


td_matrix1_raw = pd.read_excel(os.path.join(MATRIX_PATH, 'FOMC1_meeting_matrix_onlyTF.xlsx'), index_col=0)
td_matrix1 = td_matrix1_raw / td_matrix1_raw.sum(axis=0)
stem_num1 = td_matrix1_raw.sum(axis=0)
td_matrix1[td_matrix1 == 0] = 1e-12

HHI_FOMC1, posterior_mean, gamma1, lam1, olda, text1 = vb_estimate('FOMC1', onlyTF=True, K=topic_num, alpha=3, eta=0.025)

maxit = 10
from estimation import KL
for i in range(maxit):
    (gamma1, bound) = olda.update_lambda(text1)
    lam1 = olda._lambda
    gamma1 = gamma1.T

    lam1 = lam1.T
    # compute posterior mean of each draw
    theta1 = gamma1 / gamma1.sum(axis=0)
    B1 = lam1 / lam1.sum(axis=0)
    print(KL(td_matrix1, td_matrix1, B1, theta1))

from estimation import KL
P_hat = np.dot(B1, theta1)



