import os
import pandas as pd
import re
def main():
    dir = "../../../collection/python/output/bluebook_raw_text"
    raw_text_df = pd.DataFrame()
    for file in os.listdir(dir):
        with open(dir+"/"+file) as f:
            text = f.read().replace("\n"," ")
            raw_text_df = raw_text_df.append({'date':file.replace(".txt",""),'raw_text':text},ignore_index=True)
    pattern = ".{1000}alternatives?\s+[a-e]\s.{1000}"
    regex = re.compile(pattern, re.IGNORECASE)

    basket = ['inflation','unemployment','monetary policy','productivity','market expectation']

    for i in raw_text_df.index:
        match = re.findall(regex,raw_text_df.at[i,'raw_text'])
        if match:
            match_text = "\n\n\n".join(match)
            raw_text_df.at[i, 'matches'] = match_text
            alternatives = re.findall("alternatives?\s+[a-e]",match_text)
            raw_text_df.at[i,'alternatives'] = alternatives
            for term in basket:
                term_matches = []
                for match in raw_text_df.at[i,'matches'].split("\n\n\n"):
                    #print(match)
                    sentences = match.split(".")
                    for sentence in sentences:
                        print(sentence)
                        if term in sentence:
                            term_matches.append(sentence+".")

                #term_sentence = "\. .*"+term+".*\."
                #search = re.findall(term_sentence,raw_text_df.at[i, 'matches'])
                column_name = term.replace(" ","_")
                if term_matches:
                    print("found")
                    raw_text_df.at[i, column_name] = "\n".join(term_matches)

    raw_text_df.to_csv("../output/alternative_window_text_topics.csv")
if __name__ == "__main__":
    main()