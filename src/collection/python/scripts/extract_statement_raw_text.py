import os
from bs4 import BeautifulSoup
import datetime
import csv

#This prgram extracts the raw text from downloaded html statement documents
def extract_statement_raw_text():
    if not os.path.exists("../output/statement_webpages"):
        os.mkdir("../output/statement_webpages")
    if not os.path.exists("../output/statement_raw_text"):
        os.mkdir("../output/statement_raw_text")
    statement_csv_rows = []
    for file in os.listdir("../output/statement_webpages"):
        file_path = "../output/statement_webpages/{}".format(file)
        with open(file_path, 'rb') as f:
            file_soup = BeautifulSoup(f,'lxml')
            raw_text = extract_html_text(file_soup).encode('utf8')
            raw_text_path = "../output/statement_raw_text/{}".format(file.replace(".html",".txt"))
            with open(raw_text_path, "wb") as f:
                f.write(raw_text)

            file_year = file[0:4]
            statement_csv_row = {}
            statement_csv_row['meeting_start_date'] = file.split(".")[0]
            statement_csv_row['release_date'] = extract_release_date\
                (file_soup,file_year)
            statement_csv_row['file_text'] = raw_text.decode()
            statement_csv_rows.append(statement_csv_row)

    write_statement_csv(statement_csv_rows)

def extract_html_text(file_soup):
    file_text = ""
    p_tags = file_soup.find_all("p",attrs={'class':None})
    for p_tag in p_tags:
        if p_tag.text and p_tag.text.strip() and len(p_tag.contents) == 1:
            file_text = file_text + " " + p_tag.text
    return file_text

def extract_release_date(file_soup,file_year):
    date = ''
    if int(file_year)> 2005:
        date_search = file_soup.find("p",class_='article__time')
        if date_search:
            date = date_search.text
    else:
        date_search = file_soup.find("i")
        if date_search:
            date = date_search.text.split(": ")[1]
    if date:
        formatting = "%B %d, %Y"
        date_object = datetime.datetime.strptime(date, formatting).date()
        release_date = date_object
    else:
        release_date = None
    return release_date

def write_statement_csv(statements):
    with open("../output/statement_data.csv","w") as csvfile:
        fieldnames = list(statements[0].keys())
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for statement in statements:
            writer.writerow(statement)

if __name__ == "__main__":
    extract_statement_raw_text()