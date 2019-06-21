import pandas as pd
import requests
import os

#This file reads in the derived data file in order to download all bluebook
#pdfs

def main():
    data_file_name = "../output/derived_data.csv"
    start_year = 1965
    end_year = 2013
    df = pd.read_csv(data_file_name)
    files = []
    for index, row in df.iterrows():
        if row['grouping'] == "Bluebook" and \
                row['link'] and int(row['year']) \
                in range(start_year, end_year + 1):
            files.append({
                    'link': row['link'],
                    'start_date': row['start_date'],
                    'end_date': row['end_date'],
                    'year': row['year']
            })
    documents = []
    if not os.path.exists("../output/bluebook_pdfs"):
        os.mkdir("../output/bluebook_pdfs")
    for file in files:
        document = download_pdf(file)
        documents.append(document)

def download_pdf(file):
    file_path = "../output/bluebook_pdfs/{}.pdf".format(file['start_date'])
    if not os.path.exists(file_path):
        r = requests.get(file['link'])
        with open(file_path, 'wb') as f:
            f.write(r.content)

if __name__ == "__main__":
    main()