#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Purpose: Uses the statement data to train a classifier and use the classifier 
         for the prediction of the alternatives in the bluebook from 1988-2008
         Here: Use vocabulary from the bluebooks and then create a word count
         matrix based on this vocabulary.
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

from gensim.utils import simple_preprocess
from gensim.parsing.porter import PorterStemmer
from gensim.parsing.preprocessing import remove_stopwords
import collections
from numpy import linalg as LA
from standard_classifier import get_merged_data,transform_merged


###############################################################################

### Creates list with wordcounts with supplied list
def count_words(dataframe,unique_words):
    counts=[]
    for idx,row in dataframe.iterrows():
        ## Do with one document in the training data
        sample_raw=row['statement']
        sample_clean=simple_preprocess(sample_raw, deacc=True)
        sample_clean_nostop=list(filter(None,[remove_stopwords(word) for word in sample_clean]))
        p=PorterStemmer()
        sample_stem=p.stem_documents(sample_clean_nostop)
        ## Get the count for each word
        counter = collections.Counter(sample_stem)
        voc_count=[]
        for word in unique_words:
            voc_count.append(counter[word])
        counts.append(voc_count)  
    return counts

# Stem and remove stop words and return a unique list of words
def extract_unique_words(dataframe):
    raw_list=" ".join(dataframe.tolist())
    clean_list=simple_preprocess(raw_list, deacc=True)
    clean_list_nostop=list(filter(None,[remove_stopwords(word) for word in clean_list]))
    p=PorterStemmer()
    clean_stemmer=p.stem_documents(clean_list_nostop)
    unique_words=list(set(clean_stemmer))
    return unique_words

### Obtain the dataset
df_data, category_to_id, id_to_category,category_id_df = get_merged_data()

### Get the unique words in the bluebooks
unique_words=extract_unique_words(df_data[df_data['training']!=1]['statement'])

## Prepare training sample
training_counts=count_words(df_data[df_data['training']==True],unique_words)    
x_training=np.array(training_counts)
y_train=np.array(df_data[df_data['training']==1]['treatment_id'])

l2norm=LA.norm(x_training,ord=2,axis=1,keepdims=True)
x_training=x_training
#/l2norm

## Prepare test sample
test_counts=count_words(df_data[df_data['training']==False],unique_words)    
x_test=np.array(test_counts)
l2norm=LA.norm(x_test,ord=2,axis=1,keepdims=True)
x_test=x_test

model = LinearSVC()
model.fit(x_training, y_train)
y_pred = model.predict(x_test)

y_act=np.array(df_data[df_data['training']!=1]['treatment_id'])

from sklearn.metrics import confusion_matrix
import seaborn as sns
conf_mat = confusion_matrix(y_act, y_pred)
fig, ax = plt.subplots(figsize=(6,6))
sns.heatmap(conf_mat, annot=True, fmt='d',
            xticklabels=category_id_df['policy_treatment'], yticklabels=category_id_df['policy_treatment'].values)
plt.ylabel('Actual')
plt.xlabel('Predicted')
plt.show()


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




















