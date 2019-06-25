"""
Purpose: Loads the bluebook data from the raw files and extracts the sentences 
         that are affiliated with the alternatives and creates file.
@author: olivergiesecke
"""

###############################################################################
### Set packages ###

import pandas as pd
import re
import os

###############################################################################
# Open points:
# 1) Handling of footnotes. Right now, they are mixed into sentence at the end 
# of the page. This interrupts the sentence that do not end at the end of the 
#page.
# 2) Think about the use of nltk for the extraction of the relevant information
# 3) Adjust the cloud of words to be more relevant to our objective.
###############################################################################

def main():
    ## Read data and define sample
    df_output=getdata_bluebook()
    # Write data frame to csv
    if not os.path.isdir("../output/"):
        os.mkdir("../output/")
    df_output.to_csv("../output/bluebook_alternatives.csv")
    
### Define data download
def getdata_bluebook():
    # Get all files except the hidden
    doc_list=[]
    for item in os.listdir("../../../collection/python/output/bluebook_raw_text/"):
        if not item.startswith('.'):
            doc_list.append(item)
    
    files=[]
    for idx,doc in enumerate(doc_list):
        print(idx," Working on file", doc)
        # Do for specific document
        #doc=doc_list[20]
        
        # Open the file
        with open("../../../collection/python/output/bluebook_raw_text/"+doc,'r') as f:
            # Read document line by line
            lines=f.readlines()
        
            cleaned_lines=[]
            for line in lines:
                # Replace linebreaks with space
                line=line.replace("\n"," ")
                # Remove empty lines 
                if not re.match(r'^\s*$', line):
                    #Remove four character lines that do not end with period
                    #regex = r".{1,4}(?<!\.)$"
                    #if not re.match(regex, line):
                    cleaned_lines.append(line)
            # Make a single element from list.
            text="".join(cleaned_lines)            
        
        # Search for alternative(s) and keep the sentence
        all_sentences=[]
        pattern = "([^.]*)(alternatives?\s+[a-e])(\.|[^a-z]\.|[^a-z][^\.]+\.)"
        regex = re.compile(pattern, re.IGNORECASE)
        for match in regex.finditer(text):
            all_sentences.append(match.group())
            
        data={"meeting_date":doc[:-4],"n_sentences":len(all_sentences),"sentences":all_sentences}
        
        # Search for alternative {a,b,c,d,e} and keep the sentence
        for alt in ["a","b","c","d","e"]:
            alt_sentences=[]
            pattern = "([^.]*)(alternative\s+"+alt+")(\.|[^a-z]\.|[^a-z][^\.]+\.)"
            regex = re.compile(pattern, re.IGNORECASE)
            for match in regex.finditer(text):
                alt_sentences.append(match.group())
            alt_sent="alt_"+alt+"_sentences"
            alt_count="alternative_"+alt+"_count"
            data.update({alt_sent:alt_sentences,alt_count:len(alt_sentences)})
    
        # Collect all files in the data file
        files.append(data)            
        
    # Collect output in dataframe
    return pd.DataFrame(files)

if __name__ == "__main__":
   main()
