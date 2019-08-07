import os
import pandas as pd
import re
def main():
    dir = "../../../collection/python/output/bluebook_raw_text"
    df = pd.DataFrame()
    for file in os.listdir(dir):
        with open(dir + "/" + file) as f:
            text = f.read().replace("\n", " ")
            df = df.append({'date': file.replace(".txt", ""), 'raw_text': text}, ignore_index=True)

    for i in df.index:
        raw_text = df.loc[i,'raw_text']
        sentences = raw_text.split(".")
        string = re.compile("expectations?",re.IGNORECASE)
        exp_sents = [sentence+'.' for sentence in sentences if re.search(string,sentence)]
        if exp_sents:
            df.loc[i,'sentences']=exp_sents
            df.loc[i,'sentence_counts'] = str(len(exp_sents))
            df.loc[i,'d_inflation'] = "inflation" in "".join(exp_sents)
            df.loc[i,'d_unemployment'] = "unemployment" in "".join(exp_sents)
            df.loc[i,'d_rates'] = "rates" in "".join(exp_sents)
            df.loc[i,'d_market_expectations'] = "market expectations" in "".join(exp_sents)
            df.loc[i,'d_ffr'] = "federal funds rate"in "".join(exp_sents)
    df.to_csv("../output/bluebook_text_expectations.csv")
if __name__ == "__main__":
    main()