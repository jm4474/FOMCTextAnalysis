import pandas as pd
import re
import csv
import datetime
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

        cur_document['year'] = year.strip()
        cur_document['event_type'] = extract_event_type(meeting_info).strip()
        cur_document['file_name'] = extract_file_name(document_name).strip()
        cur_document['file_type'] = extract_file_type(link,document_name).strip()
        cur_document['file_size'] = extract_file_size(document_name).strip()
        cur_document['link'] = extract_link(link).strip()
        cur_document['grouping'] = extract_grouping(grouping).strip()

        date_info = meeting_info.split(cur_document['event_type'])[0].strip()
        if "," in date_info:
            date_info = date_info.split(",")[0] + "-" + date_info.split("and ")[1]
        start_date = extract_start_date(date_info, year)
        end_date = extract_end_date(date_info, start_date, year)
        cur_document['start_date'] = start_date
        cur_document['end_date'] = end_date

        documents.append(cur_document)
    write_derived_csv(documents)

def extract_start_date(date_info,year):
    start_date = {}
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
    return date_object

def extract_end_date(date_info,start_date,year):
    new_month = False
    if "-" in date_info:
        if date_info.split("-")[1].isdigit():
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
    return date_object

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
    return file_name

def extract_file_size(document_name):
    re_search = re.search('([0-9])?(\.)?([0-9]{1,3})( )(MB|KB)',document_name)
    if re_search:
        return re_search.group()
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
            return re_search.group()
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

def extract_grouping(grouping):
    file_type = re.split('[:,(]',grouping)[0]

    #Removes Year From Year-Specific groupings: Example 2008 Memos
    file_type = re.sub("\d{4} ",'',file_type)
    return file_type

def write_derived_csv(documents):
    with open('../output/derived_data.csv', 'w') as csvfile:
        fieldnames = ['year', 'start_date', 'end_date', 'event_type',
                        'file_name', 'file_size','file_type', 'link', 'grouping']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for document in documents:
            writer.writerow(document)

main()