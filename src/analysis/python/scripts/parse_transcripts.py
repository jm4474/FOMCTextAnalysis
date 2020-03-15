import pandas as pd
import os
import re
import pprint
import shutil

    # Clean all the obvious typos
corrections ={'BAUGHWJV':'BAUGHMAN',
              'BOHNE':'BOEHNE',
              'EISEMENGER':'EISENMENGER',
              'GEITHER':'GEITHNER',
              'KIMBREL':'KIMEREL',
              'MATTINGLY': 'MATTLINGLY',
              'FORESTALL':'FORRESTAL',
              'GRENSPAN':'GREENSPAN',
              'GREESPAN':'GREENSPAN',
              'GREENPSAN':'GREENSPAN',
              'GREENSPAN,':'GREENSPAN',
              'GREENPAN':'GREENSPAN',
              'McANDREWS':'MCANDREWS',
              'MCDONUGH':'MCDONOUGH',
              'MOSCOW':'MOSKOW',
              'MORRIS':'MORRRIS',
              'MONHOLLAN':'MONHOLLON',
              'MILIER':'MILLER',
              'MILER':'MILLER',
              'SCWLTZ':'SCHULTZ',
              'SCHELD':'SCHIELD',
              'WILLZAMS':'WILLIAMS',
              'WALLJCH':'WALLICH',
              'VOLCKFR':'VOLCKER',
              'VOLCRER':'VOLKER',
              'ALLISON for':'ALLISON',
              'ALTMA"':'ALTMANN',
              'B A U G W':'BAUGW',
              'BIES (as read by Ms':'BIES',
              'BLACK &':'BLACK',
              'MAYO/MR':'MAYO',
              'Greene':"GREENE",
              'CROSS,':'CROSS',
              'GREENSPAN,':'GREENSPAN',
              'HOSKINS,':'HOSKINS',
              'MACCLAURY':'MACLAURY',
              'MORRRIS':'MORRIS',
              "O'CONNELL":'O’CONNELL',
              'SOLOMON]':'SOLOMON',
              'TRUMAN-':'TRUMAN',
              'VOLCKER,':'VOLCKER',
              'VOLKER,':'VOLCKER',
              'WALLlCH':'WALLICH',
              '[BALLES]':'BALLES',
              '[GARDNER]':'GARDNER',
              '[KICHLINE]?':'KICHLINE',
              '[PARDEE]':'PARDEE',
              '[ROOS]':'ROOS',
              '[STERN':'STERN',
              '[WILLES]':'WILLES',
              'ŞAHIN':'SAHIN',
              '[STERN(?)':'STERN',
              '[STERN]':'STERN',
              'GRALEY':'GRAMLEY',
              'ALTMA”':'ALTMANN'}

              
            
                  
def name_corr(val):
    sentence=""
    dictkeys=[key for key, value in corrections.items()]
    if val in dictkeys:
        val = corrections[val]    
    else:
        if re.match(".*\(\?\)",val):
            val = re.search("(.*)(\(\?\))",val)[1]
            if val in dictkeys:
                val = corrections[val]  
            
        if len(val.split(" "))>1:
            #print(val.split(" ")[0])
            #print(val.split(" ")[1:])
            sentencehelp = " ".join(val.split(" ")[1:])
            if not len(re.findall("Yes",sentencehelp))>7:
                if len(sentencehelp)>10:
                    sentence = sentencehelp
                    #print(sentence)
            val = val.split(" ")[0]
            if val in dictkeys:
                val = corrections[val]              
    #print(val)       
    return val,sentence

