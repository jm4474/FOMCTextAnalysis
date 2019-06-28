#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
"""
Purpose: Logs into Factiva by using Selenium and scraps the news paper articles
@author: olivergiesecke
"""
###############################################################################
### Usual Import ###
import pandas as pd
import numpy as np

import urllib, os.path, time
import os
import requests, zipfile, io
import xml.etree.ElementTree as ET
import urllib.request
import csv
import struct
import sys

import random
import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime
from datetime import timedelta
import time
from bs4 import BeautifulSoup

def main():
    #Path to Chrome Driver
    directory = "../../../../"


    ###############################################################################
    ### Start Selenium

    #Initialize selenium chrome driver and navigate to factiva
    path_to_chromedriver = directory+'chromedriver'
    browser = webdriver.Chrome(executable_path = path_to_chromedriver)
    url = 'http://www.columbia.edu/cgi-bin/cul/resolve?AUQ3920'
    browser.get(url)
    wait_time = random.randint(15,25)
    print("Waiting for {} Seconds...".format(wait_time))
    browser.implicitly_wait(wait_time)

    #Click Through The Maintanence Window
    if browser.find_element_by_xpath("//body[@id='sys-maintenance']"):
        browser.find_element_by_id("okBtn").click()
    wait_time = 10
    print("Waiting for {} Seconds...".format(wait_time))
    browser.implicitly_wait(wait_time)

    # Import the dates from the derived csv file
    derived_df = pd.read_csv("../output/derived_data.csv")
    derived_df = derived_df[derived_df.event_type == "Meeting"]
    derived_df['end_date'] = pd.to_datetime(derived_df['end_date'])
    date_period = derived_df[(derived_df.end_date.dt.year >= 1988) & (derived_df.end_date.dt.year < 2010)]
    end_dates = list(set(date_period['end_date']))

    counter = len(end_dates)
    print("Found {} Meeting Dates".format(counter))
    all_articles = pd.DataFrame
    for end_date in end_dates:
        try:
            print("Currently Working On Meeting With End Date:{}".format(end_date))
            print("{} meetings left".format(counter))

            article_date = end_date+timedelta(+1)
            day=article_date.day
            month=article_date.month
            year=article_date.year

            day_str=str(day).zfill(2)
            month_str=str(month).zfill(2)
            year_str=str(year).zfill(4)


            ### Navigate and query the search page
            query = '(Federal Open Market Committee or FOMC ) and (rst=sfft)'
            try:
                browser.find_element_by_xpath("//textarea[@name='ftx']").send_keys(len(query) * Keys.BACKSPACE)
                browser.find_element_by_xpath("//textarea[@name='ftx']").send_keys(query)

            except NoSuchElementException:
                browser.find_element_by_xpath("//textarea[@class='ace_text-input']").send_keys(len(query) * Keys.BACKSPACE)
                browser.find_element_by_xpath("//textarea[@class='ace_text-input']").send_keys(query)
            browser.find_element_by_xpath('//*[@id="dr"]/option[contains(text(), "Enter date range...")]').click()
            browser.find_element_by_id('frd').clear()
            browser.find_element_by_id('frd').send_keys(day_str)
            browser.find_element_by_id('frm').clear()
            browser.find_element_by_id('frm').send_keys(month_str)
            browser.find_element_by_id('fry').clear()
            browser.find_element_by_id('fry').send_keys(year_str)
            browser.find_element_by_id('tod').clear()
            browser.find_element_by_id('tod').send_keys(day_str)
            browser.find_element_by_id('tom').clear()
            browser.find_element_by_id('tom').send_keys(month_str)
            browser.find_element_by_id('toy').clear()
            browser.find_element_by_id('toy').send_keys(year_str)

            wait_time = random.randint(15,25)
            print("Waiting for {} Seconds...".format(wait_time))
            time.sleep(wait_time)

            browser.find_element_by_xpath('//*[@id="btnSearchBottom"]').click()
            try:
                ### Extract all the relevant links
                article_search_results = []
                article_containers = browser.find_elements_by_xpath('//div[@class="headlines"]/table/tbody/tr[@class="headline"]')
                print("Found {} Articles".format(len(article_containers)))
                for article_container in article_containers:
                    try:
                        article_result = {}
                        article_result['link'] = article_container.find_element_by_class_name("enHeadline")
                        article_result['source'] = article_container.find_element_by_class_name("leadFields").\
                            find_element_by_tag_name("a").text
                        article_result['date'] = end_date.date()
                        article_result['headline'] = article_result['link'].text
                        article_search_results.append(article_result)
                    except:
                        print("ERROR GETTING ARTICLE RESULT INFO FOR DATE {}".format(end_date))

                # parses article
                for article in article_search_results:
                    article['link'].click()
                    try:
                        wait_time = random.randint(15, 25)
                        print("Waiting for {} Seconds...".format(wait_time))
                        time.sleep(wait_time)
                        soup=BeautifulSoup(browser.page_source, 'html.parser')
                        #print([p for p in soup.find_all("p")])
                        article_text = soup.find_all('p',attrs={'class': 'articleParagraph enarticleParagraph'})
                        #print("Article Text looks like:{}".format(article_text))
                        cleaned_lines = []
                        for p_tag in article_text:
                            cleaned_lines.append(' '.join(filter(None, p_tag.getText().split('\n'))))
                        content=' '.join(cleaned_lines)

                        #Final Article Data for Export
                        article_entry ={'meeting_date':end_date,
                                 'article_date':article_date, 'source': str(article['source']),
                                 'headline':article['headline'],'content':[content]}

                        print("FINAL ARTICLE LOOKS LIKE:{}".format(article_entry))

                        all_articles.append(article_entry,ignore_index=True)

                        print("All Articles now contains {}".format(len(all_articles)))
                        wait_time = random.randint(15,25)
                        print("Waiting for {} Seconds...".format(wait_time))
                        time.sleep(wait_time)
                        browser.execute_script("window.history.go(-1)")
                    except:
                        print("ERROR looking in article {}".format(article))
                        browser.execute_script("window.history.go(-1)")
                wait_time = random.randint(15, 25)
                print("Waiting for {} Seconds...".format(wait_time))
                time.sleep(wait_time)
                browser.execute_script("window.history.go(-1)")
            except:
                print("error for article with date {}".format(end_date))
                browser.execute_script("window.history.go(-1)")
            wait_time = random.randint(15, 25)
            print("Waiting for {} Seconds...".format(wait_time))
            time.sleep(wait_time)
            counter-=1
        except:
            print("ERROR ON SEARCH PAGE FOR DATE {}".format(end_date))
    browser.quit()
    all_articles.to_csv("../output/ft_articles.csv")


main()