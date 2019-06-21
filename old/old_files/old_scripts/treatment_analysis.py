import pandas as pd
import pprint
import numpy as np
import matplotlib.pyplot as plt
import csv
from gensim.parsing.preprocessing import \
    preprocess_string,strip_punctuation,\
    strip_multiple_whitespaces,strip_numeric, \
    remove_stopwords,stem_text, strip_non_alphanum,\
    strip_short
import math
def main():

    alternative_a = pd.read_excel("../../Matlab/Output/Bluebook/CSV/CommentedFiles/SentencesA_commented.xlsx")
    alternative_b = pd.read_excel("../../Matlab/Output/Bluebook/CSV/CommentedFiles/SentencesB_commented.xlsx")
    alternative_c = pd.read_excel("../../Matlab/Output/Bluebook/CSV/CommentedFiles/SentencesC_commented.xlsx")

    start = 349
    treatment_csv(alternative_a,alternative_b,alternative_c,start)
    #keyword_tf_idf(alternative_a,alternative_b,alternative_c,start)
    #all_sentence_tf_idf(alternative_a,alternative_b,alternative_c,start)

def treatment_csv(alternative_a,alternative_b,alternative_c,start):
    sentences = []
    for sent_df in [alternative_a, alternative_b, alternative_c]:
        for index, row in sent_df.iloc[start:].iterrows():
            if row['C_TREATMENT'] and row['C_TREATMENT'] in ['T', 'U', 'E'] \
                    and type(row['KEYWORDS_TREATMENT']) == str:
                treatment = row['C_TREATMENT']
                sentence = row['KEYWORDS_TREATMENT']
                sentence = {
                    'treatment':treatment,
                    'sentence':sentence
                }
                sentences.append(sentence)
    write_to_csv(sentences)
def write_to_csv(documents):
    with open('../output/treatment_sentences.csv', 'w') as csvfile:
        fieldnames = ['treatment','sentence']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for document in documents:
            writer.writerow(document)
def keyword_tf_idf(alternative_a,alternative_b,alternative_c,start):
    treatments = {
        'U': [],
        'T': [],
        'E': []
    }
    unique_words = {
        'U':set(),
        'T':set(),
        'E':set(),
    }
    all_words = []
    #For Treatment
    for sent_df in [alternative_a,alternative_b,alternative_c]:
        for index,row in sent_df.iloc[start:].iterrows():
            if row['C_TREATMENT'] and row['C_TREATMENT'] in ['T','U','E'] \
                    and type(row['KEYWORDS_TREATMENT']) == str:
                treatment = row['C_TREATMENT']
                sentence = row['KEYWORDS_TREATMENT']
                custom_filters = [lambda x: x.lower(), strip_punctuation,
                                  strip_multiple_whitespaces,strip_numeric,
                                  remove_stopwords, strip_non_alphanum,
                                  stem_text,strip_short]
                dictionary = preprocess_string(sentence,custom_filters)
                for word in dictionary:
                    treatments[treatment].append(word)
                    unique_words[treatment].add(word)
                    all_words.append(word)
    tf_idf_scores = {
        'U':{},
        'T':{},
        'E':{}
    }
    for treatment in treatments.keys():
        treatment_scores = tf_idf(treatment,treatments,unique_words[treatment])
        tf_idf_scores[treatment] = treatment_scores
    for treatment in tf_idf_scores.keys():
        print(treatment)
        scores = []
        for word_score in tf_idf_scores[treatment].items():
            if word_score[1] !=0:
                scores.append(word_score)
        scores = sorted(scores,key=lambda x:x[1],reverse=True)
        pprint.pprint(scores)


def all_sentence_tf_idf(alternative_a,alternative_b,alternative_c,start):
    sentence_columns = []
    sentence_range = range(1,13)
    for sent_num in sentence_range:
        sentence_columns.append("Sentence_"+str(sent_num))

    treatments = {
        'U': [],
        'T': [],
        'E': []
    }
    unique_words = {
        'U': set(),
        'T': set(),
        'E': set(),
    }
    all_words = []
    # For Treatment
    for alt_df in [alternative_a, alternative_b, alternative_c]:
        for index, row in alt_df.iloc[start:].iterrows():
            if row['C_TREATMENT'] and row['C_TREATMENT'] in ['T', 'U', 'E']\
                    and "No Sentences" not in row['Sentence_1']:
                treatment = row['C_TREATMENT']
                sentences = ""

                for col in sentence_columns:
                    if col in alt_df.columns and type(row[col])==str:
                        sentences += sentences+row[col]

                custom_filters = [lambda x: x.lower(), strip_punctuation,
                                  strip_multiple_whitespaces, strip_numeric,
                                  remove_stopwords, strip_non_alphanum
                                  ,stem_text,strip_short]
                dictionary = preprocess_string(sentences, custom_filters)
                for word in dictionary:
                    treatments[treatment].append(word)
                    unique_words[treatment].add(word)
                    all_words.append(word)
    all_sentence_tf_idf_scores = {
        'U': {},
        'T': {},
        'E': {}
    }
    for treatment in treatments.keys():
        all_sentence_tf_idf_scores[treatment] = tf_idf(treatment,treatments,unique_words[treatment])

    for treatment in all_sentence_tf_idf_scores.keys():
        print(treatment)
        scores = []
        for word_score in all_sentence_tf_idf_scores[treatment].items():
            if word_score[1] != 0:
                scores.append(word_score)
        scores = sorted(scores, key=lambda x: x[1], reverse=True)
        pprint.pprint(scores)

def tf_idf(document,documents,unique_words):
    scores = {}
    for term in unique_words:
        #print("Document is {} and term is {}".format(document, term))
        term_frequency = 0
        for doc_word in documents[document]:
            if term == doc_word:
                term_frequency+=1
        tf = term_frequency/len(document)
        #print("term frequency of {} is:{}".format(term,str(tf)))
        document_count = 0
        document_frequency = 0
        for document in documents:
            document_count += 1
            if term in documents[document]:
                document_frequency += 1
        idf = math.log(document_count/document_frequency)
        #print("idocument frequency is:"+str(idf))
        tf_idf = tf*idf
        #print("tf-idf is :"+str(tf_idf))
        scores[term] = tf_idf
    return scores


main()