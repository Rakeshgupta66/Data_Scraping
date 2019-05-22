
# -*- coding: utf-8 -*-
"""
Created on Sun May 19 02:23:13 2019

@author: Rakesh Gupta
"""
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
import re;
import numpy as np;
import pandas as pd;

# Set the name of nurse to be searched here
nurseNamePattern = "Zach"

class URLScraper(object):
    
    def __init__(self, name_pattern):
        self.initial_url = 'https://www.ark.org/arsbn/statuswatch/index.php/nurse/search'
        self.further_page_base_url = "https://www.ark.org/arsbn/statuswatch/index.php/nurse/search/sort/name/direction/asc/start"
        self.url_list = []
        self.payload = {'name': name_pattern}
        self.result_data_frame = pd.DataFrame(columns=["License_Number", "Name",
                                         "Expiration_Date", "License_Status", "License_Type"])

    """ This method takes all the url of the nurse and store in url_list
    """
    def scrape_url(self, url, pagination_check):
        req = requests.post(url, data=self.payload)
        htmlObject = BeautifulSoup(req.text, 'html.parser')
        table = htmlObject.find_all(class_='data_table')

        #  This will take all the nurse link and store in url_list 
        if len(table) > 0:
            for a in table[0].find_all('tr', class_=["even", "odd"]):
                for j in a.find_all('a'):
                    self.url_list.append(j['href'])

        # If block would only be executed once. 
        # In future calls pagination_check is set to False
        # This code checks how many pages are there in the resultset when the name is searched
        if pagination_check:
            table_pagination = htmlObject.find_all(class_='pagination')

            if len(table_pagination) == 1:
                totalpaginationlength = int(str(table_pagination[0].find_all('center')[0]).split('of')[1].split('<')[0])    
                for i in range(1, int(totalpaginationlength / 20) + 1):
                    page_number = i * 20
                    url = self.further_page_base_url
                    url = url + "/" + str(page_number) + "/"
                    self.scrape_url(url, False)
    
    """This method will fetch all the details of the nurse and store in result_data_frame
    """                
    def construct_result(self):
        for each_url in self.url_list:
            req = requests.get(each_url)
            html_object = BeautifulSoup(req.text, 'html.parser')
            first_license_detail = html_object.find_all(class_='license_table box form')[0]
            license_number = first_license_detail.find_all('h2')[0].text
            name = html_object.find_all(class_='box_content')[0].find_all('td')[0].find('div').text
            expiration_date = first_license_detail.find("td", text="Expiration Date:").find_parent().find_all('td')[1].text
            licese_status = first_license_detail.find("td", text="License Status:").find_parent().find_all('td')[1].text
            licese_type = first_license_detail.find("td", text="License Type:").find_parent().find_all('td')[1].text

            nurse_data_frame = pd.DataFrame([[license_number, name, expiration_date, licese_status, licese_type]], columns=["License_Number", "Name",
                                                 "Expiration_Date", "License_Status", "License_Type"])
            
            self.result_data_frame = pd.concat([self.result_data_frame, nurse_data_frame])
        self.result_data_frame.reset_index(inplace=True, drop=True)

    """This method will write the all the details of the nurse in the CSV file
    """
    def store_output(self):
        self.result_data_frame.to_csv("Lexis_Nexis_Data_Scrapping.csv")
        
    """This method will call various methods above in a sequence
    """
    def scrape(self):
        self.scrape_url(self.initial_url, True)
        self.construct_result()
        self.store_output()


url_scraper = URLScraper(nurseNamePattern)
url_scraper.scrape()
