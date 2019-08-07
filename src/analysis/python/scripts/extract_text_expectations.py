import os
import pandas as pd
import re
#'expectation','inflation','unemployment','rates','market expectations',
#                  'federal funds rate',

def main():
    df = load_news()
    for i in df.index:
        raw_text = df.loc[i,'raw_text']
        sentences = raw_text.split(". ")
        exp_sents = [sentence+'.' for sentence in sentences]
        topics = ['surprise']
        if exp_sents:
            df.loc[i, 'sentences'] = "\n".join(exp_sents)
            df.loc[i, 'sentence_counts'] = str(len(exp_sents))
            for topic in topics:
                if topic in "".join(exp_sents):
                    topic_sents = []
                    for sentence in exp_sents:
                        if topic in sentence:
                            topic_sents.append(sentence)
                    df.loc[i, "d_" + topic.replace(" ", "_")] = 1
                    df.loc[i, 'sent_' + topic.replace(" ", "_")] = "\n".join(topic_sents)
    df['n_article'] = 1
    grp = df.groupby('date').sum()
    grp['month'] = pd.to_datetime(grp.index).month
    grp['year'] = pd.to_datetime(grp.index).year
    grp['std_surprise'] = grp['d_surprise']/grp['n_article']
    grp.to_csv("../output/news_text_expectations.csv")
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