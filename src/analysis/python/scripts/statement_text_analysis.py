import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
from nltk import word_tokenize
from nltk.corpus import stopwords
import re
import pprint
import math
import os
import shutil
def main():
    statement_document_analysis()
    frequency_counts()
def frequency_counts():
    cwd = "../output/statement_text_analysis/"
    terms = ['risk','risks'
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
    statements.to_csv(cwd+"word_grouping_counts.csv")

def statement_document_analysis():
    cwd = "../output/statement_text_analysis/"
    if os.path.exists(cwd):
        shutil.rmtree(cwd)
    if not os.path.exists(cwd):
        os.mkdir(cwd)
        os.mkdir(cwd+"graphs")
    terms = [
                ['risks','inflation'],
                ['risks','committee'],
                ['risks','upside'],
                ['risks','downside'],
                ['risks','balanced'],
                ['risks','unbalanced']
    ]
    print(terms)
    statements = pd.read_csv("../../../collection/python/output/statement_data.csv")
    statements['date'] = pd.to_datetime(statements['end_date'])
    for term in terms:
        term_1 = term[0]
        term_2 = term[1]
        term_phrase = term_1+":"+term_2
        statements[term_phrase] = ((statements.file_text.str.contains(term_1))&
                                   (statements.file_text.str.contains(term_2)))
        statements.sort_values(by="date",inplace=True)
        plt.plot(statements['date'],statements[term_phrase],'bo',markersize=1)
        plt.title(term_phrase)
        graph_path = cwd+"graphs/"+term_phrase.replace(":","_")+".png"
        if os.path.exists(graph_path):
            os.rmdir(graph_path)
        plt.savefig(graph_path)
    statements.to_csv(cwd+"term_connections.csv")
    #print(statements)
if __name__ == "__main__":
    main()