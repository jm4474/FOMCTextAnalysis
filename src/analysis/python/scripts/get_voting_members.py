import pandas as pd
import os
import re
import numpy as np
import pprint
import logging

'''
@Author: Anand Chitale
This script extracts voting members using the minutes of FOMC meetings, and then appends a manual verification for certain values.
'''


def main():
    voter_df = get_voters()
    get_errors(voter_df)
    merge_error_correction(voter_df)
    merge_voting_members_with_alternatives()

def get_voters():
    df = pd.read_excel("../data/fomc_dissents_data.xlsx",skiprows=3)
    df["Date"] = df["FOMC Meeting"].apply(lambda x:str(x).split(" ")[0])
    df['FOMC Votes'] = df['FOMC Votes'].apply(lambda x:0 if np.isnan(x) else x)

    
    
    voter_df = pd.DataFrame()

    for index,row in df.iterrows():
        voters = []
        num_voters = int(row['FOMC Votes'])
        date_path = '../../../collection/python/data/minutes_raw_text/{}.txt'.format(row['Date'])
        if not os.path.exists(date_path):
            continue
        with open(date_path) as f:
            broken = False
            broken_starts = 0
            broken_ends = 0
            lines = f.readlines()
            
            '''First Check For Broken Title'''

            #print("CHECKING USING FRAGMENT HEURISTIC")
            for line in lines[:200]:
                if line.strip():
                    if broken_ends==0:
                        title_frag = re.match(r'^(?:PRESENT: |PRESENT. )?(?:Mr.|Ms.|Mt.|Mrs. )$',line.strip())
                        if title_frag:
                            if not broken:
                                broken = True
                            #print("Broken Begining")
                            #print(title_frag.group(0))
                            title_frag_string = str(title_frag.group(0)).replace("PRESENT: ","")
                            voters.append(title_frag_string)
                            broken_starts+=1
                            continue
                    if broken and broken_ends<len(voters):
                        name_fragment = re.match('^[A-Z][a-z][A-Za-z]*',line.strip())
                        if name_fragment:
                            voters[broken_ends] = voters[broken_ends]+" "+str(name_fragment.group(0))
                            broken_ends+=1
            
            '''Check using Mr. Regex'''
            
            if len(voters)==0:
                #print("CHECKING TITLE REGEX")
                for line in lines[:200]:
                    '''Then check for valid input'''
                    voter_line = re.findall(r'(?:Mr.|Ms.|Mrs.) [A-Z][a-zA-Z]*',line.strip())
                    if voter_line:
                        #print(voter_line)
                        voters.append(voter_line[0])
                        if len(voters)>=num_voters:
                            break
            
            '''Check Last Name Regex'''
            
            if len(voters) == 0:
                #print("Checking POST-PRESENT-NAME HEURISTIC")
                found_present = False
                for line in lines[:200]:
                    if "PRESENT:" in line.strip() or "PRESENT." in line.strip():
                        found_present = True
                        present_line = line.split(",")[0].strip().replace("PRESENT","")
                        name_text = re.match('[A-Z][a-z]*\s?(?:[A-Z][a-z]*)?',present_line)
                        if name_text:
                            voters.append(name_text.group(0))
                        continue
                    if found_present:
                        #print(line)
                        name_text = re.match('[A-Z][a-z]*\s?(?:[A-Z][a-z]*)?',line.split(",")[0].strip())
                        if name_text:
                            voters.append(name_text.group(0))
                        if len(voters)>=num_voters:
                            break
        #print('Date:{}'.format(row['Date']))
        #print("Broken Status:{}".format(broken))
        #print("Voter Number:{}".format(num_voters))
        #print("Voters Found:{}".format(len(voters)))
        #pprint.pprint(voters)
        voter_df = voter_df.append({
            "Date":row['FOMC Meeting'],
            "voters_expected":num_voters,
            "voters_observed":len(voters),
            "Voters":voters if num_voters==len(voters) else None,
        },ignore_index=True)
    #print("="*50)
    print(voter_df)
    return voter_df

def get_errors(voter_df):
    print(len(voter_df[voter_df["Voters"].isna()]))

    voter_errors = voter_df[voter_df["Voters"].isna()].reset_index(drop=True)
    voter_errors.to_csv("../output/voter_errors.csv",index=False)

def merge_error_correction(voter_df):
    correction_df = pd.read_csv("../data/voter_corrections.csv")
    correction_df['Date'] = pd.to_datetime(correction_df['Date'])
    voter_df['Date'] = pd.to_datetime(voter_df['Date'])
    voter_df = pd.concat([voter_df,correction_df])
    voter_df = voter_df.drop_duplicates(['Date'], keep="last").sort_values(by="Date")
    voter_df = voter_df[(voter_df['Date'].dt.year>1979)&(voter_df['Date'].dt.year<2010)]
    voter_df.to_csv("../output/voting_members.csv",index=False)

def merge_voting_members_with_alternatives():
    voting_df = pd.read_csv("../output/voting_members.csv")
    alt_df = pd.read_csv("../output/alternative_outcomes_and_corpus.csv")
    voting_df['date'] = pd.to_datetime(voting_df['Date'])
    alt_df['date'] = pd.to_datetime(alt_df['date'])
    merge_df = pd.merge(alt_df,voting_df,on="date")
    
    excel_df = pd.read_excel("../data/fomc_dissents_data.xlsx",skiprows=3)
    excel_df["Date"] = excel_df["FOMC Meeting"].apply(lambda x:str(x).split(" ")[0])
    excel_df['FOMC Votes'] = excel_df['FOMC Votes'].apply(lambda x:0 if np.isnan(x) else x)
    excel_df['date'] = pd.to_datetime(excel_df["Date"])
    merge_df = pd.merge(merge_df,excel_df)
    merge_df = merge_df[[
        'date', 'alt a corpus', 'bluebook_treatment_size_alt_a', 'alt b corpus',
       'bluebook_treatment_size_alt_b', 'alt c corpus',
       'bluebook_treatment_size_alt_c', 'alt d corpus',
       'bluebook_treatment_size_alt_d', 'decision', 'Voters', 'Year',
       'Chair', 'Dissent (Y or N)', 'FOMC Votes',
       'Votes for Action', 'Votes Against Action',
       'Number Governors Dissenting', 'Number Presidents Dissenting',
       'No. Governors for Tighter', 'No. Governors for Easier',
       'No. Presidents for Tighter', 'No. Presidents for Easier',
       'Dissenters Tighter', 'Dissenters Easier',
       'Dissenters Other/Indeterminate'
    ]]
    merge_df = merge_df[(merge_df['date'].dt.year>1979)&(merge_df['date'].dt.year<2010)]
    merge_df.to_csv("../output/alternatives_corpus_and_voting_information.csv",index=False)

if __name__ == "__main__":
    main()