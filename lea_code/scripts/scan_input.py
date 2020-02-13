import os
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer

def make_scan_input(ftype):
    file_path = "../data/{}_raw_text/preprocessed/".format(ftype)
    outfile = "../data/scan_input/{}.txt".format(ftype)
    with open(outfile, 'w+') as of:
        for ff in sorted(os.listdir(file_path)):
            if ff.endswith(".txt"):
                print("processing {}".format(ff))
                sentences = open(os.path.join(file_path, ff)).read().split("\n\n")
                year = ff.split('-')[0]
                for sentence in sentences:
                    words = [w.split('\t')[1].lower() for w in sentence.split('\n') if w.split('\t')[6] == "False" and w.split('\t')[2] != "PUNCT"]
                    if len(words) > 5:
                        of.write("{}\t{}\n".format(year, ' '.join(words)))


def sort_coo(coo_matrix):
    tuples = zip(coo_matrix.col, coo_matrix.data)
    return sorted(tuples, key=lambda x: (x[1], x[0]), reverse=True)

def extract_topn_from_vector(feature_names, sorted_items, topn=10):
    """get the feature names and tf-idf score of top n items"""
    
    #use only topn items from vector
    sorted_items = sorted_items[:topn]
 
    score_vals = []
    feature_vals = []
    
    # word index and corresponding tf-idf score
    for idx, score in sorted_items:
        
        #keep track of feature name and its corresponding score
        score_vals.append(round(score, 3))
        feature_vals.append(feature_names[idx])
 
    #create a tuples of feature,score
    #results = zip(feature_vals,score_vals)
    results= {}
    for idx in range(len(feature_vals)):
        results[feature_vals[idx]]=score_vals[idx]
    
    return results

def word_counts(ftype):
    docs = {}
    docfile =  open("../data/scan_input/{}.txt".format(ftype), 'r')
    for line in docfile.readlines():
        year=line.strip().split("\t")[0]
        txt=line.strip().split("\t")[1]
        if year not in docs:
            docs[year]=[]
        else:
            docs[year].append(txt)

    counts = CountVectorizer()
    global_counts = counts.fit_transform([' '.join(doc) for doc in docs.values()])
    
    for target in list(docs.keys()):
        train_docs = [' '.join(tdocs) for time, tdocs in docs.items() if time != target]
        test_doc = ' '.join(docs[target])

        tfidf = TfidfVectorizer()
        tfidf.fit_transform(train_docs)
        feature_names=tfidf.get_feature_names()
        
        test_tfidf=tfidf.transform([test_doc])
        sorted_items=sort_coo(test_tfidf.tocoo())
        keywords=extract_topn_from_vector(feature_names,sorted_items,50)
        
        print(target, keywords)

if __name__ == "__main__":
    counts = make_scan_input("statement")
    word_counts("statement")
