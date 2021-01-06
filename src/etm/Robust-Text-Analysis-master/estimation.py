import numpy as np
import statsmodels.api as sm
import pandas as pd
from Constant import *
import matplotlib.pyplot as plt
import topicmodels
import pickle
from VB_estimate import vb_estimate
import timeit

topic_num = 40
maxit = 10000
NMF_draw_num = 120
eps = 1e-6
FOMC_change = pd.Timestamp('1993-11-01 00:00:00')
cov_type='HAC'
maxlags=4

def LDA_implementation(text, alpha=1.25, beta=0.025, burning=4000, sample_freq=50, sample_size=80, keep_num=5):
    ldaobj = topicmodels.LDA.LDAGibbs(text, topic_num)
    ldaobj.set_priors(alpha=alpha, beta=beta)
    ldaobj.sample(burning,sample_freq,sample_size)
    ldaobj.samples_keep(5)
    theta = ldaobj.dt_avg()
    B = ldaobj.tt_avg()
    perplexity = ldaobj.perplexity()
    return theta, B, perplexity


def loguniform(params):
    low, high = params
    return np.power(10, np.random.uniform(low, high))


def NMF(P, k, eps, maxit, init_random_method='gamma', init_random_matrix=None, noise_scale=0.01, gamma_param=(-5,0),
        verbose=True):
    V, D = P.shape
    W = P

    if init_random_method == 'gamma':
        scale = loguniform(gamma_param)
        B = np.random.gamma(scale, 1/scale, size=(V, k))
        B = B / B.sum(axis=0)

        Theta = np.random.gamma(scale, 1/scale, size=(k, D))
        Theta = Theta / Theta.sum(axis=0)

    elif init_random_method == 'input_matrix':
        assert init_random_matrix is not None, "Need to input initial matrix"
        B_init, Theta_init = init_random_matrix
        B = B_init + np.random.uniform(0, noise_scale, size=B_init.shape)
        Theta = Theta_init + np.random.uniform(0, noise_scale, size=Theta_init.shape)
        B = B / B.sum(axis=0)
        Theta = Theta / Theta.sum(axis=0)

    else:
        B = np.random.uniform(1e-10, 1., size=(V, k))
        B = B / B.sum(axis=0)

        Theta = np.random.gamma(1e-10, 1., size=(k, D))
        Theta = Theta / Theta.sum(axis=0)


    KL_div_prev = np.inf
    for i in range(maxit):
        Theta = (Theta / np.dot(B.T, W)) * np.dot(B.T, (W * P) / np.dot(B, Theta))
        B = (B / np.dot(W, Theta.T)) * np.dot((W * P) / np.dot(B, Theta), Theta.T)
        KL_div = KL(W, P, B, Theta)
        if np.isnan(KL_div):
            print('KL divergence failed because zero division encountered')
            return None, None
        if i % 500 == 0:
            if verbose:
                print('KL divergence between steps {}: before: {}. after: {}. abs diff: {}'.format(i, KL_div_prev, KL_div, abs(KL_div_prev - KL_div)))
        if abs(KL_div_prev - KL_div) < eps:
            if verbose:
                print("converged after {}".format(str(i)))
            break
        KL_div_prev = KL_div

    B_norm = B / B.sum(axis=0)
    Theta_norm = Theta / Theta.sum(axis=0)
    return B_norm, Theta_norm



def KL(W, P, B, Theta):
    P_hat = np.dot(B, Theta)
    loss = np.sum(np.sum(W * (P * np.log(P / P_hat) - P + P_hat)))

    return loss


def band(P, k, eps, maxit, M, stem_num, cov_type='HAC', maxlags=4, init_random_method='gamma', init_random_matrix=None,
         noise_scale=0.01, gamma_param=(-3,0), verbose=True):
    record = np.zeros((M, P.shape[1]))
    covariates = pd.read_csv(os.path.join(UTILFILE_PATH,'covariates.csv'))
    covariates['num_stems'] = stem_num
    covariates['Intercept'] = 1
    params = pd.DataFrame(index=range(M),
                          columns=['Transparency', 'Recession', 'EPU', 'Twoday', 'PhDs', 'num_stems', 'Intercept'])
    bse = pd.DataFrame(index=range(M),
                       columns=['Transparency', 'Recession', 'EPU', 'Twoday', 'PhDs', 'num_stems', 'Intercept'])
    tstat = pd.DataFrame(index=range(M),
                       columns=['Transparency', 'Recession', 'EPU', 'Twoday', 'PhDs', 'num_stems', 'Intercept'])
    for m in range(M):
        start = timeit.default_timer()
        # try multiple times because it could be that the random initial matrix has zero and failed KL calculation
        for i in range(3):
            B, Theta = NMF(P, k, eps, maxit, init_random_method=init_random_method, init_random_matrix=init_random_matrix,
                               noise_scale=noise_scale, gamma_param=gamma_param, verbose=verbose)
            if B is not None and np.isnan(B).sum() == 0:
                break

        HHI = (Theta ** 2).sum(axis=0)
        record[m] = HHI
        model = sm.OLS(HHI, covariates[
            ['Transparency', 'Recession', 'EPU', 'Twoday', 'PhDs', 'num_stems', 'Intercept']].values).fit()

        params.loc[m] = model.get_robustcov_results(cov_type=cov_type, maxlags=maxlags).params
        bse.loc[m] = model.get_robustcov_results(cov_type=cov_type, maxlags=maxlags).bse
        tstat.loc[m] = params.loc[m] / bse.loc[m]
        end = timeit.default_timer()
        if verbose:
            print('Finished Trial number {}. Time: {}'.format(str(m), end-start))
    return record, params, bse, tstat


