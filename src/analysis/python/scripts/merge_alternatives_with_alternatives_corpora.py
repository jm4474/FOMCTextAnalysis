import pandas as pd
import os
import re

def main():
    df = pd.DataFrame()
    os.chdir("../data/alternatives_corpora")
    for filename in os.listdir():
        if ".txt" not in filename:
            continue
        alternatives = {'a':[],'b':[],'c':[],'d':[]}
        with open(filename) as f:
            for line in f.readlines():
                if line.strip():
                    split = re.split("[a-z]\s[A-Z]{3,4}\s\d*",line.strip(),1)
                    if len(split)>1:
                        alt = line.strip()[0]
                        alternatives[alt].append(split[1])
        to_append = {
            "date":filename.split(".txt")[0],
        }
        for alternative in alternatives.keys():
            to_append["alt {} corpus".format(alternative)] = "\n".join(alternatives[alternative])
        df = df.append(to_append,ignore_index=True)
    alt_corpus_df = df

    label_df = pd.read_csv("../../output/fed_targets_with_alternatives.csv")

    label_df = label_df[
        [
            "date",
            "decision",
            "bluebook_treatment_size_alt_a",
    "bluebook_treatment_size_alt_b",
    "bluebook_treatment_size_alt_c",
    "bluebook_treatment_size_alt_d",
    "bluebook_treatment_size_alt_e"
        ]
    ]

    label_df['date'] = pd.to_datetime(label_df['date'])
    alt_corpus_df['date'] = pd.to_datetime(alt_corpus_df['date'])

    merge_df = pd.merge(label_df,alt_corpus_df,on="date")

    merge_df = merge_df[['date', 'alt a corpus','bluebook_treatment_size_alt_a',
                        'alt b corpus','bluebook_treatment_size_alt_b',
                        'alt c corpus','bluebook_treatment_size_alt_c',
                        'alt d corpus','bluebook_treatment_size_alt_d',
                        'decision'
                        ]]

    merge_df.to_csv("../../output/alternative_outcomes_and_corpus.csv")


if __name__ == "__main__":
    main()