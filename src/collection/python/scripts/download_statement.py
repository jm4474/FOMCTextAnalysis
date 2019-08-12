import os
import pandas as pd
import requests

'''
@author Anand Chitale
This file reads in the derived data file to download all statement webpage html files
into the output folder statement webpages
'''
def download_statement():
    data_file_name = "../output/derived_data.csv"
    start_year = 1965
    end_year = 2013
    df = pd.read_csv(data_file_name)
    files = []
    for index, row in df.iterrows():
        if row['grouping'] == "Statement" and \
                row['link'] and int(row['year']) \
                in range(start_year, end_year + 1):
            files.append({
                'link': row['link'],
                'start_date': row['start_date'],
                'end_date': row['end_date'],
                'year': row['year']
            })
    documents = []
    if not os.path.exists("../output/statement_webpages"):
        os.mkdir("../output/statement_webpages")
    for file in files:
        document = download_html(file)
        documents.append(document)

def download_html(file):
    with open("../output/statement_data.csv","wb") as f:
        file_path = "../output/statement_webpages/{}.html".format(file['end_date'])
        if not os.path.exists(file_path):
            r = requests.get(file['link'])
            with open(file_path, 'wb') as f:
                f.write(r.content)

if __name__ == "__main__":
    download_statement()