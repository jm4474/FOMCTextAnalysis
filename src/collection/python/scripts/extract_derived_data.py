import pandas as pd
import re
import csv
import datetime

#This program reads in the raw FOMC scraped metadata and produces
#A readable and actionable derived data csv for data download

def main():
    raw_df = pd.read_csv("../output/raw_data.csv")
    documents = []
    for index, row in raw_df.iterrows():
        cur_document = {}
        meeting_info = row['meeting_info']
        if "(unscheduled)" in meeting_info:
            meeting_info = meeting_info.replace("(unscheduled)", "Conference Call")

        document_name = row['document_name']
        link = row['link']
        grouping = row['grouping']
        year = row['year']
        print("Document Name:{}".format(document_name))
        print("Meeting Info:{}".format(meeting_info))
        cur_document['year'] = str(year)
        cur_document['event_type'] = extract_event_type(meeting_info)
        cur_document['file_name'] = extract_file_name(document_name)
        cur_document['file_type'] = extract_file_type(link,document_name)
        cur_document['file_size'] = extract_file_size(document_name)
        cur_document['link'] = extract_link(link)
        cur_document['grouping'] = extract_grouping(grouping)
        cur_document['document_class'] = extract_document_class(cur_document['grouping'])

        date_info = meeting_info.split(cur_document['event_type'])[0]
        print("Date Info:{}".format(date_info))
        if "," in date_info:
            date_info = date_info.split(",")[0] + "-" + date_info.split("and ")[1]
        start_date = extract_start_date(date_info, year)
        end_date = extract_end_date(date_info, start_date, year)
        cur_document['start_date'] = start_date
        cur_document['end_date'] = end_date

        documents.append(cur_document)
    documents = do_manual_derived_changes(documents)
    write_derived_csv(documents)

def extract_start_date(date_info,year):
    if "-" in date_info:
        if "/" in date_info:
            month = date_info.split('/')[0]
            day = date_info.split()[1].split("-")[0]
        else:
            month = date_info.split()[0]
            day = date_info.split()[1].split("-")[0]
    else:
        month = date_info.split()[0]
        day = date_info.split()[1]
    formatting = "%B %d %Y"
    date_string = "{} {} {}".format(month, day, year)
    date_object = datetime.datetime.strptime(date_string, formatting).date()
    if date_object:
        return date_object
    else:
        return None

def extract_end_date(date_info,start_date,year):
    new_month = False
    if "-" in date_info:
        if date_info.split("-")[1].strip().isdigit():
            if "/" in date_info:
                new_month = True
                month = date_info.split("/")[1].split(" ")[0]
                day = date_info.split("-")[1]
            else:
                month = str(start_date.month)
                day = date_info.split("-")[1]
        else:
            date_info = date_info.split("-")[1]
            new_month = True
            month = date_info.split()[0]
            day = date_info.split()[1]
    else:
        month = str(start_date.month)
        day = str(start_date.day)
    if new_month:
        formatting = "%B %d %Y"
    else:
        formatting = "%m %d %Y"
    date_string = "{} {} {}".format(month,day,year)
    date_object = datetime.datetime.strptime(date_string, formatting).date()
    if date_object:
        return date_object
    else:
        return None

def extract_event_type(meeting_info):
    if 'Conference Call' in meeting_info:
        return "Conference Call"
    elif 'Meeting' in meeting_info:
        return 'Meeting'
    else:
        return None

def extract_file_name(document_name):
    #Gets rid of the file_size in parentheses including the file extension
    file_name = re.sub("(\()([0-9]{1,3})?(\.)?([0-9]{1,3})( )(MB|KB)( )(\w{1,5})(\))",'',document_name)
    #Gets rid of the file size without parentheses while preserving the file extension
    file_name = re.sub("([0-9])?(\.)?([0-9]{1,3})( )(MB|KB)( )",'',file_name)
    file_name = ' '.join(file_name.split())
    if file_name:
        return file_name.strip()
    else:
        return None

def extract_file_size(document_name):
    re_search = re.search('([0-9])?(\.)?([0-9]{1,3})( )(MB|KB)',document_name)
    if re_search:
        return re_search.group().strip()
    else:
        return None

def extract_file_type(link,document_name):
    if type(link)== str:
        if ".pdf" in link:
            return "PDF"
        else:
            return "HTML"
    else:
        re_search = re.search('(HTML|PDF)',document_name)
        if re_search:
            return re_search.group().strip()
        else:
            return None

def extract_link(link):
    if type(link)!= str :
        return
    base = "https://www.federalreserve.gov"
    if link:
        if link[0] == "/":
            return base+link.strip()
        else:
            return link.strip()
    else:
        return None

def extract_grouping(grouping):
    file_type = re.split('[:,(]',grouping)[0]

    #Removes Year From Year-Specific groupings: Example 2008 Memos
    file_type = re.sub("\d{4} ",'',file_type)
    if file_type:
        return file_type.strip()
    else:
        return None

def extract_document_class(grouping):
    document_classes = {
        'Economic Information':[
            'Beige Book',
            'Greenbook',
            'Bluebook',
            'Redbook',
            'Tealbook'
        ],
        'Meeting Summary':[
            'Historical Minutes',
            'Intermeeting Executive Committee Minutes',
            'Minutes',
            'Record of Policy Actions',
            'Statement',
            'Minutes of Actions',
            'Memoranda of Discussion'
        ],
        'Agenda':[
            'Agenda'
        ],
        'Transcript':[
            'Transcript'
        ]
    }
    document_class = None
    for class_key in document_classes:
        if grouping in document_classes[class_key]:
            document_class = class_key
    if document_class:
        return document_class
    else:
        print("No Class Found for Grouping Type:{}".format(grouping))
        return None

def do_manual_derived_changes(documents):
    #This Event Was Missing its Greenbook and was therefore incorrectly characterized
    for document in documents:
        if document['grouping'] == "Supplement":
            document['grouping'] = "Greenbook"
            document['document_class'] = "Economic Information"
    return documents

def write_derived_csv(documents):
    with open('../output/derived_data.csv', 'w') as csvfile:
        fieldnames = ['year', 'start_date', 'end_date', 'event_type',
                        'file_name', 'file_size','file_type', 'link',
                        'grouping','document_class']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for document in documents:
            writer.writerow(document)

if __name__ == "__main__":
    main()