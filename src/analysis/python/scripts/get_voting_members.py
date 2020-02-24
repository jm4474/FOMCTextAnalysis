import pandas as pd
import os
import re
import numpy as np
import pprint
import logging

def main():
    df = pd.read_excel("../data/fomc_dissents_data.xlsx",skiprows=3)
    df["Date"] = df["FOMC Meeting"].apply(lambda x:str(x).split(" ")[0])
    df['FOMC Votes'] = df['FOMC Votes'].apply(lambda x:0 if np.isnan(x) else x)

    
    voter_df = pd.DataFrame()

    for index,row in df.iterrows():
        voters = []
        num_voters = int(row['FOMC Votes'])
        date_path = '../../../collection/python/data/transcript_raw_text/{}.txt'.format(row['Date'])
        if not os.path.exists(date_path):
            continue
        with open(date_path) as f:
            broken = False
            broken_starts = 0
            broken_ends = 0
            lines = f.readlines()
            
            '''First Check For Broken Title'''

            print("CHECKING USING FRAGMENT HEURISTIC")
            for line in lines[:200]:
                if line.strip():
                    if broken_ends==0:
                        title_frag = re.match(r'^(?:PRESENT: |PRESENT. )?(?:Mr.|Ms.|Mt. )$',line.strip())
                        if title_frag:
                            if not broken:
                                broken = True
                            print("Broken Begining")
                            print(title_frag.group(0))
                            title_frag_string = str(title_frag.group(0)).replace("PRESENT: ","")
                            voters.append(title_frag_string)
                            broken_starts+=1
                            continue
                    if broken and broken_ends<len(voters):
                        name_fragment = re.match('^[A-Z][a-z][A-Za-z]*',line.strip())
                        if name_fragment:
                            print(name_fragment)
                            if broken_ends==0:
                                print("Found {} Fragments".format(len(voters)))
                                print(voters)
                            print("Broken Ending")
                            print(name_fragment.group(0))
                            voters[broken_ends] = voters[broken_ends]+" "+str(name_fragment.group(0))
                            broken_ends+=1
            
            '''Check using Mr. Regex'''
            
            if len(voters)==0:
                print("CHECKING TITLE REGEX")
                for line in lines[:200]:
                    '''Then check for valid input'''
                    voter_line = re.findall(r'(?:Mr.|Ms.) [A-Z][a-zA-Z]*',line.strip())
                    if voter_line:
                        #print(voter_line)
                        voters.append(voter_line[0])
                        if len(voters)>=num_voters:
                            break
            
            '''Check Last Name Regex'''
            
            if len(voters) == 0:
                print("Checking POST-PRESENT-NAME HEURISTIC")
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
                        print(line)
                        name_text = re.match('[A-Z][a-z]*\s?(?:[A-Z][a-z]*)?',line.split(",")[0].strip())
                        if name_text:
                            voters.append(name_text.group(0))
                        if len(voters)>=num_voters:
                            break
        print('Date:{}'.format(row['Date']))
        print("Broken Status:{}".format(broken))
        print("Voter Number:{}".format(num_voters))
        print("Voters Found:{}".format(len(voters)))
        pprint.pprint(voters)
        voter_df = voter_df.append({
            "Date":row['FOMC Meeting'],
            "voters_expected":num_voters,
            "voters_observed":len(voters),
            "Voters":voters if num_voters==len(voters) else None,
        },ignore_index=True)
        print("="*50)
        print(voter_df)
        voter_df.to_csv("../output/voting_members.csv")

if __name__ == "__main__":
    main()