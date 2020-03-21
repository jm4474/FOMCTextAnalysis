import pandas as pd
import requests
import os
from bs4 import BeautifulSoup
import re

def download(ftype):
    data_file_name = "../output/derived_data.csv"
    start_year = 1965
    end_year = 2019
    df = pd.read_csv(data_file_name)
    files = []
    for index, row in df.iterrows():
        if (row['grouping'].lower() == ftype or (ftype=='minutes' and ftype in row['grouping'].lower()) or (ftype=='transcript' and row['grouping'].lower() == ftype == row['file_name'].lower()))  and \
                row['link'] and int(row['year']) \
                in range(start_year, end_year + 1):
            files.append({
                    'link': row['link'],
                    'start_date': row['start_date'],
                    'end_date': row['end_date'],
                    'year': row['year']
            })
    documents = []
    if ftype=="press conference":
        for idx, f in enumerate(files):
            #print(files[idx]['link'])
            files[idx]['link'] = "https://www.federalreserve.gov/mediacenter/files/{}.pdf".format(files[idx]['link'].split(".")[-2].split("/")[-1])
            print(files[idx]['link'])
    if not os.path.exists("../data/{}_pdfs".format(ftype)):
        os.mkdir("../data/{}_pdfs".format(ftype))
    for fidx, file in enumerate(files):
        if type(file['link'])==str:
            if file['link'].endswith("pdf"):
                document = download_pdf(ftype, file)
            elif file['link'].endswith("htm"):
                document = download_html(ftype, file)
            else:
                print('unsupported file ending {}'.format(file['link']))
            documents.append(document)
        
        
def download_html(ftype, file):
    file_path = "../data/{}_pdfs/{}.txt".format(ftype,file['end_date'])
    if not os.path.exists(file_path):
        print("{}".format(file_path))
        r = requests.get(file['link'])
        file_soup = BeautifulSoup(r.content,'lxml')
        r_text = extract_html_text(file_soup)
        with open(file_path, 'w') as f:
            f.write(r_text)
    else:
        print("{} -- exists".format(file_path))
            
            
def extract_html_text(file_soup):
    article_text = file_soup.find("div",id="article")

    # kill all script and style elements
    for script in file_soup(["script", "style"]):
        script.extract()  # rip it out

    if article_text:
        text = article_text.get_text()
    else:
        text = file_soup.get_text()
    lines = text.split("\n")
    cleaned = [line.strip() for line in lines if line.strip()]
    return "\n".join(cleaned)


def download_post_2013(ftype):
    # downloads docs 2014--2019 (others via standard download("press conference"))
    base_url = "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm"
    r = requests.get(base_url)
    file_soup = BeautifulSoup(r.content,'lxml')
    if ftype.lower()=="press conference":
        links = re.findall(r".+href=\"([^\"]+).htm\">Press Conference</a><br/>", str(file_soup))
    elif ftype.lower()=="minutes":
        links = re.findall(r".+href=\"([^\"]+minutes[^\"]+).pdf\">PDF</a>", str(file_soup))
    elif ftype.lower()=="statement":
        links = re.findall(r".+href=\"([^\"]+.htm)\">Statement</a><br/>", str(file_soup))
        links.extend(re.findall(r".+href=\"([^\"]+a1).pdf\">PDF</a>", str(file_soup)))
    for ll in links:
        print(ll)
        date = "{}-{}-{}".format(ll[-8:-4], ll[-4:-2], ll[-2:])
        if ll.endswith("htm"):
            print("htm!!!!!")
            date = "{}-{}-{}".format(ll.split(".")[-2][-9:-5], 
                                     ll.split(".")[-2][-5:-3], 
                                     ll.split(".")[-2][-3:-1])
            r= requests.get("https://www.federalreserve.gov{}".format(ll))
            print(r,"https://www.federalreserve.gov{}".format(ll))
            file_soup = BeautifulSoup(r.content,'lxml')
            r_text = extract_html_text(file_soup)
            with open("../data/{}_pdfs/{}.txt".format(ftype, date), "w+") as f:
                f.write(r_text)
        else:
            if ll.endswith("a1"):
                date = "{}-{}-{}".format(ll[-10:-6], ll[-6:-4], ll[-4:-2])
            r= requests.get("https://www.federalreserve.gov{}.pdf".format(ll))
            print("https://www.federalreserve.gov{}.pdf".format(ll))
            with open("../data/{}_pdfs/{}.pdf".format(ftype, date), "wb+") as f:
                f.write(r.content)

        
def download_pdf(ftype, file):
    file_path = "../data/{}_pdfs/{}.pdf".format(ftype,file['start_date'])
    if not os.path.exists(file_path):
        print("{}".format(file_path))
        r = requests.get(file['link'])
        with open(file_path, 'wb') as f:
            f.write(r.content)
    else:
        print("{} -- exists".format(file_path))

if __name__ == "__main__":
    download("minutes")
    download_post_2013("minutes")
