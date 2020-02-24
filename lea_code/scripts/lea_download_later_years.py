#Author Anand Chitale
import requests
from bs4 import BeautifulSoup
from bs4 import Tag
import csv
'''
@author Anand Chitale
#This script goes through every page of the FOMC historical website and extracts raw
metadata information on every relevant document on the website
outputing into raw_data.csv
'''
def download_raw_doc_metadata():
    documents = []
    start_date, end_date = 2010,2019
    year_pages = get_year_pages(start_date,end_date)
    for year in year_pages:
        soup = BeautifulSoup(year,'lxml')

        #Article Div Tag Contains All Meeting Tables
        meeting_container = soup.find("div", id="article")
        year = meeting_container.find("h3").text

        #contains a table of all documents in a meeting
        meeting_tables = meeting_container.findChildren("div",recursive=False)

        for meeting_table in meeting_tables:
            meeting_info = meeting_table.find("h5").text

            meeting_document_tables = meeting_table.find_all("div")[1]

            #each p tag contains a set of one of more links to documents of a type
            document_types = meeting_document_tables.find_all("p")
            for document_type in document_types:
                document_list = get_documents_and_links(document_type)
                grouping = get_grouping(document_type,document_list)
                #Append Meeting Specific Information to each document
                for document in document_list:
                    document['grouping'] = grouping
                    add_document(documents,document,year,meeting_info)

            #Catches any minutes that are not given in a p-tag, just written as text in the div
            meeting_document_lists = meeting_document_tables.find_all("div")
            for meeting_document_list in meeting_document_lists:
                non_p_text = ''.join(meeting_document_list.find_all(text=True, recursive=False))
                non_p_text += get_non_link_inner_text(meeting_document_list)
                if non_p_text and non_p_text.strip():
                    non_p_text = ' '.join(non_p_text.split())
                    document = {'document_name':non_p_text,
                                      'link': None
                                    }
                    grouping = get_grouping(document['document_name'],None)
                    document['grouping'] = grouping
                    add_document(documents,document,year,meeting_info)

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
    comment = ''
    document_name = ''
    ptext = document_type.find(text=True, recursive=False)
    if ptext and ptext.strip():
        ptext = ptext.strip()
        #Takes care of edge case where reference was in p_text and minutes in link
        if ptext[0] == "(":
            comment = ptext
        else:
            document_name = ptext
    document_name += get_non_link_inner_text(document_type)
    links = document_type.find_all("a")
    if not links:
        current_document = {}
        document_name += comment
        current_document['document_name'] = document_name
        current_document['link'] = None
        documents.append(current_document)
    else:
        for link in links:
            cur_doc_name = document_name + link.text
            cur_doc_name += comment
            current_document = {}
            current_document['document_name'] = cur_doc_name
            current_document['link'] = link.get("href")
            documents.append(current_document)
    return documents

def add_document(documents,document,year,meeting_info):
    document['year'] = year
    document['meeting_info'] = meeting_info
    documents.append(document)

# Writes information to CSV File
def write_to_csv(documents):
    with open('../output/lea_raw_data.csv', 'w') as csvfile:
        fieldnames = ['year', 'meeting_info', 'document_name', 'link', 'grouping']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for document in documents:
            writer.writerow(document)
#We are only concerned with p tag text and the like, not link text
def get_non_link_inner_text(tag):
    inner_text = ''
    for child in tag.find_all(recursive=False):
        if type(child) == Tag and child.name == "em":
             inner_text += child.text
    return inner_text
#Finds the grouping of the file based on properties of the fomc website
def get_grouping(document_type,document_list):
    if type(document_type) == str and document_list is None:
        grouping = document_type
    else:
        document_type_text = document_type.find(text=True, recursive=False)

        #Takes care of edge case where reference was in p_text and minutes in link
        if document_type_text and document_type_text.strip() \
                and not document_type_text.strip()[0]=="(":
            grouping = document_type_text
        else:
            grouping = document_list[0]['document_name']
    return grouping

if __name__ == "__main__":
    download_raw_doc_metadata()
