import os
import pandas as pd
import requests
from tika import parser
from tika import initVM
def main():
    initVM()
    if not os.path.isdir("../output/raw_bluebook"):
        os.mkdir("../output/raw_bluebook")
    data_file_name = "../output/derived_data.csv"
    grouping = "Bluebook"
    start_year = 1965
    end_year = 2013
    df = pd.read_csv(data_file_name)
    files = []
    for index, row in df.iterrows():
        if row['grouping'] == grouping and \
                row['link'] and int(row['year']) in range(start_year, end_year + 1):
            files.append({'link': row['link'],
                          'start_date': row['start_date']
                          }
                         )
    for file in files:
        if not os.path.exists("../output/Bluebook/" + file['start_date']):
            r = requests.get(file['link'])
            open("../output/Bluebook/" + file['start_date'], 'wb').write(r.content)
        if not os.path.exists("../output/raw_bluebook/"+file['start_date']):
            parsed = parser.from_file("../output/Bluebook/"+file['start_date'])
            file_text = parsed['content']
            open("../output/raw_bluebook/"+file['start_date']+".txt","w").write(file_text)
        else:
            pass

main()