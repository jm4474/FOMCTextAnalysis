import pandas as pd
import requests
from bs4 import BeautifulSoup
import datetime
import csv
import tika
from tika import parser
import re
import os
def main():
    download_clean = True
    if download_clean and not os.path.isdir("../output/clean_bluebook"):
        os.mkdir("../output/clean_bluebook")
    data_file_name = "../output/derived_data.csv"
    grouping = "Bluebook"
    start_year = 1965
    end_year = 2013
    df = pd.read_csv(data_file_name)
    files = []
    for index, row in df.iterrows():

        if row['grouping'] == grouping and \
                row['link'] and int(row['year']) in range(start_year,end_year+1):
            files.append({'link':row['link'],
                          'start_date':row['start_date'],
                          'end_date':row['end_date'],
                          'year':row['year']
                          }
                         )
    documents = []
    for file in files:
        if grouping == "Statement":
            tika.initVM()
            document =  download_html(file)
        elif grouping == "Bluebook":
            document = download_pdf(file,download_clean)
        documents.append(document)
    write_statement_csv(documents,grouping)

def download_pdf(file,download_clean):
    document = {
        'start_date': file['start_date'],
        'end_date': file['end_date']
    }
    if not os.path.exists("../output/Bluebook/"+file['start_date']):
        r = requests.get(file['link'])
        open("../output/Bluebook/"+file['start_date'], 'wb').write(r.content)
    parsed = parser.from_file("../output/Bluebook/"+file['start_date'])
    document['file_text'] = parsed['content']
    clean_parser = parser.from_file("../output/Bluebook/"+file['start_date'],xmlContent=True)
    clean_text = clean_pdf(clean_parser,document['start_date'])
    if download_clean == True:
        with open("../output/clean_bluebook/"+document['start_date'],"w") as f:
            f.write(clean_text)
    else:
        document['clean_text'] = clean_text
    return document

def download_html(file):
    statement = {
        'start_date': file['start_date'],
        'end_date': file['end_date']
    }
    file_text = ""
    r = requests.get(file['link']).content
    soup = BeautifulSoup(r,'lxml')
    p_tags = soup.find_all("p",attrs={'class':None})
    for p_tag in p_tags:
        if p_tag.text and p_tag.text.strip() and len(p_tag.contents) == 1:
            file_text = file_text + " " + p_tag.text
    statement['file_text'] = file_text
    if int(file['year']) > 2005:
        date_search = soup.find("p",class_='article__time')
        if date_search:
            date = date_search.text
    else:
        date_search = soup.find("i")
        if date_search:
            date = date_search.text.split(": ")[1]
    if date:
        formatting = "%B %d, %Y"
        date_object = datetime.datetime.strptime(date, formatting).date()
        statement['release_date'] = date_object
    else:
        statement['release_date'] = None
    return statement

def write_statement_csv(statements,grouping):
    with open('../output/'+grouping+'.csv', 'w') as csvfile:
        fieldnames = list(statements[0].keys())
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for statement in statements:
            writer.writerow(statement)

def clean_pdf(clean_parser, start_date):
    need_manual = ['1970-10-20','1973-06-18','1989-03-28','1995-11-15']
    soup = BeautifulSoup(clean_parser['content'], 'lxml')
    output = ""

    pages = soup.find_all("div")
    reached_appendix = False
    for page in pages:
        if reached_appendix:
            break
        valid_page = True
        if page.text and page.text.strip():
            ps = page.find_all("p", text=True)
            for p in ps:
                valid_line = True
                p_text = p.text.strip()

                # print(re.search("(^Appendix)(\s)(\w)(:)",p_text,re.IGNORECASE))
                if re.search("(^Appendix)(\s)(\w)$", p_text, re.IGNORECASE) \
                        or re.search("(^Appendix)(\s)(\w)(:)", p_text, re.IGNORECASE):
                    reached_appendix = True

                elif re.search("^(Chart )(\d){1,5}$", p_text)\
                        or re.search("(CHART )(\d){1,5}",p_text):
                    valid_page = False

                elif re.search("^Appendix Table (\w){1,5}",p_text,re.IGNORECASE):
                    valid_page= False

                if reached_appendix or not valid_page:
                    break

                #Line Specific Classifier
                # Page Number
                elif re.search("^(-)( ?)(\d{1,3})( ?)(-)$", p_text):
                    valid_line = False
                # FootNote
                elif re.search("(^\d{1,3})(\.)( )", p_text):
                    valid_line = False

                # Handle Rogue Numbers
                elif re.search("^(-)?(\d{1,3})(\.)?(\d{1,3})?", p_text):
                    valid_line = False

                #Handle table data such as 12.5 10.5
                elif re.search("((-)?(\d{1,2})(\.)?(\d{1,2})?(\s)){3}", p_text):
                    valid_line = False
                elif re.search("^NOTE", p_text, re.IGNORECASE):
                    valid_line = False
                elif len(p_text.split()) <= 1:
                    valid_line = False

                if start_date in need_manual:
                    result = manual_transformations(p_text, start_date)
                    if result:
                        if result == "ESCAPE":
                            print("TERMINATED WRITING FOR FILE" + start_date)
                            reached_appendix = True
                            break
                        print("doing manual transform of file from {} to {}"\
                              .format(p_text, result)
                              )
                        p_text=result
                if valid_line:
                    output+=p_text+"\n"
    return output

def manual_transformations(p_text,start_date):
    if '(7) "Moderate growth' in p_text and start_date=="1970-10-20":
        return p_text.replace("\"Moderate","Moderate")
    elif "(12)- M3 is" in p_text and start_date=="1989-03-28":
        return p_text.replace("- M3"," M3")
    elif "(1). Over the" in p_text and start_date=="1995-11-15":
        return p_text.replace("(1).", "(1)")
    elif "TABLE 1" in p_text and start_date=="1973-06-18":
        return "ESCAPE"
    else:
        return None

if __name__ == "__main__":
    main()