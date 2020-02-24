import pandas as pd
import os
from shutil import rmtree
    
def perform_change():
    df = pd.read_csv("../../output/fed_targets_with_alternatives.csv")
    if os.path.exists("../../output/change_labeled_alternatives_corpora"):
        rmtree("../../output/change_labeled_alternatives_corpora")
    os.mkdir("../../output/change_labeled_alternatives_corpora/")
    counter = 0
    os.chdir("../../data/alternatives_corpora")
    for filename in os.listdir():
        counter+=1
        print(f'working on file numer {counter} of {len(os.listdir())}')
        if ".txt" not in filename:
            continue
        with open(filename) as f:
            lines = f.readlines()
            numerical_lines = []
            sign_lines = []
            for line in lines:
                if line.strip():
                    alt = line.split()[0]
                    assert(alt in ["a","b","c","d"])
                    query = df[df.date==filename.split(".")[0]]
                    if len(query)==0:
                        break
                        
                    change = str(query[f"bluebook_treatment_size_alt_{alt}"].item())
                    print(change)
                    numerical_value = float(str(query[f"bluebook_treatment_size_alt_{alt}"].item()))
                    if(numerical_value>0):
                        sign="+"
                    elif(numerical_value<0):
                        sign="-"
                    else:
                        sign="0"
                    numerical_line = change+" " + " ".join(line.strip().split()[1:])
                    numerical_lines.append(numerical_line)

                    sign_line = sign+" " + " ".join(line.strip().split()[1:])
                    sign_lines.append(sign_line)
            with open(f'../../output/change_labeled_alternatives_corpora/{filename}','w+') as f:
                for line in numerical_lines:
                    f.write(line)
                    f.write("\n")
            with open(f'../../output/sign_labeled_alternatives_corpora/{filename}','w+') as f:
                for line in sign_lines:
                    f.write(line)
                    f.write("\n")
        

if __name__ == "__main__":
    perform_change()