import pandas as pd
import pprint
import re
from collections import Counter
import numpy as np
import os

def get_error_dates():
    df = pd.read_csv("fed_targets_with_alternatives.csv")
    m_df = pd.read_csv('fed_targets_with_alternatives_missinbb.csv')

    df = pd.concat([df,m_df],ignore_index=True,axis=0)[['date','decision','bluebook_treatment_size_alt_a',
        'bluebook_treatment_size_alt_b', 'bluebook_treatment_size_alt_c',
        'bluebook_treatment_size_alt_d', 'bluebook_treatment_size_alt_e']]

    df=df[['date','decision','bluebook_treatment_size_alt_a',
        'bluebook_treatment_size_alt_b', 'bluebook_treatment_size_alt_c',
        'bluebook_treatment_size_alt_d', 'bluebook_treatment_size_alt_e']]

    for alt in ['a','b','c','d','e']:
        df = df.rename(columns={f'bluebook_treatment_size_alt_{alt}':f'd_{alt}'})
        df.loc[:,f'd_{alt}'] = pd.to_numeric(df[f'd_{alt}'],errors='coerce')

    def get_overlaps(x):
        matches = []
        for alt in ['a','b','c','d','e']:
            if x[f'd_{alt}'] == x['decision']:
                matches.append(alt)
        return matches

    df['alt_chosen'] = df.apply(lambda x: get_overlaps(x),axis=1)
    df['mult_match'] = df.apply(lambda x:len(x['alt_chosen'])>1,axis=1)
    df['no_match'] = df.apply(lambda x:len(x['alt_chosen'])==0,axis=1)


    correction_df = df[(df.no_match==True)|(df.mult_match==True)].reset_index(drop=True)

    return correction_df

def create_fill_in_df(correction_df):
    sentence_df = pd.read_excel("../../../derivation/python/data/bluebook_manual_data_online.xlsx")
    sentence_df['start_date'] = pd.to_datetime(sentence_df['start_date'])
    sentence_df['end_date'] = pd.to_datetime(sentence_df['end_date'])

    correction_df['date'] = pd.to_datetime(correction_df['date'])
    manual_df = pd.merge(sentence_df,correction_df,left_on="end_date",right_on="date",how="right")

    manual_df = manual_df[[
        'date','start_date', 'end_date',
        'decision', 'd_a', 'd_b', 'd_c',
        'd_d', 'd_e', 'alt_chosen', 'mult_match', 'no_match', 'DFF_Before_meeting',
        'DFEDTR_before', 'DFEDTR_end', 'C_TREATMENT_alt_a',
        'C_TREATMENT_SIZE_alt_a', 'justify_alt_a', 'Sentences_alt_a',
        'C_TREATMENT_alt_b', 'C_TREATMENT_SIZE_alt_b', 'justify_alt_b',
        'Sentences_alt_b', 'C_TREATMENT_alt_c', 'C_TREATMENT_SIZE_alt_c',
        'justify_alt_c', 'Sentences_alt_c', 'C_TREATMENT_alt_d',
        'C_TREATMENT_SIZE_alt_d', 'justify_alt_d', 'Sentences_alt_d',
        'C_TREATMENT_alt_e', 'C_TREATMENT_SIZE_alt_e', 'justify_alt_e',
        'Sentences_alt_e', 'comments']].sort_values(by="date").reset_index(drop=True)

    print("Found this many errors:")
    print(len(manual_df))

    manual_df.to_csv("undetermined_alternatives.csv",index=False)

def main():
    os.chdir("../output")
    correction_df = get_error_dates()
    create_fill_in_df(correction_df)

if __name__ == "__main__":
    main()