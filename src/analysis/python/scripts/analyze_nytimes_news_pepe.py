import pandas as pd
from nltk.corpus import stopwords
import pprint
def main():
    df = pd.read_csv("../../../collection/python/data/news_data.csv",
                     names=['date','headline','category','text'])
    df['date'] = pd.to_datetime(df['date'],format="%Y%m%d")
    df = df[['date','headline','category','text']]
    #print(df)
    words = []
    print("df contains {} articles".format(len(df)))
    keyword_counts = {}
    missing = []
    for index,row in df.iterrows():
        if type(row['text'])==str:
            text = row['text'].lower()
        terms = ["federal open market committee",
                        "open market committee",
                        "federal reserve",
                        "federal funds rate",
                        "fomc"]
        in_text = False
        for term in terms:
            if term in text:
                in_text = True
        if in_text:
            missing.append(row['text'])
        for word in text.split():
            if word not in stopwords.words('english'):
                words.append(word)

    freq_counts = {}
    for word in words:
        if word in freq_counts:
            freq_counts[word] += 1
        else:
            freq_counts[word] = 1

    sorted_freq = sorted(freq_counts.items(), key=lambda x: x[1])
    sorted_keyword_counts = sorted(keyword_counts.items(), key=lambda x: x[1])

    #pprint.pprint(sorted_freq)
    #pprint.pprint(sorted_keyword_counts)
    print(len(missing))
    pprint.pprint(missing)
main()