from Constant import *
from utils import bigrams, trigram, replace_collocation
from tika import parser
import re
import timeit
import os
import pandas as pd
import string

import topicmodels
from nltk.stem import PorterStemmer

def generate_raw_data():
    """
    This function generates raw text data from FOMC transcripts

    returns a list where each element is the full text within each FOMC meeting

    It will take about 4-5 minutes
    """

    raw_doc = os.listdir(PDF_PATH)  # as above
    filelist = sorted(raw_doc)  # sort the pdfs in order
    onlyfiles = [f for f in raw_doc if os.path.isfile(os.path.join(PDF_PATH, f))]  # keep if in correct dir
    date = [f[4:10] for f in onlyfiles]  # keep the dates in pdfs

    raw_text = pd.DataFrame(columns=['Date', 'Speaker', 'content'])  # empty dataframe

    start = timeit.default_timer()
    for i, file in enumerate(filelist):
        print('Document {} of {}: {}'.format(i, len(filelist), file))

        parsed = parser.from_file(os.path.join(cwd, 'FOMC_pdf', file))  # parse the pdf
        interjections = re.split('\nMR. |\nMS. |\nCHAIRMAN |\nVICE CHAIRMAN ', parsed[
            'content'])  # split the entire string by the names (looking for MR, MS, Chairman or Vice Chairman)
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

        temp_df['Date'] = date[i]
        raw_text = pd.concat([raw_text, temp_df], ignore_index=True)

    end = timeit.default_timer()
    raw_text.index = raw_text['Date']  # set dataframe index to the Date
    raw_text.to_excel(os.path.join(CACHE_PATH,'raw_text.xlsx'))  # save as raw_text.xlsx

    print("Documents processed. Time: {}".format(end - start))
    print("Cache Location: {}".format(os.path.join(CACHE_PATH, 'raw_text.xlsx')))


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


def tokenize(content):
    '''
    Code for tokenization:
        1. remove words with length of 1
        2. remove non-alphabetical words
        3. remove stop words
        4. stem all words
    '''
    FOMC_token = []
    for i,statement in enumerate(content):
        statement = statement.lower()
        docsobj = topicmodels.RawDocs([statement], "long")
        docsobj.token_clean(1)
        # remove months, "unintelligible"
        additional_stopword = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september',
                               'october', 'november', 'december', 'unintelligible']
        for word in additional_stopword:
            docsobj.stopwords.add(word)
        firstname = pd.read_excel(os.path.join(UTILFILE_PATH,'firstnames.xlsx'))
        firstname_list = firstname['First name'].dropna().values
        for firstname in firstname_list:
            docsobj.stopwords.add(firstname.lower())
        docsobj.stopword_remove("tokens")
        docsobj.stem()
        docsobj.stopword_remove("stems")
        ps = PorterStemmer()
        FOMC_token.append(' '.join([ps.stem(word) for word in docsobj.tokens[0]]))

    return FOMC_token



def find_collocation(raw_text_separated):
    content = raw_text_separated['content'].apply(lambda x: re.sub(r'[^\w\s]', '', x))  # remove punctuations

    big_document = content.apply(lambda x: x.split(' ')).values

    bigram_list = bigrams(big_document)
    trigram_list = trigram(big_document)

    replace_word = ['_'.join(x.split(' ')) for x in bigram_list] + ['_'.join(x.split(' ')) for x in trigram_list]
    dict_collocation = dict(zip(bigram_list + trigram_list, replace_word))

    content = content.apply(lambda x: replace_collocation(x, dict_collocation))

    raw_text_separated['content'] = content
    raw_text_separated.to_excel(os.path.join(CACHE_PATH,'FOMC_separated_collocation.xlsx'))
    return raw_text_separated


def preprocess():
    '''
    main function for preprocessing

    This function writes the tokenized documents, which includes columns of
    Date: date of the meeting
    Section: FOMC1 or FOMC2
    Speaker: speaker of the interjection
    content: list of tokens in the interjection

    '''

    text = pd.read_excel(os.path.join(CACHE_PATH,'raw_text.xlsx'))

    print('Separating FOMC1 and FOMC2')
    start = timeit.default_timer()
    text_separated = separation(text)
    end = timeit.default_timer()
    print('Finished. Time: {}'.format(end - start))
    print('******************************************************************************')

    # text_separated_col = text_separated
    print('Tokenize content')
    start = timeit.default_timer()
    text_separated['content'] = tokenize(text_separated['content'].values)
    end = timeit.default_timer()
    print('Finished. Time: {}'.format(end - start))
    print('******************************************************************************')

    print('Generate collocation')
    start = timeit.default_timer()
    text_separated_col = find_collocation(text_separated)
    end = timeit.default_timer()
    print('Finished. Time: {}'.format(end - start))
    print('******************************************************************************')
    text_separated_col.to_excel(os.path.join(CACHE_PATH,'FOMC_token_separated_col.xlsx'))

if __name__ == '__main__':
    generate_raw_data()
    preprocess()
