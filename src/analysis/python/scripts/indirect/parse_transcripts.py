import pandas as pd
import os
import re
import pprint
import shutil

def main():
    speaker_statements = get_speaker_statements()
    get_speaker_corps(pd.read_pickle("../../output/speaker_data/speaker_corpus.pkl"))
def get_speaker_statements():
    base_directory = base_directory = "../../../../collection/python/data/transcript_raw_text"
    raw_doc = os.listdir(base_directory)
    filelist = sorted(raw_doc)
    documents = []
    if os.path.exists("../../output/speaker_data"):
        shutil.rmtree("../../output/speaker_data")
    os.mkdir("../../output/speaker_data")

    for doc_path in filelist:
        with open("{}/{}".format(base_directory,doc_path),'r') as f:
            documents.append(f.read().replace("\n"," ").replace(":",".").replace(r"\s\s+"," "))
    date = pd.Series(data=filelist).apply(lambda x: x[0:10])
    #print(date)
    parsed_text = pd.DataFrame()
    for doc_index in range(len(documents)):
        if doc_index%10 == 0:
            print("Working on producing interjections for doc #{} of ~{}".format(doc_index,len(documents)))
        #THIS METRIC FAILES FOR 59 out of 4857 occurances
        interjections    = re.split(' MR\. | MS\. | CHAIRMAN | VICE CHAIRMAN ', documents[doc_index])[1:] 
                    
        temp_df          = pd.DataFrame(columns=['Date','Speaker','content'],index=range(len(interjections)))          
                    #Temporary data frame

        for j in range(len(interjections)):
            interjection           = interjections[j]

            temp_df['Date'].loc[j]    = date[doc_index]
            #speaker = "".join([char for char in  if char.isalnum()])
            temp_df['Speaker'].loc[j] = interjection.split('.')[0].strip()

            temp_df['content'].loc[j] = ''.join(interjection.split('.')[1:])

        parsed_text = pd.concat([parsed_text,temp_df],ignore_index=True)
    parsed_text.to_csv("../../output/interjections.csv")
    
    speaker_statements = parsed_text.groupby(['Date','Speaker']).sum().reset_index()
    speaker_statements = speaker_statements[speaker_statements['Speaker'].apply(lambda x:len(x.split())==1)]
    speaker_statements = speaker_statements[speaker_statements['Speaker'].apply(lambda x:x.isalpha())]

    #Speaker D. Lindsey. messes up our dataset 9 times, so we apply a manual adjustment.
    speaker_statements["content"] = speaker_statements["content"].apply(lambda x: " ".join(str(x).split()[1:]) if str(x).split()[0]=="LINDSEY" else x)
    speaker_statements["Speaker"] = speaker_statements["Speaker"].apply(lambda x: "LINDSEY" if x=="D" else x)

    #Correct Typos
    with open("../../data/speaker_typos.txt",'r') as f:
        for line in f.readlines():
            correct = line.split()[0]
            errors = line.split()[1:]
            for error in errors:
                speaker_statements["Speaker"] = speaker_statements["Speaker"].apply(lambda x: correct if x==error else x)
    

    speaker_statements.to_pickle("../../output/speaker_data/speaker_corpus.pkl")
    speaker_statements.to_csv("../../output/speaker_data/speaker_corpus.csv")
    print("Completed generating speaker statements!")
    return speaker_statements

def get_speaker_corps(speaker_statements):
    speakers = [speaker for speaker in set(speaker_statements["Speaker"])]
    print("Number of speakers:{}".format(len(speakers)))
    count = 0
    for speaker in speakers:
        #print("Currently working on statements for speaker {} of {}. Name:{}".format(count,len(speakers),speaker))
        speaker_df = speaker_statements[speaker_statements["Speaker"]==speaker]
        speaker_path = "{}/{}".format("../../output/speaker_data",speaker)
        if not os.path.exists(speaker_path):
            os.mkdir(speaker_path)
        
        speaker_list = list(speaker_df["content"])
        with open("{}/{}_{}".format(speaker_path,speaker,"corpus.txt"),"w+") as f:
            f.write(" ".join(speaker_list))
        count+=1

if __name__ == "__main__":
        main()