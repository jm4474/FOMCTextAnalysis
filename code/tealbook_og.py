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

directory='/Users/olivergiesecke/Dropbox/MPCounterfactual/code'
os.chdir(directory)

# list of documents
doc_list=['FOMC20131218tealbookb20131212', 'FOMC20131030tealbookb20131024', 'FOMC20130918tealbookb20130912', 'FOMC20130731tealbookb20130725', 'FOMC20130619tealbookb20130613', 'FOMC20130501tealbookb20130425', 'FOMC20130320tealbookb20130314', 'FOMC20130130tealbookb20130124', 'FOMC20121212tealbookb20121206', 'FOMC20121024tealbookb20121018', 'FOMC20120913tealbookb20120906', 'FOMC20120801tealbookb20120726', 'FOMC20120620tealbookb20120614', 'FOMC20120425tealbookb20120419', 'FOMC20120313tealbookb20120308', 'FOMC20120125tealbookb20120119', 'FOMC20111213tealbookb20111208', 'FOMC20111102tealbookb20111027', 'FOMC20110921tealbookb20110915', 'FOMC20110809tealbookb20110804', 'FOMC20110622tealbookb20110616', 'FOMC20110427tealbookb20110421', 'FOMC20110315tealbookb20110310', 'FOMC20110126tealbookb20110120', 'FOMC20101214tealbookb20101209', 'FOMC20101103tealbookb20101028', 'FOMC20100921tealbookb20100916', 'FOMC20100810tealbookb20100805', 'FOMC20100623tealbookb20100617']

for doc in doc_list:
    filename=doc

    if not os.path.exists("../output/TealbookB/"+filename):
        r = requests.get('https://www.federalreserve.gov/monetarypolicy/files/'+filename+".pdf")    
        open("../output/TealbookB/"+filename+".pdf", 'wb').write(r.content)
    
    #parsed = parser.from_file('tealbookcheck.pdf')
    #document['file_text'] = parsed['content']
    clean_parser = parser.from_file("../output/TealbookB/"+filename+".pdf")
    lines = clean_parser['content'].splitlines()
    output=""
    
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
            
                if re.search("[\s\w\“”\-,:;'’]*\s*Alternative\w*\s*[ABCD]\s[\s\w\“”\-,:;'’]*",p_text,re.IGNORECASE):
                    valid_line = True
                   # print(p_text)                            
                    if not d_continuation:
                        # Sentence ends in this line
                        if re.search("[\s\w\“”\-,:;'’]*\s*Alternative\w*\s*[ABCD]\s[\s\w\“”\-,:;'’]*\.",p_text,re.IGNORECASE):
                            d_continuation=False
                            # Begin and end in this line
                            if re.search("\.[\s\w\“”\-,:;'’]*\s*Alternative\w*\s*[ABCD]\s[\s\w\“”\-,:;'’]*\.",p_text,re.IGNORECASE):
                                match_string=re.search(".[\s\w\“”\-,:;'’]*\s*Alternative\w*\s*[ABCD]\s[\s\w\“”\-,:;'’]*\.",p_text,re.IGNORECASE).group()
                                line_ouput=match_string[2:]
                                #print(count,line_ouput)
                            else:
                                line_int_ouput=re.search("\s*Alternative\w*\s*[ABCD]\s[\s\w\“”\-,:;'’]*\.",p_text,re.IGNORECASE).group()                        
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
                                        rev_line=lines[count-i]
                                        if len(rev_line)>4 and not re.search("Class I FOMC",rev_line,re.IGNORECASE) and not re.search("Page\s\d{1,3}",rev_line,re.IGNORECASE) and not re.search("Authorized",rev_line,re.IGNORECASE):
                                            line_int_ouput=rev_line+" "+line_int_ouput
                                        i=i+1
                                
                                
                                #print(count,line_ouput)
                        else:
                            d_continuation=True
                            if re.search("\.[\s\w\“”\-,:;'’]*\s*Alternative\w*\s*[ABCD]\s[\s\w\“”\-,:;'’]*",p_text,re.IGNORECASE):
                                match_string=re.search("\.[\s\w\“”\-,:;'’]*\s*Alternative\w*\s*[ABCD]\s[\s\w\“”\-,:;'’]*",p_text,re.IGNORECASE).group()
                                line_ouput=match_string[2:]
                                #print(count,line_ouput)
                            else:
                                
                                line_int_ouput=re.search("[\s\w\“”\-,:;'’]*\s*Alternative\w*\s*[ABCD]\s[\s\w\“”\-,:;'’]*",p_text,re.IGNORECASE).group() 
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
                                            line_int_ouput=rev_line+" "+line_int_ouput
                                        i=i+1
                                
            else:
                valid_line = True
                if re.search("[\s\w\“”\-,:;'’]*\.",p_text,re.IGNORECASE):
                    line_ouput=re.search("[\s\w\“”\-,:;'’]*\.",p_text,re.IGNORECASE).group()   
                    d_continuation=False
                    # Check for new occurences of Alternative\w* in the line
                    if re.search("\.[\s\w\“”\-,:;'’]*\sAlternative\w*\s*[ABCD]\s[\s\w\“”\-,:;'’]*",p_text,re.IGNORECASE):
                        # Sentence ends in this line
                        if re.search("\.[\s\w\“”\-,:;'’]*\s*Alternative\w*\s*[ABCD]\s[\s\w\“”\-,:;'’]*\.",p_text,re.IGNORECASE):
                            d_continuation=False
                            line_int_ouput=re.search("\.[\s\w\“”\-,:;'’]*\s*Alternative\w*\s*[ABCD]\s[\s\w\“”\-,:;'’]*\.",p_text,re.IGNORECASE).group()                        
                            line_int_ouput=line_int_ouput[2:]
                        else:
                            d_continuation=True
                            line_int_ouput=re.search("\.[\s\w\“”\-,:;'’]*\s*Alternative\w*\s*[ABCD]\s[\s\w\“”\-,:;'’]*",p_text,re.IGNORECASE).group()
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
                output+=line_ouput.strip()+"\n\n" 
                #print(count,d_continuation)
            if valid_line and d_continuation:
                output+=line_ouput.strip()+" "   
                #print(count,d_continuation)
    clean_text=output
                    
    with open('../output/TealbookB_cleaned/'+filename,"w") as f:
        f.write(clean_text)                
        