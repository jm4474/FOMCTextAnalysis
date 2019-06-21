#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Purpose: Uses the statement data to train a classifier and use the classifier 
         for the prediction of the alternatives in the bluebook from 1988-2008
         Here: standard classifier as RF, MN logitic regression, SVM
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

## Get bluebooks alternatives and statements in one file
def get_merged_data():
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
    
    return [df_data, category_to_id, id_to_category,category_id_df]

df_data, category_to_id, id_to_category,category_id_df = get_merged_data()

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
print(cv_df.groupby('model_name').accuracy.mean())
# terrible performance
