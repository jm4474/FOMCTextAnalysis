import os
import pandas as pd
import requests

'''
@author Anand Chitale
This file reads in the derived data file to download all transcript webpage html files
into the output folder transcript webpages
'''
def download_transcript():
    data_file_name = "../output/derived_data.csv"
    start_year = 1965
    end_year = 2015
    df = pd.read_csv(data_file_name)
    files = []
    for index, row in df.iterrows():
        if row['grouping'] == "Transcript" and \
                row['link'] and int(row['year']) \
                in range(start_year, end_year + 1):
            files.append({
                'link': row['link'],
                'start_date': row['start_date'],
                'end_date': row['end_date'],
                'year': row['year']
            })
    documents = []
    if not os.path.exists("../output/transcript_pdfs"):
        os.mkdir("../output/transcript_pdfs")
    for file in files:
        document = download_html(file)
        documents.append(document)

def download_html(file):
    with open("../output/transcript_data.csv","wb") as f:
        file_path = "../output/transcript_pdfs/{}.pdf".format(file['end_date'])
        if not os.path.exists(file_path):
            r = requests.get(file['link'])
            with open(file_path, 'wb') as f:
                f.write(r.content)

if __name__ == "__main__":
    download_transcript()