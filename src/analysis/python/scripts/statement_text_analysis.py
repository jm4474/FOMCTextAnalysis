import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
from nltk import word_tokenize,bigrams,collocations
from nltk.corpus import stopwords
import re
import pprint
import math
def main():
    statements = pd.read_csv("../../../collection/python/output/statement_data.csv")
    statements['date'] = pd.to_datetime(statements['end_date'])

    terms = ['inflation', 'demand', 'labor', 'price stability',
             'consumption', 'activity', 'investment', 'policy'
             ]
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

    statements.to_csv("statement_terms.csv")

def statement_document_analysis():
    statements = pd.read_csv("../../../collection/python/output/statement_data.csv")
    statements['date'] = pd.to_datetime(statements['end_date'])
    for term in terms.keys():
        term_phrase = term+":"+terms[term]
        statements[term_phrase] = ((statements.file_text.str.contains(term))&
                                   (statements.file_text.str.contains(terms[term])))
        statements.sort_values(by="date",inplace=True)
        plt.plot(statements['date'],statements[term_phrase],'bo')
        plt.title(term_phrase)
        plt.show()
    print(statements)
if __name__ == "__main__":
    main()