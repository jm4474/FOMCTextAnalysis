#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan  6 23:17:24 2021

@author: olivergiesecke
"""

#Author: Anand Chitale
#This file reads in Pepe's transcript collocated and tokenized data file and brings it
#into the repo

#Note: Matlab generated file uses start date as the meeting date

import pandas as pd
import os
import shutil
import pickle
import re

'''
The imported file has a few errors which make use of
the end date, instead of the start date, as is custom for
most of the imported file. Furthermore, the imported file
failed to fetch data for the meeting on 5-17-1988.
Finally, we have to deal with a number of typos in the speaker name
'''
end_date_error_replacements = {
    199207:199206,
    199502:199501,
    199807:199806
}

corrections ={'BAUGHWJV':'BAUGHMAN',
              'BOHNE':'BOEHNE',
              'EISEMENGER':'EISENMENGER',
              'GEITHER':'GEITHNER',
              'KIMBREL':'KIMEREL',
              'MATTINGLY': 'MATTLINGLY',
              'FORESTALL':'FORRESTAL',
              'GRENSPAN':'GREENSPAN',
              'GREESPAN':'GREENSPAN',
              'GREENPSAN':'GREENSPAN',
              'GREENSPAN,':'GREENSPAN',
              'GREENPAN':'GREENSPAN',
              'McANDREWS':'MCANDREWS',
              'MCDONUGH':'MCDONOUGH',
              'MOSCOW':'MOSKOW',
              'MORRIS':'MORRRIS',
              'MONHOLLAN':'MONHOLLON',
              'MILIER':'MILLER',
              'MILER':'MILLER',
              'SCWLTZ':'SCHULTZ',
              'SCHELD':'SCHIELD',
              'WILLZAMS':'WILLIAMS',
              'WALLJCH':'WALLICH',
              'VOLCKFR':'VOLCKER',
              'VOLCRER':'VOLKER',
              'ALLISON for':'ALLISON',
              'ALTMA"':'ALTMANN',
              'B A U G W':'BAUGW',
              'BIES (as read by Ms':'BIES',
              'BLACK &':'BLACK',
              'MAYO/MR':'MAYO',
              'Greene':"GREENE",
              'CROSS,':'CROSS',
              'GREENSPAN,':'GREENSPAN',
              'HOSKINS,':'HOSKINS',
              'MACCLAURY':'MACLAURY',
              'MORRRIS':'MORRIS',
              "O'CONNELL":'O’CONNELL',
              'SOLOMON]':'SOLOMON',
              'TRUMAN-':'TRUMAN',
              'VOLCKER,':'VOLCKER',
              'VOLKER,':'VOLCKER',
              'WALLlCH':'WALLICH',
              '[BALLES]':'BALLES',
              '[GARDNER]':'GARDNER',
              '[KICHLINE]?':'KICHLINE',
              '[PARDEE]':'PARDEE',
              '[ROOS]':'ROOS',
              '[STERN':'STERN',
              '[WILLES]':'WILLES',
              'ŞAHIN':'SAHIN',
              '[STERN(?)':'STERN',
              '[STERN]':'STERN',
              'GRALEY':'GRAMLEY',
              'ALTMA”':'ALTMANN'}

def name_corr(val):
    sentence=""
    dictkeys=[key for key, value in corrections.items()]
    if val in dictkeys:
        val = corrections[val]
    else:
        if re.match(".*\(\?\)",val):
            val = re.search("(.*)(\(\?\))",val)[1]
            if val in dictkeys:
                val = corrections[val]

        if len(val.split(" "))>1:
            #print(val.split(" ")[0])
            #print(val.split(" ")[1:])
            sentencehelp = " ".join(val.split(" ")[1:])
            if not len(re.findall("Yes",sentencehelp))>7:
                if len(sentencehelp)>10:
                    sentence = sentencehelp
                    #print(sentence)
            val = val.split(" ")[0]
            if val in dictkeys:
                val = corrections[val]
    #print(val)
    return val,sentence

def generate_speaker_file(speaker_statements):

    #if not os.path.exists("../output/speaker_data"):
    #    os.mkdir("../output/speaker_data")


    speaker_statements["content"] = speaker_statements["content"].apply(lambda x: " ".join(str(x).split()[1:]) if len(str(x).split())>1 and str(x).split()[0]=="LINDSEY" else x)
    speaker_statements["Speaker"] = speaker_statements["Speaker"].apply(lambda x: "LINDSEY" if x=="D" else x)
    speaker_statements['Speaker'] = speaker_statements['Speaker'].apply(lambda x: x.split(".")[0] if "." in x else x)
    speaker_statements['Speaker'] = speaker_statements['Speaker'].apply(lambda x: corrections[x] if x in corrections else x )

    speakers = [speaker for speaker in set(speaker_statements["Speaker"])]
    print("Number of speakers:{}".format(len(speakers)))
    count = 1
    #for speaker in speakers:
        #print("Currently working on statements for speaker {} of {}. Name:{}".format(count,len(speakers),speaker))
        #speaker_df = speaker_statements[speaker_statements["Speaker"]==speaker]
        #speaker_path = "{}/{}".format("../output/speaker_data",speaker)
        #if not os.path.exists(speaker_path):
        #    os.mkdir(speaker_path)
        #speaker_df[['start_date','content']].to_csv("{}/{}_{}".format(speaker_path,speaker,"statements_by_meeting.csv"))
        #speaker_list = list(speaker_df["content"])
        #with open("{}/{}_{}".format(speaker_path,speaker,"corpus.txt"),"w+") as f:
        #    f.write(" ".join(speaker_list))
        #count+=1
    speaker_statements['content'] = speaker_statements['content'].fillna("")
    speaker_statements = speaker_statements.groupby(['start_date','Speaker','Section'])['content'].apply(lambda x: "%s" % " ".join(x)).reset_index()
    speaker_statements['Speaker'] = speaker_statements['Speaker'].apply(lambda x:x.lower())

    return speaker_statements


def import_matlab_data():
    ts_df = pd.read_excel("../data/raw_text_separated.xlsx")
    ts_df = ts_df[['Date','Section','Speaker','content']]
    ts_df.Date = ts_df.Date.replace(end_date_error_replacements)


    ts_df['Date'] = pd.to_datetime(ts_df['Date'],format="%Y%m")
    ts_df['month'] = ts_df['Date'].dt.month
    ts_df['year'] = ts_df['Date'].dt.year
    ts_df = ts_df.drop(columns=["Date"])


    mdf = pd.read_csv("../../../derivation/python/output/meeting_derived_file.csv")
    meeting_df = mdf[mdf.event_type=="Meeting"]


    meeting_df['start_date'] = pd.to_datetime(meeting_df['start_date'])
    meeting_df['end_date'] = pd.to_datetime(meeting_df['end_date'])

    meeting_dates = pd.DataFrame(meeting_df[['start_date','end_date']])

    meeting_dates['month'] = meeting_dates['start_date'].dt.month
    meeting_dates['year'] = meeting_dates['start_date'].dt.year

    merge_df = pd.merge(left=ts_df,right=meeting_dates,how="right",on=['month','year'])
    merge_df = merge_df[merge_df.Speaker.notna()]
    merge_df = merge_df.fillna("")

    return merge_df

def main():

    matlab_df = import_matlab_data()

    speaker_df = generate_speaker_file(matlab_df)
    print(speaker_df)
    speaker_df.to_pickle("../output/speaker_data.pkl")
    speaker_df.to_csv("../output/speaker_data.csv",index=False)


if __name__ == "__main__":
    main()
