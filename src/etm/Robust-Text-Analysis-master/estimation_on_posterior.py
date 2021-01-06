from VB_estimate import vb_estimate
from estimation import band
import numpy as np
import pandas as pd
from timeit import default_timer
from Constant import *
import pickle
import matplotlib.pyplot as plt

maxit = 1
topic_num = 40
maxit_NMF = 50000
draw_num = 120
eps = 1e-8

print('Reading cached data')
with open(os.path.join(MATRIX_PATH, 'FOMC1_text_onlyTF.pkl'), 'rb') as f:
    FOMC1_text = pickle.load(f)
with open(os.path.join(MATRIX_PATH, 'FOMC2_text_onlyTF.pkl'), 'rb') as f:
    FOMC2_text = pickle.load(f)
td_matrix1_raw = pd.read_excel(os.path.join(MATRIX_PATH, 'FOMC1_meeting_matrix_onlyTF.xlsx'), index_col=0)
td_matrix2_raw = pd.read_excel(os.path.join(MATRIX_PATH, 'FOMC2_meeting_matrix_onlyTF.xlsx'), index_col=0)
stem_num1 = td_matrix1_raw.sum(axis=0)
stem_num2 = td_matrix2_raw.sum(axis=0)

VB_HHI_FOMC1_res = []
VB_HHI_FOMC2_res = []
NMF_HHI_FOMC1_max = []
NMF_HHI_FOMC1_min = []
NMF_HHI_FOMC2_max = []
NMF_HHI_FOMC2_min = []


for i in range(maxit):
    print('Drawing posterior estimate number {}'.format(i))
    start = default_timer()
    HHI_FOMC1, posterior_mean1, gamma1, lam1, olda1, text1 = vb_estimate('FOMC1',onlyTF=True, K=topic_num, alpha=1.25, eta=0.025, tau=100000, kappa=1)
    HHI_FOMC2, posterior_mean2, gamma2, lam2, olda2, text2 = vb_estimate('FOMC2', onlyTF=True, K=topic_num, alpha=1.25, eta=0.025, tau=100000, kappa=1)

    # transpose lambda so that it is aligned to be V x K
    #lam1 = lam1.T
    lam1, lam2 = lam1.T, lam2.T
    # compute posterior mean of each draw
    theta1 = gamma1 / gamma1.sum(axis=0)
    B1 = lam1 / lam1.sum(axis=0)
    theta2 = gamma2 / gamma2.sum(axis=0)
    B2 = lam2 / lam2.sum(axis=0)

    # perform NMF on posterior
    P_hat1 = np.dot(B1, theta1) #/ np.dot(B1, theta1).sum(axis=0)
    P_hat2 = np.dot(B2, theta2) #/ np.dot(B2, theta2).sum(axis=0)

    Herfindahl1, _, _, _ = band(P_hat1, topic_num, eps, maxit_NMF, draw_num, stem_num1, init_random_method='gamma', init_random_matrix=None,
         noise_scale=0.01, gamma_param=(-3,0))
    Herfindahl2, _, _, _ = band(P_hat2, topic_num, eps, maxit_NMF, draw_num, stem_num2, init_random_method='gamma', init_random_matrix=None,
         noise_scale=0.01, gamma_param=(-3,0))

    # todo: append HHI computed from theta1 into the NMF_HHI_FOMC1, then report the min and max
    # the reason is because the robust NMF graph on BTheta is not over all possible NMFs, so
    # including the HHI computed from the gamma directly from VB will by construction expand the band so that
    # the average of the HHI from 100 VBs will be in the band for average (min(120 NMF + 1 true VB)), average (max(120 NMF + 1 true VB))

    Herfindahl1, Herfindahl2 = list(Herfindahl1), list(Herfindahl2)
    Herfindahl1.append(HHI_FOMC1)
    Herfindahl2.append(HHI_FOMC2)
    Herfindahl1, Herfindahl2 = np.array(Herfindahl1), np.array(Herfindahl2)

    NMF_HHI_FOMC1_max.append(Herfindahl1.max(axis=0))
    NMF_HHI_FOMC1_min.append(Herfindahl1.min(axis=0))
    NMF_HHI_FOMC2_max.append(Herfindahl2.max(axis=0))
    NMF_HHI_FOMC2_min.append(Herfindahl2.min(axis=0))
    VB_HHI_FOMC1_res.append(HHI_FOMC1)
    VB_HHI_FOMC2_res.append(HHI_FOMC2)
    end = default_timer()
    print('Finished draw {}. Time {}'.format(i, end-start))

fig1 = plt.figure()
plt.plot(np.arange(148), np.array(VB_HHI_FOMC1_res).mean(axis=0), c='r')
plt.plot(np.arange(148), np.array(NMF_HHI_FOMC1_max).mean(axis=0), c='k', ls='--')
plt.plot(np.arange(148), np.array(NMF_HHI_FOMC1_min).mean(axis=0), c='k', ls='--')
plt.fill_between(np.arange(148), np.array(NMF_HHI_FOMC1_max).mean(axis=0), np.array(NMF_HHI_FOMC1_min).mean(axis=0), color='grey', alpha=0.1)
plt.title('Herfindahl measures for FOMC1 Meetings, alpha = 1.25')
plt.show()

fig1 = plt.figure()
plt.plot(np.arange(148), np.array(VB_HHI_FOMC2_res).mean(axis=0), c='r')
plt.plot(np.arange(148), np.array(NMF_HHI_FOMC2_max).mean(axis=0), c='k', ls='--')
plt.plot(np.arange(148), np.array(NMF_HHI_FOMC2_min).mean(axis=0), c='k', ls='--')
plt.fill_between(np.arange(148), np.array(NMF_HHI_FOMC2_max).mean(axis=0), np.array(NMF_HHI_FOMC2_min).mean(axis=0), color='grey', alpha=0.1)
plt.title('Herfindahl measures for FOMC2 Meetings, alpha = 1.25')
plt.show()