def get_speaker_statements():
    base_directory = base_directory = "../../../collection/python/data/transcript_raw_text"
    raw_doc = os.listdir(base_directory)
    filelist = sorted(raw_doc)
    documents = []
    if os.path.exists("../output/speaker_data"):
        shutil.rmtree("../output/speaker_data")
    os.mkdir("../output/speaker_data")
    
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
            
            speakercontent = interjection.split('.')[0].strip()
            
            name,sentence = name_corr(speakercontent)
            
            content = ''.join(interjection.split('.')[1:])
            
            if not sentence=="":
                content = sentence +" "+content
                #print(content)
            
            temp_df['Speaker'].loc[j] = name
    
            temp_df['content'].loc[j] = content
    
        parsed_text = pd.concat([parsed_text,temp_df],ignore_index=True)
        
        
    parsed_text.to_pickle("parsed_text.pkl")
    parsed_text = pd.read_pickle("parsed_text.pkl")
    
    #speakerlist = sorted(parsed_text["Speaker"].unique().tolist())
    
    
    # Get names of indexes for which we have an unidentified speaker and drop those
    indexNames = parsed_text[ (parsed_text['Speaker'] == 'mY0') | (parsed_text['Speaker'] == 'WL”') | (parsed_text['Speaker'] == 'W') | (parsed_text['Speaker'] == 'AL"N')  ].index
    parsed_text.drop(indexNames , inplace=True)
    
    parsed_text["content"] = parsed_text["content"].apply(lambda x: " ".join(str(x).split()[1:]) if len(str(x).split())>1 and str(x).split()[0]=="LINDSEY" else x)
    parsed_text["Speaker"] = parsed_text["Speaker"].apply(lambda x: "LINDSEY" if x=="D" else x)
    
    # Delete content with a check for presence of members.
    #parsed_text['check']=parsed_text['content'].apply(lambda x: len(re.findall("Yes",x)))
    #parsed_text['d_presence']=parsed_text['check']>7
    
     
    parsed_text.to_csv("../output/interjections.csv")
    
    speaker_statements = parsed_text.groupby(['Date','Speaker'])['content'].apply(lambda x: "%s" % " ".join(x))
    speaker_statements = speaker_statements.reset_index()
    
    dates_df = pd.read_csv("../../../collection/python/output/derived_data.csv")
    speaker_statements = speaker_statements.merge(dates_df[["start_date","end_date"]].drop_duplicates(),left_on="Date",right_on="start_date",how="left")
        
    speaker_statements.to_pickle("../output/speaker_data/speaker_corpus.pkl")
    speaker_statements.to_csv("../output/speaker_data/speaker_corpus.csv")
    print("Completed generating speaker statements!")
    return speaker_statements

def get_speaker_corps(speaker_statements):
    speakers = [speaker for speaker in set(speaker_statements["Speaker"])]
    print("Number of speakers:{}".format(len(speakers)))
    count = 0
    for speaker in speakers:
        print("Currently working on statements for speaker {} of {}. Name:{}".format(count,len(speakers),speaker))
        speaker_df = speaker_statements[speaker_statements["Speaker"]==speaker]
        speaker_path = "{}/{}".format("../output/speaker_data",speaker)
        if not os.path.exists(speaker_path):
            os.mkdir(speaker_path)
        speaker_df[['Date','content']].to_csv("{}/{}_{}".format(speaker_path,speaker,"statements_by_meeting.csv"))
        speaker_list = list(speaker_df["content"])
        with open("{}/{}_{}".format(speaker_path,speaker,"corpus.txt"),"w+") as f:
            f.write(" ".join(speaker_list))
        count+=1
        
def main():
    speaker_statements = get_speaker_statements()
    get_speaker_corps(speaker_statements)


if __name__ == "__main__":
    main()
        
# =============================================================================
# ## Do some checks:  
# with open('../../output/data.json', 'r') as speakerids:
#     speakerid = json.load(speakerids)
#     
# speakerlist = [ x.lower() for x in speaker_statements["Speaker"].unique().tolist()]
# 
# for key,value in speakerid.items():
#     if key.lower() not in speakerlist:
#         print(key)
#     else:
#         print('in list')
# 
# =============================================================================

