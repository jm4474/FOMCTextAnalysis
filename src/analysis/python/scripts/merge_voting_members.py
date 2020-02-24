import pandas as pd
import numpy as np

def main():
    voting_df = pd.read_csv("../output/get_voting_members.csv")
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
    print(merge_df)
    merge_df.to_csv("../output/alternatives_corpus_and_voting_information.csv")

if __name__ == "__main__":
    main()