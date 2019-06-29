import pandas as pd
from datetime import timedelta
import requests
from bs4 import BeautifulSoup
import csv
import time
broken_links = 0
'''
@Author Anand Chitale
This program scrapes the new york times
'''
def main():
    derived_df=pd.read_csv("../output/derived_data.csv")
    derived_df = derived_df[derived_df.event_type=="Meeting"]
    derived_df['end_date'] = pd.to_datetime(derived_df['end_date'])
    date_period = derived_df[(derived_df.end_date.dt.year>=1988)\
                             &(derived_df.end_date.dt.year<=2009)]
    end_dates = list(set(date_period['end_date']))
    all_articles = []
    counter = len(end_dates)
    for date in end_dates:
        print(str(counter)+" dates remaining")
        all_articles += get_articles(date)
        counter-=1
    write_nytimes_csv(all_articles)
    print(broken_links)
def get_articles(date):
    date_articles = []
    base_query = \
            "https://www.nytimes.com/search?endDate=END_DATE&query=federal%20open%20market%20committee&sort=best&startDate=START_DATE"
    meeting_date = date.to_pydatetime()
    article_date = meeting_date + timedelta(days=1)
    query_date = article_date.strftime("%Y%m%d")
    print("currently searching articles for date {}".format(query_date))
    query = base_query.replace("END_DATE",query_date).replace("START_DATE",query_date)
    query_request = requests.get(query)
    if query_request.status_code != 200:
        print("error in search request for date {}".format(query_date))
        return date_articles
    print("Date Search link is {}".format(query))
    soup = BeautifulSoup(query_request.content,'lxml')
    results = soup.find("ol",attrs={'data-testid':'search-results'})
    if results:
        print("found {} articles".format(len(results.find_all("li"))))
        for result in results.find_all("li"):
            article_a_tag = result.find("a")
            if not article_a_tag:
                print("entry had no article search result")
                continue
            article_link = article_a_tag.get("href")
            if article_link.startswith("/"):
                article_link = "http://www.nytimes.com"+article_link
            article_request = requests.get(article_link)
            if article_request.status_code!=200:
                print("ARTICLE PAGE FAILED. link is:{}".format(article_link))
                global broken_links
                broken_links += 1
                return date_articles
            article = {}
            article['meeting_date'] = meeting_date
            article['article_date'] = article_date
            article_soup = BeautifulSoup(article_request.content,'lxml')
            for script in soup(["script","style"]):
                script.decompose()
            article_info = get_article_info(article_soup)
            headline = article_info['headline']
            content = article_info['content']
            if not content:
                print("could not find content for article with link {}".format(article_link))
            article['headline'] = headline
            article['content'] = content
            article['link'] = article_link
            print("succesfuly added article")
            date_articles.append(article)
    else:
        print("Found no articles for date {}".format(query_date))
    return date_articles

def get_article_info(file_soup):
    headline = ''
    headline_search = file_soup.find("h1",itemprop="headline")
    if headline_search:
        headline = headline_search.get_text()
    content_containers = ['entry-content','story-body-supplemental']
    content = ""
    for potential_container in content_containers:
        content_search = file_soup.find("div",class_=potential_container)
        if content_search:
            raw_text = content_search.get_text()
            raw_lines = raw_text.splitlines()
            cleaned_lines = [line for line in raw_lines if line.strip()]
            content = "\n".join(cleaned_lines)
            break
    article_info = {
        'headline': headline,
        'content': content
    }
    return article_info
def write_nytimes_csv(documents):
    with open('../output/nytimes_articles.csv', 'w') as csvfile:
        fieldnames = documents[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for document in documents:
            writer.writerow(document)
main()