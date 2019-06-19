"""
@author: olivergiesecke
"""

###############################################################################
### Set packages ###

import pandas as pd
import re
import os
import matplotlib.pyplot as plt


from nltk.corpus import stopwords
import gensim
import gensim.corpora as corpora
from gensim.utils import simple_preprocess
from gensim.models.phrases import Phrases, Phraser
# spacy for lemmatization
from distutils.core import setup
from Cython.Build import cythonize
import spacy
from wordcloud import WordCloud
import numpy as np

###############################################################################
# Open points:
# 1) Handling of footnotes. Right now, they are mixed into sentence at the end 
# of the page. This interrupts the sentence that do not end at the end of the 
#page.
# 2) Think about the use of nltk for the extraction of the relevant information
# 3) Adjust the cloud of words to be more relevant to our objective.


# Do the merge with the news data
# Do the merge with the statements 


###############################################################################




### Define table output 
def create_table(data,name):
    # Output the table
    columnheaders=list(data[0].keys())[1:]
    keysofdict=list(data[0].keys())
    numbercolumns=len(data[0])
    with open("../output/summary_tables/"+name+".tex", "w") as f:
        f.write(r"\begin{tabular}{"+"l" + "".join("c" * (numbercolumns-1)) + "}\n")
        f.write("\\hline\\hline \n")
        f.write(" & "+" & ".join([x for x in columnheaders]) + " \\\ \n")    
        f.write("\\hline \n")
        # write data
        for idx,entry in enumerate(data):

            # Do formatting for specific tables 
            if name=="tab_aggsum":
                if idx==1:
                    f.write("\\addlinespace"+" \n")
                if idx==2:
                    f.write("\\textit{of which:} \\\ \n")
            if name=="tab_summary_count":
                if idx==1:
                    f.write("\\addlinespace"+" \n")
                    
            entries=[]
            for key in keysofdict:
                entries.append(str(entry[key]))
            f.write(" & ".join(entries) + " \\\ \n")
        f.write("\\hline \n")
        f.write(r"\end{tabular}")


    
### Define data download
def getdata_bluebook():
    # Get all files except the hidden
    doc_list=[]
    for item in os.listdir("../output/raw_bluebook/"):
        if not item.startswith('.'):
            doc_list.append(item)
    
    files=[]
    for idx,doc in enumerate(doc_list):
        print(idx," Working on file", doc)
        # Do for specific document
        #doc=doc_list[20]
        
        # Open the file
        with open("../output/raw_bluebook/"+doc,'r') as f:
            # Read document line by line
            lines=f.readlines()
        
            cleaned_lines=[]
            for line in lines:
                # Replace linebreaks with space
                line=line.replace("\n"," ")
                # Remove empty lines 
                if not re.match(r'^\s*$', line):
                    #Remove four character lines that do not end with period
                    #regex = r".{1,4}(?<!\.)$"
                    #if not re.match(regex, line):
                    cleaned_lines.append(line)
            # Make a single element from list.
            text="".join(cleaned_lines)            
        
        # Search for alternative(s) and keep the sentence
        all_sentences=[]
        pattern = "([^.]*)(alternatives?\s+[a-e])(\.|[^a-z]\.|[^a-z][^\.]+\.)"
        regex = re.compile(pattern, re.IGNORECASE)
        for match in regex.finditer(text):
            all_sentences.append(match.group())
            
        data={"meeting_date":doc[:-4],"n_sentences":len(all_sentences),"sentences":all_sentences}
        
        # Search for alternative {a,b,c,d,e} and keep the sentence
        for alt in ["a","b","c","d","e"]:
            alt_sentences=[]
            pattern = "([^.]*)(alternative\s+"+alt+")(\.|[^a-z]\.|[^a-z][^\.]+\.)"
            regex = re.compile(pattern, re.IGNORECASE)
            for match in regex.finditer(text):
                alt_sentences.append(match.group())
            alt_sent="alt_"+alt+"_sentences"
            alt_count="alternative_"+alt+"_count"
            data.update({alt_sent:alt_sentences,alt_count:len(alt_sentences)})
    
        # Collect all files in the data file
        files.append(data)            
        
    # Collect output in dataframe
    return pd.DataFrame(files)

### Create cloud of words

def remove_stopwords(words,stopwords):
    nostopwords=[]
    for word in words:
        if word not in stopwords:
            nostopwords.append(word)        
    return nostopwords
    
