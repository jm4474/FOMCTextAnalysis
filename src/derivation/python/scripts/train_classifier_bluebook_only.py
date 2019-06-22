#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Purpose: Uses only bluebooks for training
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
from train_standard_classifier import get_merged_data,transform_merged
from sklearn.model_selection import train_test_split
import seaborn as sns
###############################################################################

###############################################################################
### Use only the bluebooks for the training

from random import sample,seed
seed(20)

### Obtain the bluebook data
df_data, category_to_id, id_to_category,category_id_df = get_merged_data()
df_bluebooks=df_data[(df_data['training']==False) & (df_data['date']>"1988-12-13")]

### Do standard characterization with TF-IDF
tfidf = TfidfVectorizer(sublinear_tf=True, min_df=5,norm='l2', encoding='latin-1', ngram_range=(1, 2),stop_words='english')
features = tfidf.fit_transform(df_bluebooks['statement']).toarray()
features.shape 
labels=df_bluebooks['treatment_id']
# yields 365 meetings with 1181 tokens

models = [
    RandomForestClassifier(n_estimators=200, max_depth=3, random_state=0),
    LinearSVC(penalty="l1", dual=False, tol=1e-9, C=1.1, max_iter=1000) ,
    LogisticRegression(random_state=0),
    ]

CV = 5
cv_df = pd.DataFrame(index=range(CV * len(models)))
entries = []
for model in models:
    model_name = model.__class__.__name__
    accuracies = cross_val_score(model, features, labels, scoring='accuracy', cv=CV)
    for fold_idx, accuracy in enumerate(accuracies):
        entries.append((model_name, fold_idx, accuracy))
        cv_df = pd.DataFrame(entries, columns=['model_name', 'fold_idx', 'accuracy'])

cv_df.groupby('model_name').accuracy.mean()

### Pick SVC
model = LinearSVC(penalty="l1", dual=False, tol=1e-9, C=1.1, max_iter=1000)
X_train, X_test, y_train, y_test, indices_train, indices_test = train_test_split(features, labels, df_bluebooks.index, test_size=0.33, random_state=0)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)
from sklearn.metrics import confusion_matrix
conf_mat = confusion_matrix(y_test, y_pred)
fig, ax = plt.subplots(figsize=(10,10))
sns.heatmap(conf_mat, annot=True, fmt='d',
            xticklabels=category_id_df['policy_treatment'], yticklabels=category_id_df['policy_treatment'].values)
plt.ylabel('Actual')
plt.xlabel('Predicted')
plt.show()