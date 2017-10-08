#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 10 12:26:51 2017

@author: rogerduong
"""
import audit

import re
from bs4 import BeautifulSoup
import requests
import time

mapping = {
    'Lor' : 'Lorong',
    'Terrance' : 'Terrace',
    'terrace' : 'Terrace',
    'St' : 'Street',
    'Upp' : 'Upper',
    'road' : 'Road',
    'Rd' : 'Road',
    ' rd' : ' Road',
    'Roadc' : 'Road',
    'Roads' : 'Road',
    'Pl' : 'Place',
    'Jln' : 'Jalan',
    'aenue' : 'Avenue',
    'Ave' : 'Avenue',
    'Avebue' : 'Avenue',
    'AveNue' : 'Avenue',
    'avenue' : 'Avenue',
    'Blvd' : 'Boulevard',
    'Dr' : 'Drive',
    'drive' : 'Drive',
    'garden' : 'Garden',
    'geylang' : 'Geylang',
    'park' : 'Park',
}

postal_code_html_page = 'http://www.singpost.com/find-postal-code'

def clean_street_name(street_name, mapping):
    """Clean street name, by replacing dictionary strings found
    in street_name in mapping"""
    
    m_end = audit.street_type_end.search(street_name)
    m_num = audit.street_type_num.search(street_name)
    street_type = ''
    if m_end:
        street_type = m_end.group()
    elif m_num:
        if len(re.split(' ', street_name)) >=2:
            street_type = re.split(' ', street_name)[-2]
        else:
            street_type = re.split(' ', street_name)[-1]
        
    if street_type in mapping.keys():
        new_street_name = street_name.replace(street_type, mapping[street_type])
        print(street_name+ ' --> ' + new_street_name)
        return(new_street_name)

def get_postal_code(html_page, house_number, street_name):
    """Get Postal Code from web page of Singapore Post"""
    
    time.sleep(5) #Delay start of scraping for 5 seconds
    
    headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'}
    data = {'building': house_number,
            'street_name': street_name}
    
    r = requests.post(html_page, data=data, headers=headers, timeout=2)

    c = r.content    
    soup = BeautifulSoup(c, "lxml")
    
    result = soup.find(id = 'datatable-1')
    
    if result is not None: #scrape through the result page to datatable-1
        for val in result.findAll('p'):
            if len(val.text) == 6:
                postal_code = val.text
        return postal_code
    else:
        return('Error')

def clean_postal_code(old_postal_code, house_number, street_name):
    """Clean postal code, by replacing old_postal_code with new name retrieved
    from Singapore Post"""
    
    if len(old_postal_code) != 6:
        if ' ' in old_postal_code: #to account for postal codes like 'Singapore 123456'
            new_postal_code = old_postal_code.replace(' ','')[-6:]
        elif len(old_postal_code) == 5: #account for leading zeros being removed
            new_postal_code = '0' + old_postal_code
        else: #get the postal code by querying the Singapore Post website
            get_result = get_postal_code(postal_code_html_page, house_number, street_name)
            if get_result != 'Error':
                new_postal_code = get_result
                print('Successfully retrieved postal code from Singpost for')
            else:
                new_postal_code = old_postal_code
                print('Error retrieving postal code from Singpost for')
        print(house_number + ' ' + street_name)
        print(old_postal_code + ' --> ' + str(new_postal_code))
        return(new_postal_code)
    else:
        return(old_postal_code)