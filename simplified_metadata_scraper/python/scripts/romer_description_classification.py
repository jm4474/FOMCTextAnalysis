import pandas as pd
import re
import numpy as np
import csv
def main():
    extract_treatment(create_classifier_df())
def create_classifier_df():
    original_df = pd.read_csv("../output/romer_data.csv")
    comp_df = []

    prev_row = ""
    meetings = []
    for index,row in original_df.iterrows():
        meeting = {}
        meeting['date'] = row['date']

        prev = float(row['prev'])
        new = float(row['new'])

        if prev>new:
            meeting['TREATMENT'] = "E"
        elif prev<new:
            meeting['TREATMENT'] = "T"
        else:
            meeting['TREATMENT'] = "U"
        given_desc = row['description'].lower()
        if given_desc in\
                ["same as previous meeting.",
                "similar to previous meeting."]:
            meeting['description'] = prev_row
        else:
            meeting['description'] = given_desc
        prev_row = meeting['description']
        meeting['predicted_treatment'] = ""
        meetings.append(meeting)
    comp_df = pd.DataFrame(meetings)
    #comp_df.to_csv("../output/romer_prediction.csv")
    return comp_df

def extract_treatment(comp_df):
    keywords_ease = ["lower", "cut", "cuts", "decline", "reduction", "ease", "reduce", "easing"]
    keywords_unchanged = ["keep", "unchanged", "no change", "maintained", "maintain", "remain", "forego", "continue"]
    keywords_tighten = ["raise", "hike", "raised", "firm", "firming", "increase", "tightening", "rise", "tighten",
                        "tighter"]
    for index,row in comp_df.iterrows():
        print(row['date'])
        print(row['description'])
        count_ease = 0
        count_unchanged = 0
        count_tighten = 0
        sentence = row['description']
        for keyword in keywords_ease:
            pattern = "[^a-z]" + keyword + "[^a-z]"
            regex = re.compile(pattern, re.IGNORECASE)
            for match in regex.finditer(sentence):
                count_ease += 1
                # print(match.group())

        for keyword in keywords_unchanged:
            pattern = "[^a-z]" + keyword + "[^a-z]"
            regex = re.compile(pattern, re.IGNORECASE)
            for match in regex.finditer(sentence):
                count_unchanged += 1
                # print(match.group())

        for keyword in keywords_tighten:
            pattern = "[^a-z]" + keyword + "[^a-z]"
            regex = re.compile(pattern, re.IGNORECASE)
            for match in regex.finditer(sentence):
                count_tighten += 1
        counts = [count_ease, count_unchanged, count_tighten]
        print(counts)
        new_count = []
        if 0 in counts:
            new_count = counts.copy()
            new_count.remove(0)
        else:
            new_count = counts.copy()
        d_conflict = 0
        if len(new_count) >= 2:
            if sorted(new_count)[-1] == sorted(new_count)[-2]:
                d_conflict = 1

        sum_counts = sum(counts)
        labels = ["E", "U", "T"]
        if not sum_counts == 0 and not d_conflict == 1:
            index_max = np.argmax([count_ease, count_unchanged, count_tighten])
            # print(labels[index_max])
            row['predicted_treatment'] = labels[index_max]
            print(labels[index_max])
        else:
            row['predicted_treatment'] = "No assignment"
            print("no assignment")
    comp_df.to_csv("../output/romer_prediction.csv")




main()
