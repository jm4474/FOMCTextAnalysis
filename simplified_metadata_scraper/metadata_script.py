#Author: Anand Chitale June 3rd 2013
import requests
from bs4 import BeautifulSoup
import csv

def main():
    documents = []
    start_date = 1936
    end_date = 2013

    year_pages = get_year_pages(start_date,end_date)
    for year in year_pages:
        soup = BeautifulSoup(year,'lxml')
        #Article Div Tag Contains All Meeting Tables
        meeting_container = soup.find("div",id="article")
        year = meeting_container.find("h3").text
        #contains a table of all documents in a meeting
        meeting_tables = meeting_container.findChildren("div",recursive=False)
        for meeting_table in meeting_tables:
            #header which contains date and type of event
            meeting_info = meeting_table.find("h5").text
            #each p tag contains a set of one of more links to documents of a type
            materials = meeting_table.find_all("p")
            for material in materials:
                documents_and_links = get_documents_and_links(material)
                #Append Meeting Specific Information to each document
                for document in documents_and_links:
                    document['meeting_info'] = meeting_info
                    document['year'] = year
                    documents.append(document)
    #writes to csv file in current working directory
    write_to_csv(documents)
def get_year_pages(start_date,end_date):
    base_time_url = "https://www.federalreserve.gov/monetarypolicy/fomchistorical"

    # dictionary which holds each years page
    year_pages = []

    for year in range(start_date,end_date+1):
        url = base_time_url + str(year) + '.htm'
        resp = requests.get(base_time_url + str(year) + '.htm')
        if resp.status_code == requests.codes.ok:
            year_pages.append(resp.content)
        else:
            print("error occured. Could not get information for year:{} with url:{}".format(year,url))
            continue
    return year_pages


def get_documents_and_links(document_type):
    documents = []
    ptext = document_type.find(text=True,recursive=False)
    doc_name = ''
    if ptext and ptext.strip():
        doc_name = ptext
    links = document_type.find_all("a")
    if not links:
        current_document = {}
        current_document['document_name'] = doc_name
        current_document['link'] = None
        documents.append(current_document)
    else:
        for link in links:
            cur_doc_name = doc_name + link.text
            current_document = {}
            current_document['document_name'] = cur_doc_name
            current_document['link'] = link.get("href")
            documents.append(current_document)
    return documents

# Writes information to CSV File
def write_to_csv(documents):
    with open('test_metadata.csv', 'w') as csvfile:
        fieldnames = ['year', 'meeting_info', 'document_name', 'link']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for document in documents:
            writer.writerow(document)

if __name__ == "__main__":
    main()