import pandas as pd
import requests
from bs4 import BeautifulSoup
import datetime
import csv
import tika
from tika import parser
def main():
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
            document = download_pdf(file)
        documents.append(document)
    write_statement_csv(documents,grouping)

def download_pdf(file):
    document = {
        'start_date': file['start_date'],
        'end_date': file['end_date']
    }
    r = requests.get(file['link'])
    open("../output/Bluebook/"+file['start_date'], 'wb').write(r.content)
    parsed = parser.from_file("../output/Bluebook/"+file['start_date'])
    document['file_text'] = parsed['content']
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

if __name__ == "__main__":
    main()