def lemmatization(texts, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV']):
    """https://spacy.io/api/annotation"""
    texts_out = []
    # Initialize spacy 'en' model, keeping only tagger component (for efficiency)
    # python3 -m spacy download en
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(" ".join(texts)) 
    texts_out.append([token.lemma_ for token in doc if token.pos_ in allowed_postags])
    return texts_out
    

def create_cloudwords(sentences,name):
    stop_words = stopwords.words('english')
       
    # Manual extraction of words
    data_man="".join(sentences)
    words_man=data_man.replace(".", " ")
    
    # Gensium extraction of words
    def sent_to_words(sentences):
        for sentence in sentences:
            yield(gensim.utils.simple_preprocess(str(sentence), deacc=True))  # deacc=True removes punctuations
    
    wordsperphrase = list(sent_to_words(sentences))
    words_model=[]
    for phrase in wordsperphrase:
        for word in phrase:
            words_model.append(word)
        
    # Do some simple comparison
    print("Manual word count: ",len(words_man))
    print("Model word count: ",len(words_model))
    
    # Assign the words
    data_words=words_model
        
    # Remove Stop Words
    data_words_nostops = remove_stopwords(data_words,stop_words)
    
    # Do lemmatization keeping only noun, adj, vb, adv
    data_lemmatized = lemmatization(data_words_nostops, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV'])
     
# =============================================================================
#     # Define functions for stopwords, bigrams, trigrams and lemmatization
#     # Build the bigram and trigram models
#     bigram = Phrases(data_lemmatized[0], min_count=1, threshold=0.1) # higher threshold fewer phrases.
#     trigram = Phrases(bigram[data_lemmatized[0]], threshold=.1)  
#     
#     bigram_mod = Phraser(bigram)  # construct faster model (this is only an wrapper)
#     bigram_mod[data_lemmatized[0]]  # apply model to sentence
#     
#     print("original",len(data_lemmatized[0]),"processed",len(bigram_mod[data_lemmatized[0]]))
#     
# =============================================================================
    
    wordcloud = WordCloud(width = 1600, height = 1600, 
                    background_color ='white', 
                    min_font_size = 10).generate(" ".join(data_lemmatized[0])) 
      
    # plot the WordCloud image                        
    plt.figure(figsize = (8, 8), facecolor = None) 
    plt.imshow(wordcloud) 
    plt.axis("off") 
    plt.show() 
    
    plt.savefig("../output/summary_tables/"+name+".png")
    

###############################################################################

### Read data and define sample ###
df_output=getdata_bluebook()
df_output['year']=pd.to_numeric(df_output['meeting_date'].str[:4])
df_output['date']=pd.to_datetime(df_output['meeting_date'])
df_result=df_output[(df_output['date']<="2009-03-18") & (df_output['date']>="1968-08-13")]
# Write data frame to csv
df_result.to_csv("../output/bluebook_alternatives_og.csv")

keywords_ease=["lower","cut","cuts","decline","reduction","ease","reduce","easing"]
keywords_unchanged=["keep","unchanged","no change","maintained","maintain","remain","forego","continue"]
keywords_tighten=["raise","hike","raised","firm","firming","increase","tightening","rise","tighten","tighter"]

for alt in ["a","b","c","d","e"]:
    df_result.loc[:,"alt_"+alt+"_class"]=""
    ### Keyword classification
    for idx,row in df_result.iterrows():
        sentences=row["alt_"+alt+"_sentences"]
        #sentences=df_result[df_result['date']=="2006-12-12"]["alt_c_sentences"].item()
        keep_sentences=[]
          
        for sentence in sentences:
            pattern = "(alternatives?\s+[^"+alt+"])([^a-z])"
            if not re.search(pattern,sentence,re.IGNORECASE):
                keep_sentences.append(sentence)        
                    
        # Do counts for each keyword
        if len(keep_sentences)==0:
            df_result.loc[df_result['date']==row['date'],"alt_"+alt+"_class"]="No sentence"
        else:
            count_ease=0
            count_unchanged=0
            count_tighten=0
            for sentence in keep_sentences:
                
                for keyword in keywords_ease:
                    pattern = "[^a-z]"+keyword+"[^a-z]"
                    regex=re.compile(pattern,re.IGNORECASE)
                    for match in regex.finditer(sentence):
                        count_ease+=1
                        #print(match.group())
                
                for keyword in keywords_unchanged:
                    pattern = "[^a-z]"+keyword+"[^a-z]"
                    regex=re.compile(pattern,re.IGNORECASE)
                    for match in regex.finditer(sentence):
                        count_unchanged+=1
                        #print(match.group())                
                        
                for keyword in keywords_tighten:
                    pattern = "[^a-z]"+keyword+"[^a-z]"
                    regex=re.compile(pattern,re.IGNORECASE)
                    for match in regex.finditer(sentence):
                        count_tighten+=1
                        #print(match.group())
            #print("ease: ",count_ease,"unchanged: ",count_unchanged,"tighten:",count_tighten)
            
            counts=[count_ease,count_unchanged,count_tighten]
            new_count=[]
            if 0 in counts:
                new_count=counts.copy()
                new_count.remove(0)
            else:
                new_count=counts.copy()
            
            d_conflict=0
            if len(new_count)>=2:
                if sorted(new_count)[-1]==sorted(new_count)[-2]:
                    d_conflict=1

            
            sum_counts=sum(counts)
            labels=["ease","unchanged","tighten"]
            if not sum_counts==0 and not d_conflict==1:
                index_max = np.argmax([count_ease,count_unchanged,count_tighten])
                #print(labels[index_max])
                df_result.loc[df_result['date']==row['date'],"alt_"+alt+"_class"]=labels[index_max]
            else:
                df_result.loc[df_result['date']==row['date'],"alt_"+alt+"_class"]="No assignment"
      
df_result.sort_values('date', inplace=True)
# Get output for individual years
alternative="b"
year=2006
df_result[df_result['year']==year][['year','date',"alt_"+alternative+"_class"]]

start_year=1994
end_year=1999
pd.pivot_table(df_result[(df_result['year']>=start_year) & (df_result['year']<=end_year)],'date',index=['alt_'+alternative+'_class'], \
               aggfunc=np.count_nonzero)
pd.pivot_table(df_result[df_result['year']>=start_year],'date',index=['alt_'+alternative+'_class'], \
               columns=['year'],aggfunc=np.count_nonzero)

# Check the no assignment cases
df_result[(df_result["alt_"+alternative+"_class"]=="No assignment") &  \
          (df_result['year']>=start_year) & (df_result['year']<=end_year)] \
          ["alt_"+alternative+"_sentences"].iloc[3]
