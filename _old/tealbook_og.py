###############################################################################
### Set packages ###

import pandas as pd
import requests
from bs4 import BeautifulSoup
import datetime
import csv
from tika import parser
import re
import os

###############################################################################
### Set the working directory ###

directory='/Users/olivergiesecke/Dropbox/MPCounterfactual'
os.chdir(directory)

# =============================================================================
# ### Write Code for single Tealbook
# document = {'start_date': 20131218,'end_date': 20131218    }
# 
# filename="FOMC20131218tealbookb20131212.pdf"
# r = requests.get('https://www.federalreserve.gov/monetarypolicy/files/'+filename)
# 
# =============================================================================
#filename="FOMC20131218tealbookb20131212.pdf"
#r = requests.get('https://www.federalreserve.gov/monetarypolicy/files/'+filename)
# 
#parsed = parser.from_file('tealbookcheck.pdf')
#document['file_text'] = parsed['content']
clean_parser = parser.from_file('FOMC20131218tealbookb20131212.pdf')
lines = clean_parser['content'].splitlines()
output=""

lines[1821]
lines[1829]

lines[1838]

lines[1854]
lines[1855]

# Get all sentences that contain Alternatives
d_continuation=False
for count,line in enumerate(lines):
    
    # Search for the alternative keyword
    valid_line = False
    p_text = line.strip()
    #print(p_text)
    
    # Jump over empty lines
    if len(p_text)>4 and not re.search("Class I FOMC",p_text,re.IGNORECASE) and not re.search("Page\s\d{1,3}",p_text,re.IGNORECASE) and not re.search("Authorized",p_text,re.IGNORECASE):
    
    
        if not d_continuation:
        
            if re.search("[\s\w\“”\-,:;'’]*\s*Alternative\w*\s[ABCD]\s[\s\w\“”\-,:;'’]*",p_text,re.IGNORECASE):
                valid_line = True
               # print(p_text)                            
                if not d_continuation:
                    # Sentence ends in this line
                    if re.search("[\s\w\“”\-,:;'’]*\s*Alternative\w*\s[ABCD]\s[\s\w\“”\-,:;'’]*\.",p_text,re.IGNORECASE):
                        d_continuation=False
                        # Begin and end in this line
                        if re.search("\.[\s\w\“”\-,:;'’]*\s*Alternative\w*\s[ABCD]\s[\s\w\“”\-,:;'’]*\.",p_text,re.IGNORECASE):
                            match_string=re.search(".[\s\w\“”\-,:;'’]*\s*Alternative\w*\s[ABCD]\s[\s\w\“”\-,:;'’]*\.",p_text,re.IGNORECASE).group()
                            line_ouput=match_string[2:]
                            #print(count,line_ouput)
                        else:
                            line_int_ouput=re.search("\s*Alternative\w*\s[ABCD]\s[\s\w\“”\-,:;'’]*\.",p_text,re.IGNORECASE).group()                        
                            # Search for the previous beginning of the sentence
                            
                            d_iter=True
                            i=1
                            while d_iter:
                                # search for start of the sentence
                                if re.search("\.[\“\”\-,:;'’]*\s",lines[count-i]):
                                    match_string=re.search("\.[\“\”\-,:;'’]*\s[\s\w\“”\-,:;'’]*",lines[count-i]).group()
                                    match_string=match_string[2:]
                                    line_ouput=match_string+" "+line_int_ouput
                                    d_iter=False
                                else:
                                    line_int_ouput=lines[count-i]+" "+line_int_ouput
                                    i=i+1
                                    
                            
                            
                            #print(count,line_ouput)
                    else:
                        d_continuation=True
                        if re.search("\.[\s\w\“”\-,:;'’]*\s*Alternative\w*\s[ABCD]\s[\s\w\“”\-,:;'’]*",p_text,re.IGNORECASE):
                            match_string=re.search("\.[\s\w\“”\-,:;'’]*\s*Alternative\w*\s[ABCD]\s[\s\w\“”\-,:;'’]*",p_text,re.IGNORECASE).group()
                            line_ouput=match_string[2:]
                            #print(count,line_ouput)
                        else:
                            
                            line_int_ouput=re.search("[\s\w\“”\-,:;'’]*\s*Alternative\w*\s[ABCD]\s[\s\w\“”\-,:;'’]*",p_text,re.IGNORECASE).group() 
                            #print(count,line_ouput)
                            
                            d_iter=True
                            i=1
                            while d_iter:
                                # search for start of the sentence
                                if re.search("\.[\“\”\-,:;'’]*\s",lines[count-i]):
                                    match_string=re.search("\.[\“\”\-,:;'’]*\s[\s\w\“”\-,:;'’]*",lines[count-i]).group()
                                    match_string=match_string[2:]
                                    line_ouput=match_string+" "+line_int_ouput
                                    d_iter=False
                                else:
                                    rev_line=lines[count-i]
                                    if len(rev_line)>4 and not re.search("Class I FOMC",rev_line,re.IGNORECASE) and not re.search("Page\s\d{1,3}",rev_line,re.IGNORECASE) and not re.search("Authorized",rev_line,re.IGNORECASE):
                                        line_int_ouput=lines[count-i]+" "+line_int_ouput
                                    i=i+1
                            
        else:
            valid_line = True
            if re.search("[\s\w\“”\-,:;'’]*\.",p_text,re.IGNORECASE):
                line_ouput=re.search("[\s\w\“”\-,:;'’]*\.",p_text,re.IGNORECASE).group()   
                d_continuation=False
                # Check for new occurences of Alternative\w* in the line
                if re.search("\.[\s\w\“”\-,:;'’]*\sAlternative\w*\s*[ABCD]\s[\s\w\“”\-,:;'’]*",p_text,re.IGNORECASE):
                    # Sentence ends in this line
                    if re.search("\.[\s\w\“”\-,:;'’]*\s*Alternative\w*\s[ABCD]\s[\s\w\“”\-,:;'’]*\.",p_text,re.IGNORECASE):
                        d_continuation=False
                        line_int_ouput=re.search("\.[\s\w\“”\-,:;'’]*\s*Alternative\w*\s[ABCD]\s[\s\w\“”\-,:;'’]*\.",p_text,re.IGNORECASE).group()                        
                        line_int_ouput=line_int_ouput[2:]
                    else:
                        d_continuation=True
                        line_int_ouput=re.search("\.[\s\w\“”\-,:;'’]*\s*Alternative\w*\s[ABCD]\s[\s\w\“”\-,:;'’]*",p_text,re.IGNORECASE).group()
                        line_int_ouput=line_int_ouput[2:]
                    line_ouput=line_ouput+" "+line_int_ouput
                else:
                    d_continuation=False
                #print(count,p_text)
            else:
                line_ouput=p_text
                d_continuation=True
                #print(count,p_text)
    
        if valid_line and not d_continuation:
            output+=line_ouput+"\n\n" 
            print(count,d_continuation)
        if valid_line and d_continuation:
            output+=line_ouput+" "   
            print(count,d_continuation)
clean_text=output
                
with open('FOMC20131218tealbookOutput',"w") as f:
    f.write(clean_text)                
    