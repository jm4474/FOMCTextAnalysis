
#Author: Anand Chitale
#This file reads in Pepe's transcript collocated and tokenized data file and brings it
#into the repo

#Note: Matlab generated file uses start date as the meeting date

import pandas as pd
import os
import shutil
import pickle
import re


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


def import_matlab_data():
    ts_df = pd.read_pickle("../../../derivation/python/output/raw_text_part2.pkl")
    ts_df = ts_df[['Date','Section','Speaker','content']]

    ts_df['Date'] = pd.to_datetime(ts_df['Date'],format="%Y-%m-%d")
    ts_df['month'] = ts_df['Date'].dt.month
    ts_df['year'] = ts_df['Date'].dt.year

    mdf = pd.read_csv("../../../derivation/python/output/meeting_derived_file.csv")
    meeting_df = mdf[['start_date', 'end_date', 'event_type']].copy()

    meeting_df['start_date'] = pd.to_datetime(meeting_df['start_date'])
    meeting_df['end_date'] = pd.to_datetime(meeting_df['end_date'])

    merge_df = ts_df.merge(meeting_df,how="left",left_on="Date",right_on = "end_date")
    merge_df.drop(columns="Date",inplace=True)

    return merge_df

def main():

    matlab_df = import_matlab_data()
    
    matlab_df = matlab_df.replace({"Speaker":corrections})
    matlab_df["Speaker"] = matlab_df["Speaker"].apply(lambda x: x.lower())
    matlab_df = matlab_df[['start_date', 'end_date' , 'Speaker', 'Section', 'content', 'month', 'year', 'event_type']]
    matlab_df = matlab_df[matlab_df["event_type"]=="Meeting"]
    matlab_df.drop(columns=["event_type"],inplace=True)
    
    matlab_df.to_pickle("../output/speaker_data_part2.pkl")
    matlab_df.to_csv("../output/speaker_data_part2.csv",index=False)


    speaker_data = pd.read_pickle("../output/speaker_data.pkl")    
    speakers_full = pd.concat([speaker_data,matlab_df[['start_date', 'Speaker', 'Section', 'content']]], axis=0)    
    speakers_full = speakers_full.reset_index(drop=True)
    speakers_full.to_pickle("../output/speaker_data_full.pkl")
    speakers_full.to_csv("../output/speaker_data_full.csv",index=False)




if __name__ == "__main__":
    main()
