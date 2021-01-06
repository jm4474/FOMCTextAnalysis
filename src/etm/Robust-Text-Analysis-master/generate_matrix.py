import pandas as pd
from Constant import *
import numpy as np
import gensim
from gensim import corpora, models
import matplotlib.pyplot as plt
from utils import plot_word_cloud
import pickle

def generate_term_document_interjection(option=None, tf_idf_threshold=9000):
    '''
    option = 'text' or 'matrix' for return options

    '''
    data = pd.read_excel(os.path.join(CACHE_PATH,'FOMC_token_separated_col.xlsx'))
    texts = []
    for line in data['content'].fillna(' ').values:
        texts.append(line.split(' '))

    dictionary = corpora.Dictionary(texts)
    corpus = [dictionary.doc2bow(text) for text in texts]

    term_document2 = gensim.matutils.corpus2dense(corpus, num_terms=len(dictionary.keys()))

    TF = 1 + np.log(term_document2.sum(axis=1))
    IDF = np.log(term_document2.shape[1] / np.count_nonzero(term_document2, axis=1))

    TF_IDF = pd.Series(dict(zip(dictionary.keys(), TF * IDF)))

    keys_to_use2 = TF_IDF.sort_values(ascending=False)[:tf_idf_threshold].index.values

    TF_IDF.sort_values(ascending=False).reset_index()[0].plot()
    plt.savefig(os.path.join(PLOT_PATH,'TF_IDF_interjection.png'))

    dictionary.filter_tokens(good_ids=keys_to_use2)

    pd.Series(dictionary.token2id).to_excel(os.path.join(MATRIX_PATH,'dictionary_interjection.xlsx'))

    new_text = []
    for line in texts:
        new_text.append([x for x in line if x in dictionary.token2id.keys()])

    new_corpus2 = [dictionary.doc2bow(text) for text in texts]
    new_term_document2 = gensim.matutils.corpus2dense(new_corpus2, num_terms=len(dictionary.keys()))

    pd.DataFrame(new_term_document2).to_excel(os.path.join(MATRIX_PATH,'Matrix_interjection_tfidf.xlsx'))

    if option == 'text':
        return new_text
    elif option == 'matrix':
        return new_term_document2
    else:
        return None

def generate_term_document_meeting(option=None, tf_idf_threshold=[9000,6000]):
    '''
    option = 'text' or 'matrix' for return options

    '''

    data = pd.read_excel(os.path.join(CACHE_PATH,'FOMC_token_separated_col.xlsx'))
    data = data.dropna()

    meeting_text_both = []
    term_document_both = []
    for section in [1,2]:
        meeting_text = []
        for meeting in data['Date'].unique():
            meeting_text.append(' '.join(
                data.groupby('Date').get_group(meeting).groupby('Section').get_group(section)['content'].values).split(' '))

        dictionary = corpora.Dictionary(meeting_text)
        corpus = [dictionary.doc2bow(text) for text in meeting_text]

        term_document = gensim.matutils.corpus2dense(corpus, num_terms=len(dictionary.keys()))

        TF = 1 + np.log(term_document.sum(axis=1))
        IDF = np.log(term_document.shape[1] / np.count_nonzero(term_document, axis=1))

        TF_IDF = pd.Series(dict(zip(dictionary.keys(), TF * IDF)))

        if section == 1:
            N = tf_idf_threshold[0]
            color = 'b'
        if section == 2:
            N = tf_idf_threshold[1]
            color = 'r'

        keys_to_use = TF_IDF.sort_values(ascending=False)[:N].index.values

        TF_IDF.sort_values(ascending=False).reset_index()[0].plot(c=color)
        plt.xlabel('TF-IDF rank')
        plt.ylabel('TF-IDF score')
        plt.axvline(N, linestyle='--', color=color)

        dictionary.filter_tokens(good_ids=keys_to_use)

        pd.Series(dictionary.token2id).to_excel(os.path.join(MATRIX_PATH,'FOMC{}_dictionary_meeting.xlsx'.format(section)))

        text = []
        for line in meeting_text:
            text.append([x for x in line if x in dictionary.token2id.keys()])

        new_corpus = [dictionary.doc2bow(text) for text in meeting_text]
        new_term_document = gensim.matutils.corpus2dense(new_corpus, num_terms=len(dictionary.keys()))

        print('Writing term-document matrix to {}'.format(os.path.join(MATRIX_PATH, 'FOMC' + str(section) + '_meeting_matrix.xlsx')))
        pd.DataFrame(new_term_document).to_excel(os.path.join(MATRIX_PATH, 'FOMC' + str(section) + '_meeting_matrix.xlsx'))
        with open(os.path.join(MATRIX_PATH, 'FOMC{}_text.pkl'.format(section)), 'wb') as f:
            pickle.dump(text, f)
        term_document_both.append(new_term_document)
        meeting_text_both.append(text)
    plt.savefig(os.path.join(PLOT_PATH, 'TF_IDF_meeting.png'))
    if option == 'text':
        return meeting_text_both
    elif option == 'matrix':
        return term_document_both
    else:
        return None


