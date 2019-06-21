#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Purpose: Uses the statement data to train a classifier and use the classifier 
         for the prediction of the alternatives in the bluebook from 1988-2008
Status: Draft
Author: olivergiesecke
"""

###############################################################################
### Import packages
import pandas as pd
import re
import os
from io import StringIO
import numpy as np
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import LinearSVC
from sklearn.model_selection import cross_val_score

###############################################################################

### Open the csv with the statements (note: this is the manual statement file)
data=pd.read_csv("../output/statements_text_extraction_cleaned.csv")
# Data stored in data['statement'] and data['policy_treatment']

## Clean Data
data=data[data['policy_treatment'].notna()][['statement','policy_treatment']]
print(len(data))
# 129 entries
## Create categorical variable for policy treatment
data['treatment_id'] = data['policy_treatment'].factorize()[0]
data.loc[:,'training']=True

## Create dictionaries to map from the categorical variable to string and vice versa
category_id_df = data[['policy_treatment', 'treatment_id']].drop_duplicates()\
    .sort_values('treatment_id')
category_to_id = dict(category_id_df.values)
id_to_category = dict(category_id_df[['treatment_id','policy_treatment']].values)

## Define function to reshape the sentences in the bluebooks
def transform_merged(merge_class_d_e):
    for alt in ['a','b','c','d','e']:
        merge_class_d_e['C_TREATMENT_SIZE_alt_'+ alt] = ""
        merge_class_d_e['Sentences_alt_'+alt] = ""
        sentence_columns = []
        for sentence_num in range(1, 12):
            col_name = 'Sentence_' + str(sentence_num) + "_alt_" + alt
            if col_name in merge_class_d_e and type(merge_class_d_e[col_name]=="str"):
                
                sentence_columns.append(col_name)
        #merge_class_d_e['Sentences_alt_'+alt] = merge_class_d_e[sentence_columns].apply(lambda row: ' '.join(row.values.astype(str)), axis=1)
        for index,row in merge_class_d_e.iterrows():
            sentence_content = []
            for sentence_col in sentence_columns:
                sentence = row[sentence_col]
                pattern = "(alternatives?\s+[^"+alt+"])([^a-z])"
                if type(sentence)==str and not re.search(pattern,sentence,re.IGNORECASE):
                    # and not re.search(pattern,sentence,re.IGNORECASE)
                    sentence_content.append(sentence)
            merge_class_d_e.at[index,'Sentences_alt_'+alt] = ' '.join(sentence_content)
    return merge_class_d_e


### Bluebooks
## Import the bluebook data
df_test=pd.read_excel("../output/validate_classifier_bluebook_FINAL.xlsx")
df_test=transform_merged(df_test)
df_test=df_test[["date","C_TREATMENT_alt_a","C_TREATMENT_alt_b","C_TREATMENT_alt_c",'Sentences_alt_a','Sentences_alt_b','Sentences_alt_c']]

## Clean the bluebooks
df_test=pd.wide_to_long(df_test, ["C_TREATMENT_alt", "Sentences_alt"] , "date", "alternative",sep="_",suffix="\w+")
df_test=df_test.reset_index()
df_test=df_test[df_test["C_TREATMENT_alt"].notna()]
df_test=df_test[df_test["C_TREATMENT_alt"]!="?"]
df_test=df_test[df_test["C_TREATMENT_alt"]!="N"]
df_test=df_test[df_test["C_TREATMENT_alt"]!="U?"]
df_test.sort_values("date",inplace=True)

letter_to_id={"E":0,"T":1,"U":2}

df_test.loc[:,"treatment_id"]=np.nan
for index,row in df_test.iterrows():
    treatment_id=letter_to_id[row["C_TREATMENT_alt"]]
    df_test.loc[index,"treatment_id"]=int(treatment_id)
df_test=df_test.rename({"Sentences_alt":"statement","C_TREATMENT_alt":"policy_treatment"},axis='columns')

### Merge the bluebooks and the statements
df_data=df_test.append(data,ignore_index=True)
df_data=df_data[df_data["statement"]!=""]
df_data.loc[df_data['training'].isna(),'training']=False

selection=np.array(df_data["training"]==True)
label=np.array(df_data["treatment_id"])

### Do standard characterization with TF-IDF
tfidf = TfidfVectorizer(sublinear_tf=True, min_df=5,norm='l2', encoding='latin-1', ngram_range=(1, 2),stop_words='english')
features = tfidf.fit_transform(df_data['statement']).toarray()
features.shape 
# yields 485 meetings with 2743 tokens

### Do prediction with different models
x_train=features[selection]
y_train=list(label[selection])

x_pred=features[~selection]
y_act=label[~selection]

models = [
            RandomForestClassifier(n_estimators=200, max_depth=3, random_state=0),
            LinearSVC(),
            LogisticRegression(random_state=0),
            ]

entries = []
for model in models:
    model_name = model.__class__.__name__
    model.fit(x_train, y_train)
    y_pred = model.predict(x_pred)
    accuracy=np.sum(y_pred == y_act) / len(label[~selection])
    entries.append((model_name, accuracy))

cv_df = pd.DataFrame(entries, columns=['model_name',  'accuracy'])
cv_df.groupby('model_name').accuracy.mean()


model = LogisticRegression()
model.fit(x_train, y_train)
y_pred = model.predict(x_pred)
# terrible performance

###############################################################################
## Get all words of the bluebook alternatives

from gensim.utils import simple_preprocess
from gensim.parsing.porter import PorterStemmer
from gensim.parsing.preprocessing import remove_stopwords
import collections
from numpy import linalg as LA


def clean_tex(dataframe,trainingsample,unique_words):
    counts=[]
    for idx,row in dataframe[dataframe['training']==trainingsample].iterrows():
        ## Do with one document in the training data
        sample_raw=row['statement']
        sample_clean=simple_preprocess(sample_raw, deacc=True)
        sample_clean_nostop=list(filter(None,[remove_stopwords(word) for word in sample_clean]))
        sample_stem=p.stem_documents(sample_clean_nostop)
        ## Get the count for each word
        counter = collections.Counter(sample_stem)
        voc_count=[]
        for word in unique_words:
            voc_count.append(counter[word])
        counts.append(voc_count)  
    return counts

raw_list=" ".join(df_data[df_data['training']!=1]['statement'].tolist())
clean_list=simple_preprocess(raw_list, deacc=True)
clean_list_nostop=list(filter(None,[remove_stopwords(word) for word in clean_list]))
p=PorterStemmer()
clean_stemmer=p.stem_documents(clean_list_nostop)
unique_words=list(set(clean_stemmer))

## Prepare training sample
training_counts=clean_tex(df_data,True,unique_words)    
x_training=np.array(training_counts)
y_train=np.array(df_data[df_data['training']==1]['treatment_id'])

l2norm=LA.norm(x_training,ord=2,axis=1,keepdims=True)
x_training=x_training
#/l2norm

## Prepare test sample
test_counts=clean_tex(df_data,False,unique_words)    
x_test=np.array(test_counts)
l2norm=LA.norm(x_test,ord=2,axis=1,keepdims=True)
x_test=x_test


###############################################################################
### Select some tuning data from the bluebook alternatives. Try to get a roughly 
### balanced sample

from random import sample 
# Select number of observations for tuning
ntuning=204
## Length of each alternativa
n_outcome={}
testindex_outcome={}
# CHECK: Do outcomes rather than alternatives
for outcome in [0,1,2]:
    n_outcome.update({outcome:len(df_data[(df_data['training']==False) & (df_data['treatment_id']==int(outcome) )])})
    index=df_data[(df_data['training']==False) & (df_data['treatment_id']==outcome )].index
    testindex_outcome.update({outcome:sample(list(index),int(ntuning/3))})
    
## Get list of indices for tuning data
indices_tuning=testindex_outcome[0]+testindex_outcome[1]+testindex_outcome[2]
all_indices=list(df_data[(df_data['training']==False)].index)
test_indices=[x for x in all_indices if x not in indices_tuning]

## Prepare tuning sample
tuning_counts=clean_tex(df_data.loc[indices_tuning],False,unique_words)    
x_tuning=np.array(tuning_counts)
y_tuning=np.array(df_data.loc[indices_tuning,'treatment_id'])

## Prepare test sample
test_counts=clean_tex(df_data.loc[test_indices],False,unique_words)    
x_test=np.array(test_counts)
y_test=np.array(df_data.loc[test_indices,'treatment_id'])

## Do the tuning of the linear SVM parameter
# This is the range for a tuning parameter
# Here, we try 20 different values
C_arr_len = 100
C_arr =np.linspace(0.00001, 100, C_arr_len)
cv_err_linsvm = np.empty(C_arr_len)
# train is an boolean array that splits the data into training and test set
# train_idx has the indices of the original data (reshuffeled)
for i in range(C_arr_len):
    print( "tuning parameter: ", i)
    # Sets up the model including the changing tuning parameter
    svm_linear = LinearSVC(penalty="l1", dual=False, tol=1e-5, C=C_arr[i], max_iter=1000)
    # Train the model based on the statement data 
    svm_linear.fit(x_training, y_train)
    # Predict the tuning data from the blueebook
    y_pred_k = svm_linear.predict(x_tuning)
    # Count the error
    cv_err_linsvm[i] =np.sum(y_pred_k != y_tuning)
   
# Plotting  
fg = plt.figure(figsize=(5, 5))
ax = fg.add_subplot(1, 1, 1)
ax.set_xlabel("$\lambda$", size="large")
ax.set_ylabel("err")
ax.set_xscale("log")
line_cv = ax.plot(C_arr, cv_err_linsvm, label="cv_err")


C_opt_linsvm = C_arr[np.argmin(cv_err_linsvm)]
print(C_opt_linsvm)

svm_linear =LinearSVC(penalty="l1", dual=False, tol=1e-5, C=C_opt_linsvm, max_iter=1000)
svm_linear.fit(x_training, y_train)
y_test_pred_linsvm = svm_linear.predict(x_test)

print( "Positive rate", np.sum(y_test == y_test_pred_linsvm) / len(y_test))
print( "False rate", np.sum(y_test != y_test_pred_linsvm) / len(y_test))

from sklearn.metrics import confusion_matrix
import seaborn as sns
conf_mat = confusion_matrix(y_test, y_test_pred_linsvm)
fig, ax = plt.subplots(figsize=(6,6))
sns.heatmap(conf_mat, annot=True, fmt='d',
            xticklabels=category_id_df['policy_treatment'], yticklabels=category_id_df['policy_treatment'].values)
plt.ylabel('Actual')
plt.xlabel('Predicted')
plt.show()





















###############################################################################

model = LinearSVC()
model.fit(x_training, y_train)
y_pred = model.predict(x_test)

y_act=np.array(df_data[df_data['training']!=1]['treatment_id'])

from sklearn.metrics import confusion_matrix
import seaborn as sns
conf_mat = confusion_matrix(y_act, y_pred)
fig, ax = plt.subplots(figsize=(6,6))
sns.heatmap(conf_mat, annot=True, fmt='d',
plt.ylabel('Actual')
plt.xlabel('Predicted')
plt.show()

### Two more things
# normalize column to l2 norm=1
# and remove sentences with multiple alternatives in the test dataset.
# Think about tuning of the hyperparameters
# Think about Ada Boost implementation.



a=98+133+125