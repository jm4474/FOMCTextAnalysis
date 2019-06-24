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
import matplotlib.pyplot as plt

import urllib, os.path, time
import os
import requests, zipfile, io
import xml.etree.ElementTree as ET
import urllib.request
import csv
import struct
import sys

import random
from selenium import webdriver
from datetime import datetime
from datetime import timedelta
import time
from bs4 import BeautifulSoup


###############################################################################
### Start Selenium
# Import the dates from the derived csv file
df_dates=pd.read_csv(directory+'/Fed_dates.csv',header=0)

path_to_chromedriver = directory+'/chromedriver' # change path as needed
browser = webdriver.Chrome(executable_path = path_to_chromedriver)
### Navigate to Factiva
url = 'http://www.columbia.edu/cgi-bin/cul/resolve?AUQ3920'
browser.get(url)
browser.implicitly_wait(30)

start=1
end=len(df_dates)
### Extract the date
for tt in range(start,end):
    print(tt)
    datestring=df_dates['date'].loc[tt]
    #date=datetime.strptime(datestring, '%m/%d/%y')+timedelta(1)
    date=datetime.strptime(datestring, '%m/%d/%y')
    # Get day of the week--make sure that it is not a Sunday
    if date.weekday()==6:
        #date=date+timedelta(1)
        date=date+timedelta(+1)
           
    day=date.day
    month=date.month
    year=date.year
    
    day_str=str(day).zfill(2)
    month_str=str(month).zfill(2)
    year_str=str(year).zfill(4)
    
    
    ### Navigate to the right window
    browser.find_element_by_id('ftx')
    browser.find_element_by_id('ftx').clear()
    browser.find_element_by_id('ftx').send_keys('(Federal Open Market Committee or FOMC ) and (rst=nytf or rst=j or rst=ftfta)')
    
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
        
    browser.find_element_by_xpath('//*[@id="btnSearchBottom"]').click()
    
    ### Extract all the relevant links
    new_list =[]
    list_links = browser.find_elements_by_tag_name('a')
    for link in list_links:
    #    print(link.get_attribute('href'))
    #    print(type(link.get_attribute('href')))
        if link.get_attribute('href') is not None:
            if "article" in link.get_attribute('href'):
                new_list.append(link)
    
    # Extract the unique elements
    def unique(list1): 
      
        # intilize a null list 
        unique_list = [] 
          
        # traverse for all elements 
        for x in list1: 
            # check if exists in unique_list or not 
            if x not in unique_list: 
                unique_list.append(x) 
        # print list 
        # for x in unique_list: 
        #    print(x )
        return unique_list
    
    link_list=unique(new_list)
    
    df= pd.DataFrame()           
    # parses website
    for i in range(len(link_list)):  
        new_list[i].click()
        time.sleep(5)
        soup=BeautifulSoup(browser.page_source, 'html.parser')
        hdextract = ''.join(filter(None, soup.find_all('div', attrs={'id': 'hd'})[0].getText().split('\n')))
        #author= soup.find_all('div', attrs={'class': 'author'})[0].getText().split('\n')[0]
        content_lis1 = soup.find_all('p',attrs={'class': 'articleParagraph enarticleParagraph'})
        
        content = []
        for li in content_lis1:
            #print(''.join(filter(None, li.getText().split('\n'))))
            content.append(' '.join(filter(None, li.getText().split('\n'))))
        parabody=' '.join(content)
        
        content={'date':datestring,'headline':[hdextract],'content':[parabody]}
        
        ## Save the list in a dataframe
        df_new=pd.DataFrame(content)
        try: 
            df_old
        except NameError:
            df_old=None        
        if df_old is None:
            df_old=df_new
        else:
            df_old=df_old.append(df_new,ignore_index = True)
        seconds = 10 + (random.random() * 5)
        time.sleep(seconds)
        #Ask Selenium to click the back button
        browser.execute_script("window.history.go(-1)") 
        print(df_old['date'])
    browser.execute_script("window.history.go(-1)") 
    seconds = 10 + (random.random() * 30)
    time.sleep(seconds)    
    
browser.quit()

df_old.to_pickle("exante")