def plot_region(HHI_max, HHI_min, HHI_mean, index, section, suffix='', dpi=100):

    df = pd.DataFrame(columns=['NMF max', 'NMF min', 'HHI mean'], index=index)
    df['NMF max'] = HHI_max
    df['NMF min'] = HHI_min
    df['LDA'] = HHI_mean

    fig = plt.figure()
    plt.plot(df['NMF max'], c='k', ls='--')
    plt.plot(df['NMF min'], c='k', ls='--')
    plt.fill_between(df.index, df['NMF max'], df['NMF min'], color='grey', alpha=0.1, label='Prior Robust HHI Measure')
    plt.axvline(FOMC_change, color='b', label='FOMC Transparency Policy Change')
    LDA, = plt.plot(df['LDA'], c='r', linewidth=2.5, label='HHI of LDA Implementation')
    #plt.legend()

    plt.title('Herfindahl measure of topic concentration in {}'.format(section))
    # plt.legend(handles = [LDA])
    plt.savefig(os.path.join(PLOT_PATH, 'HHI_{}.png'.format(section + suffix)), format='png', dpi=dpi)

def regression_single(HHI, stem_num):

    covariates = pd.read_csv(os.path.join(UTILFILE_PATH,'covariates.csv'))
    covariates['num_stems'] = stem_num
    covariates['Intercept'] = 1
    model = sm.OLS(HHI, covariates[
        ['Transparency', 'Recession', 'EPU', 'Twoday', 'PhDs', 'num_stems', 'Intercept']]).fit()

    return model


def _sample_dirichlet(alpha):
    """
    Sample from dirichlet distribution. Alpha is a matrix whose rows are params (resulting sample sum = 1 across axis 1
    """
    res = []
    for i in range(alpha.shape[0]):
        res.append(np.random.dirichlet(alpha[i,:]))

    return np.array(res)



def estimate_on_posterior(td_matrix1_raw, td_matrix2_raw, topic_num, alpha, eta, init_random_method='gamma', init_param=(-3,1),
                          verbose=False):

    _, _, gamma1, lam1, _, _ = vb_estimate('FOMC1',onlyTF=True, K=topic_num, alpha=alpha, eta=eta)
    _, _, gamma2, lam2, _, _ = vb_estimate('FOMC2', onlyTF=True, K=topic_num, alpha=alpha, eta=eta)

    # sample from dirichlet distribution given lambda and gamma
    B1 = _sample_dirichlet(lam1).T
    B2 = _sample_dirichlet(lam2).T
    Theta1 = _sample_dirichlet(gamma1).T
    Theta2 = _sample_dirichlet(gamma2).T

    P1_hat = np.dot(B1, Theta1)
    P2_hat = np.dot(B2, Theta2)

    stem_num1 = td_matrix1_raw.sum(axis=0)
    stem_num2 = td_matrix2_raw.sum(axis=0)

    Herfindahl1, params1, bse1, tstat1 = band(P1_hat, topic_num, eps, maxit, NMF_draw_num, stem_num1, init_random_method=init_random_method,
                                              gamma_param=init_param, verbose=verbose)
    Herfindahl2, params2, bse2, tstat2 = band(P2_hat, topic_num, eps, maxit, NMF_draw_num, stem_num2, init_random_method=init_random_method,
                                              gamma_param=init_param, verbose=verbose)

    section1_max = (Herfindahl1.max(axis=0), params1.max(), bse1.max(), tstat1.max())
    section1_min = (Herfindahl1.min(axis=0), params1.min(), bse1.min(), tstat1.min())
    section2_max = (Herfindahl2.max(axis=0), params2.max(), bse2.max(), tstat2.max())
    section2_min = (Herfindahl2.min(axis=0), params2.min(), bse2.min(), tstat2.min())

    HHI_FOMC1 = (Theta1**2).sum(axis=0)
    HHI_FOMC2 = (Theta2**2).sum(axis=0)

    model_FOMC1 = regression_single(HHI_FOMC1, stem_num1)
    model_FOMC2 = regression_single(HHI_FOMC2, stem_num2)

    return section1_max, section1_min, section2_max, section2_min, HHI_FOMC1, HHI_FOMC2, model_FOMC1, model_FOMC2