def generate_tf_only_matrix(tf_idf_threshold=[9000,6000], additional_stop_words = [], option=None):
    data = pd.read_excel(os.path.join(CACHE_PATH,'FOMC_token_separated_col.xlsx'))
    data = data.dropna()

    meeting_text_both = []
    term_document_both = []
    for section in [1,2]:
        meeting_text = []
        for meeting in data['Date'].unique():
            meeting_text.append(' '.join(
                data.groupby('Date').get_group(meeting).groupby('Section').get_group(section)['content'].values).split(' '))

        dictionary = corpora.Dictionary(meeting_text)

        bad_id = []
        for word in dictionary.token2id.keys():
            if word in additional_stop_words:
                bad_id.append(dictionary.token2id[word])

        dictionary.filter_tokens(bad_ids=bad_id)
        corpus = [dictionary.doc2bow(text) for text in meeting_text]

        term_document = gensim.matutils.corpus2dense(corpus, num_terms=len(dictionary.keys()))

        TF = term_document.sum(axis=1)

        TF = pd.Series(dict(zip(dictionary.keys(), TF)))


        if section == 1:
            N = tf_idf_threshold[0]
            color = 'b'
        if section == 2:
            N = tf_idf_threshold[1]
            color = 'r'

        keys_to_use = TF.sort_values(ascending=False)[:N].index.values

        TF.sort_values(ascending=False).reset_index()[0].plot(c=color)
        plt.xlabel('TF-IDF rank')
        plt.ylabel('TF-IDF score')
        plt.axvline(N, linestyle='--', color=color)

        dictionary.filter_tokens(good_ids=keys_to_use)

        pd.Series(dictionary.token2id).to_excel(os.path.join(MATRIX_PATH,'FOMC{}_dictionary_meeting_onlyTF.xlsx'.format(section)))

        text = []
        for line in meeting_text:
            text.append([x for x in line if x in dictionary.token2id.keys()])

        new_corpus = [dictionary.doc2bow(text) for text in meeting_text]
        new_term_document = gensim.matutils.corpus2dense(new_corpus, num_terms=len(dictionary.keys()))

        print('Writing term-document matrix to {}'.format(os.path.join(MATRIX_PATH, 'FOMC' + str(section) + '_meeting_matrix_onlyTF.xlsx')))
        pd.DataFrame(new_term_document).to_excel(os.path.join(MATRIX_PATH, 'FOMC' + str(section) + '_meeting_matrix_onlyTF.xlsx'))
        with open(os.path.join(MATRIX_PATH, 'FOMC{}_text_onlyTF.pkl'.format(section)), 'wb') as f:
            pickle.dump(text, f)
        term_document_both.append(new_term_document)
        meeting_text_both.append(text)
    plt.savefig(os.path.join(PLOT_PATH, 'TF_IDF_meeting_onlyTF.png'))
    if option == 'text':
        return meeting_text_both
    elif option == 'matrix':
        return term_document_both
    else:
        return None


stop_words = ['think','chairman','presid','governor',
               'number','question','will','may',
               'point','right','mr','come','go',
                'want','thank','continu','percent',
                'seem','dont','im','littl','forecast',
                'look','might','chang','reflect',
                'encourag','cant','aw',
                'small','ad','caus','district',
                'best','like','guess','across',
                'find','substanti','cours','mayb',
                'recogn','doesnt','week','timemost',
                'impress','fraction','awri','depend',
                'last','accumul','line','certainli',
                'wouldsayxx','term','analysi','retailsalesxx',
                'productiondo','time',
                'youd','saw','economi','view','know',
                'sort','theyr','talk','give','illustr',
                'try','upward','your','kiss','particularli',
                'can','geograph','revis','chart','possibl',
                'suppos','today','committee','necessarili',
                'persian','gyrat','wonthat',
                'thing','that','realli','weve',
                'peopl','much','lot','year','weakest','affair',
                'what','figur']

if __name__ == '__main__':
    text1, text2 = generate_tf_only_matrix(option='text', tf_idf_threshold=[200, 150], additional_stop_words=stop_words)
    plot_word_cloud(text1, filename='WordCloud_FOMC1_onlyTF.png', format=None)
    plot_word_cloud(text2, filename='WordCloud_FOMC2_onlyTF.png', format=None)
