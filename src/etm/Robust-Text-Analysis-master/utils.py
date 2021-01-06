import nltk
from nltk.collocations import *
import matplotlib.pyplot as plt
from Constant import PLOT_PATH
import os

def bigrams(big_document):
    ignored_words = nltk.corpus.stopwords.words('english')
    ignored_words.append('percent')
    ignored_words.append('governor')
    ignored_words.append('dont')
    # bigram_measures = nltk.collocations.BigramAssocMeasures()

    finder = BigramCollocationFinder.from_documents(big_document)
    finder.apply_word_filter(lambda w: len(w) < 3 or w.lower() in ignored_words)
    finder.apply_freq_filter(150)

    return [' '.join(x) for x in list(finder.ngram_fd.keys())]


def trigram(big_document):
    ignored_words = nltk.corpus.stopwords.words('english')
    ignored_words.append('percent')
    ignored_words.append('governor')
    ignored_words.append('dont')
    # trigram_measures = nltk.collocations.TrigramAssocMeasures()

    finder = TrigramCollocationFinder.from_documents(big_document)
    finder.apply_word_filter(lambda w: len(w) < 3 or w.lower() in ignored_words)
    finder.apply_freq_filter(100)

    return [' '.join(x) for x in list(finder.ngram_fd.keys())]


def replace_collocation(string, dict_collocation):
    for key in dict_collocation.keys():
        string = string.replace(key, dict_collocation[key])

    return string

def plot_word_cloud(text, filename='wordcloud.eps', format='eps',
                    width=1000, height=500, background_color='white', figsize=(10,6), dpi=100, bbox_inches='tight'):
    from wordcloud import WordCloud

    meeting_string = (" ").join([word for line in text for word in line])
    wordcloud = WordCloud(width=width, height=height, background_color=background_color).generate(meeting_string)
    fig = plt.figure(figsize=figsize)
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    plt.imshow(wordcloud)
    plt.axis("off")
    fig.tight_layout()
    plt.savefig(os.path.join(PLOT_PATH, filename), format=format, dpi=dpi, bbox_inches=bbox_inches)

