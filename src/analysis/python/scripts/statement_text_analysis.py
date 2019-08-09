import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
from nltk import word_tokenize
from nltk.corpus import stopwords
import re
import pprint
import math
import os
def main():
    statement_document_analysis()
    frequency_counts()
def frequency_counts():
    terms = ['inflation', 'demand', 'labor', 'price stability',
             'consumption', 'activity', 'investment', 'policy'
             ]
    statements = pd.read_csv("../../../collection/python/output/statement_data.csv")
    statements['date'] = pd.to_datetime(statements['end_date'])


    stop_words = stopwords.words('english')
    corpus_words = []
    for i in statements.index:
        raw_text = statements.loc[i,'file_text'].lower().replace("\n"," ").strip(",")
        sentences = raw_text.split(". ")
        for term in terms:
            term_sents = []
            term_words = []
            for sentence in sentences:
                if term in sentence:
                    term_sents.append(sentence)
            statements.at[i, term+"_sents"] = "|".join(term_sents)
            for sent in term_sents:
                for word in word_tokenize(sent):
                    #print(word)
                    if word.isalpha() and word not in stop_words:
                        corpus_words.append(word)
                        term_words.append(word)
            #print(term_words)
            statements.at[i,term+"_words"] = "|".join(term_words)
    corpus_counter = Counter(corpus_words)
    for term in terms:
        term_words = []
        for meeting_words in statements[term+"_words"]:
            term_words.extend(meeting_words.split("|"))
        term_counts = Counter(term_words)
        print(term.upper())
        pprint.pprint(term_counts)
        statements.loc[1,term+"_word_freqs"] = "{}:{}".format(term.upper(),str(term_counts))
    statements.to_csv("../output/statement_text_analysis/word_grouping_counts.csv")

def statement_document_analysis():
    if not os.path.exists("../output/statement_text_analysis/graphs"):
        os.mkdir("../output/statement_text_analysis")
        os.mkdir("../output/statement_text_analysis/graphs")
    terms = {
    "policy":"accommodative",
    "productivity":"robust",
    "inflation":"contained",
    "risks":"balanced",
    "firming":"measured",
    'increase': 'interest rates',
    'sustain':'economic expansion',
    'enhance':'economic expansion',
    'accommodate': 'monetary positions',
    'prolonging': 'economic expansion',
    'low': 'inflation environment',
    'fostering': 'economic outlook',
    'sustain': 'economic outlook',
    'symmetric': 'economic outlook',
    'strengthening': 'productivty',
    'easing': 'demand pressure',
    'eroded': 'confidence',
    'spending': 'weakened'
    }
    statements = pd.read_csv("../../../collection/python/output/statement_data.csv")
    statements['date'] = pd.to_datetime(statements['end_date'])
    for term in terms.keys():
        term_phrase = term+":"+terms[term]
        statements[term_phrase] = ((statements.file_text.str.contains(term))&
                                   (statements.file_text.str.contains(terms[term])))
        statements.sort_values(by="date",inplace=True)
        plt.plot(statements['date'],statements[term_phrase],'bo',markersize=1)
        plt.title(term_phrase)
        graph_path = "../output/statement_text_analysis/graphs/"+term_phrase.replace(":","_")+".png"
        if os.path.exists(graph_path):
            os.rmdir(graph_path)
        plt.savefig("../output/statement_text_analysis/graphs/"+term_phrase.replace(":","_")+".png")
    statements.to_csv("../output/statement_text_analysis/term_connections.csv")
    print(statements)
if __name__ == "__main__":
    main()