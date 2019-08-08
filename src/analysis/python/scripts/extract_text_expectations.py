import os
import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt
#'expectation','inflation','unemployment','rates','market expectations',
#                  'federal funds rate',

def main():
    df = load_news()
    for i in df.index:
        raw_text = str(df.loc[i,'raw_text']).replace("\\","").lower()
        #print(raw_text)
        sentences = raw_text.split(". ")
        topics = ['surpris','uncertain','unexpected','not expect']
        df.loc[i, 'sentences'] = ". ".join(sentences)
        df.loc[i, 'sentence_counts'] = len(sentences)
        for topic in topics:
            if topic in "".join(sentences):
                topic_sents = []
                for sentence in sentences:
                    if topic in sentence and not is_negated(sentence.split(),topic):
                        topic_sents.append(sentence)
                df.loc[i, "d_" + topic.replace(" ", "_")] = 1
                df.loc[i, 'sent_' + topic.replace(" ", "_")] = ". ".join(topic_sents)
    df['n_article'] = 1
    export_news(df,topics)

def export_bluebook(df,topics):

    df = df.sort_values(by="date")
    df.to_csv("../output/bluebook_text_expectations.csv")

def export_news(df,topics):
    grp = df.groupby('date').sum()
    grp['score'] = 0
    grp['month'] = pd.to_datetime(grp.index).month
    grp['year'] = pd.to_datetime(grp.index).year
    for topic in topics:
        score_col = 'std_'+topic.replace(" ","_")
        grp[score_col] = np.divide(grp["d_"+topic.replace(" ","_")],grp['n_article'])
        grp['score'] += grp[score_col]
    grp['score'] = grp['score']/len(topics)
    grp.to_csv("../output/news_text_expectations.csv")
    df.to_csv("../output/news_text_expectations_sentences.csv")
def is_negated(words,word):
    negation = ['no','not','lack','wasn','didn']
    word_indexes = []
    for index,cur_word in enumerate(words):
        if word in cur_word:
            word_indexes.append(index)
    for word_index in word_indexes:
        for window in range(1,4):
            if word_index-window>0:
                if words[word_index-window] in negation:
                    return True
    return False
def load_bluebook():
    dir = "../../../collection/python/output/bluebook_raw_text"
    df = pd.DataFrame()
    for file in os.listdir(dir):
        with open(dir + "/" + file) as f:
            text = " ".join(f.read().split())
            df = df.append({'date': file.replace(".txt", ""), 'raw_text': text}, ignore_index=True)
    return df
def load_news():
    df = pd.read_csv("../../../collection/python/output/news_articles.csv")
    df['date'] = pd.to_datetime(df['meeting_date'])
    df['raw_text'] = df['content']
    return df[['date','raw_text']]
if __name__ == "__main__":
    main()