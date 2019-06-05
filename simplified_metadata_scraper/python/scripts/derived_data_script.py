import pandas as pd
import re
import csv
def main():
    raw_df = pd.read_csv("../output/raw_data.csv")
    documents = []
    for index, row in raw_df.iterrows():
        cur_document = {}
        meeting_info = row['meeting_info']
        if "(unscheduled)" in meeting_info:
            meeting_info = meeting_info.replace("(unscheduled)","Conference Call")

        document_name = row['document_name']
        link = row['link']


        # cur_document['type'] = extract_type(meeting_info)
        cur_document['year'] = row['year']
        cur_document['event_type'] = extract_event_type(meeting_info)
        cur_document['file_name'] = extract_file_name(document_name)
        cur_document['file_size'] = extract_file_size(document_name)
        cur_document['link'] = extract_link(link)


        date_info = meeting_info.split(cur_document['event_type'])[0]
        if "," in date_info:
            date_info = date_info.split(",")[0] + "-" + date_info.split("and ")[1]

        start_date = extract_start_date(date_info)
        end_date = extract_end_date(date_info, start_date)
        cur_document['start_date'] = '{} {}'.format(start_date['month'],start_date['day'])
        cur_document['end_date'] = '{} {}'.format(end_date['month'],end_date['day'])

        documents.append(cur_document)
    write_derived_csv(documents)

def extract_start_date(date_info):
    start_date = {}
    if "-" in date_info:
        if "/" in date_info:
            start_date['month'] = date_info.split('/')[0]
            start_date['day'] = date_info.split(" ")[1].split("-")[0]
        else:
            start_date['month'] = date_info.split(" ")[0]
            start_date['day'] = date_info.split(" ")[1].split("-")[0]
    else:
        start_date['month'] = date_info.split(" ")[0]
        start_date['day'] = date_info.split(" ")[1]
    return start_date

def extract_end_date(date_info,start_date):
    end_date = {}
    if "-" in date_info:
        if "/" in date_info:
            end_date['month'] = date_info.split("/")[1].split(" ")[0]
            end_date['day'] = date_info.split("-")[1]
        else:
            end_date['month'] = start_date['month']
            end_date['day'] = date_info.split("-")[1]
    else:
        end_date['month'] = start_date['month']
        end_date['day'] = start_date['day']
    return end_date

def extract_event_type(meeting_info):
    if 'Conference Call' in meeting_info:
        return "Conference Call"
    elif 'Meeting' in meeting_info:
        return 'Meeting'
    else:
        return None

def extract_file_name(document_name):
    #Gets rid of the file_size in parentheses including the file extension
    file_name = re.sub("(\()([0-9])?(\.)?([0-9]{1,3})( )(MB|KB)( )(\w{1,5})(\))",'',document_name)
    #Gets rid of the file size without parentheses while preserving the file extension
    file_name = re.sub("([0-9])?(\.)?([0-9]{1,3})( )(MB|KB)( )",'',file_name)
    file_name = ' '.join(file_name.split())
    return file_name

def extract_file_size(document_name):
    #Regular expression which searches for a file_size in the format (size)( )(mb/kb)( )(file_type)
    result = re.search("([0-9])?(\.)?([0-9]{1,3})( )(MB|KB)( )(\w{1,5})",document_name)
    if result:
        return result.group()
    else:
        return None

def extract_link(link):
    if type(link)!= str :
        return
    base = "https://www.federalreserve.gov"
    if link[0] == "/":
        return base+link
    else:
        return link

def write_derived_csv(documents):
    with open('../output/derived_data.csv', 'w') as csvfile:
        fieldnames = ['year', 'start_date', 'end_date', 'event_type', 'file_name', 'file_size', 'link']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for document in documents:
            writer.writerow(document)

main()