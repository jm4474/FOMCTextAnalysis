#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 17 14:47:03 2019

@author: olivergiesecke
"""
###############################################################################
### Import packages
import pandas as pd
import re
import os
from io import StringIO
import numpy as np
import matplotlib.pyplot as plt
###############################################################################

### Open the csv
data=pd.read_csv("../output/statements_text_extraction_cleaned.csv")
# Data stored in data['statement'] and data['policy_treatment']

### Clean Data
data=data[data['policy_treatment'].notna()][['statement','policy_treatment']]
print(len(data))
# 129 entries
## Create categorical variable for policy treatment
data['treatment_id'] = data['policy_treatment'].factorize()[0]

category_id_df = data[['policy_treatment', 'treatment_id']].drop_duplicates().sort_values('treatment_id')
category_to_id = dict(category_id_df.values)
id_to_category = dict(category_id_df[['treatment_id','policy_treatment']].values)

# Some sum stats
fig = plt.figure(figsize=(8,6))
data.groupby('policy_treatment')['statement'].count().plot.bar(ylim=0)
plt.show()
pd.pivot_table( data,index='policy_treatment',aggfunc=np.count_nonzero )

### Preprocessing of the text

## Get TF-IDF with following ooptions
# sublinear_df=True: logarithmic form for frequency.
# min_df is the minimum numbers of documents a word must be present in to be kept.
# norm=l2, to ensure all our feature vectors have a euclidian norm of 1.
# ngram_range is set to (1, 2) to indicate that we want to consider both unigrams and bigrams.
# stop_words is set to "english" to remove all common pronouns ("a", "the", ...) to reduce the number of noisy features.


from sklearn.feature_extraction.text import CountVectorizer
tf=CountVectorizer( min_df=3,  encoding='latin-1', ngram_range=(1, 2), stop_words='english')
features = tf.fit_transform(data['statement']).toarray()
labels = data['treatment_id']
# yields 129 sentences with 2586 tokens
features.shape 

## Get most frequent unigrams and bigrams with each outcome
from sklearn.feature_selection import chi2
import numpy as np
N = 5
for Product, category_id in sorted(category_to_id.items()):
    features_chi2 = chi2(features, labels == category_id)
    indices = np.argsort(features_chi2[0])
    feature_names = np.array(tfidf.get_feature_names())[indices]
    unigrams = [v for v in feature_names if len(v.split(' ')) == 1]
    bigrams = [v for v in feature_names if len(v.split(' ')) == 2]
    print("# '{}':".format(Product))
    print("  . Most correlated unigrams:\n. {}".format('\n. '.join(unigrams[-N:])))
    print("  . Most correlated bigrams:\n. {}".format('\n. '.join(bigrams[-N:])))
    
# Get preditions    
    
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
X_train, X_test, y_train, y_test = train_test_split(data['statement'], data['policy_treatment'], random_state = 0)
count_vect = CountVectorizer()
X_train_counts = count_vect.fit_transform(X_train)
tfidf_transformer = TfidfTransformer()
X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)
clf = MultinomialNB().fit(X_train_tfidf, y_train)    
    
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import LinearSVC
from sklearn.model_selection import cross_val_score
models = [
    RandomForestClassifier(n_estimators=200, max_depth=3, random_state=0),
    LinearSVC(),
    MultinomialNB(),
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
import seaborn as sns
sns.boxplot(x='model_name', y='accuracy', data=cv_df)
sns.stripplot(x='model_name', y='accuracy', data=cv_df, 
              size=8, jitter=True, edgecolor="gray", linewidth=2)
plt.show()

cv_df.groupby('model_name').accuracy.mean()

model = RandomForestClassifier()
X_train, X_test, y_train, y_test, indices_train, indices_test = train_test_split(features, labels, data.index, test_size=0.33, random_state=0)
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


for predicted in category_id_df['treatment_id']:
    for actual in category_id_df['treatment_id']:
        if predicted != actual and conf_mat[actual, predicted] >= 1:
            print("'{}' predicted as '{}' : {} examples.".format(id_to_category[actual], id_to_category[predicted], conf_mat[actual, predicted]))
            print(data.loc[indices_test[(y_test == actual) & (y_pred == predicted)]][['policy_treatment', 'statement']].values)
            
from sklearn import metrics
print(metrics.classification_report(y_test, y_pred, target_names=data['policy_treatment'].unique()))            

### Import data by calling function in other file
from bluebook_alternative_extraction_and_classification import getdata_bluebook

df_output=getdata_bluebook()
df_output['year']=pd.to_numeric(df_output['meeting_date'].str[:4])
df_output['date']=pd.to_datetime(df_output['meeting_date'])
df_result=df_output[(df_output['date']<="2009-03-18") & (df_output['date']>="1988-01-01")]


### Get the feature matrix from the alternatives.
# Do one alternative at a time

## Preprocessing
# Preprocessing has to be done once at at time to insure the dimension of the feature matrices

for alt in ["a","b","c","d","e"]:
    df_result.loc[:,"alt_"+alt]=""
    for idx,value in df_result["alt_"+alt+"_sentences"].iteritems():
        if not len(value)==0:
            df_result.loc[idx,"alt_"+alt]=value[0]

x_data=pd.wide_to_long(df_result[["date","alt_a","alt_b","alt_c","alt_d","alt_e"]], "alt", "date", "alternative",sep="_",suffix="\w+")
x_data=x_data.reset_index()
x_data=pd.DataFrame(x_data[x_data["alt"]!=""])
x_data=x_data.rename({"alt":"statement"},axis='columns')
x_data=x_data.drop(columns=['date','alternative'])
x_data.loc[:,"treatment_id"]=""
new=pd.DataFrame(data[["statement","treatment_id"]])
x_data=x_data.append(new,ignore_index=True)
x_data.loc[:,"training"]=x_data["treatment_id"]!=""

selection=np.array(x_data["training"]==True)
label=np.array(x_data["treatment_id"])

from sklearn.feature_extraction.text import CountVectorizer
tf=CountVectorizer( min_df=3,  encoding='latin-1', ngram_range=(1, 2), stop_words='english')
features = tf.fit_transform(x_data['statement']).toarray()
# yields 523 meetings with 3198 tokens
features.shape 

## Do prediction with the random forest
# Select model

features[selection]

x_train=features[selection]
y_train=list(label[selection])
x_pred=features[~selection]

model = RandomForestClassifier()
model.fit(x_train, y_train)

y_id = model.predict(x_pred)

y_id=[]
for element in y_pred:
    y_label    

