#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep  9 11:55:19 2017

@author: rogerduong
"""

import xml.etree.cElementTree as ET
import re
from collections import defaultdict

OSM_FILE = 'data/osm/singapore.osm'

"""
Regular expressions that look for street types. Note that in Singapore,
street names can contain numbers like 'Ang Mo Kio Avenue 3'
street_type_num looks for such strings.
"""
street_type_end = re.compile(r'([a-z]+)$', re.IGNORECASE)
street_type_num = re.compile(r'([0-9]+)$', re.IGNORECASE)

street_types = defaultdict(int)
postal_codes_problem = defaultdict(int)

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\/&<>;\'"\?%$@\,\. \t\r\n]')
postal_code_correct = re.compile(r'^[0-9]{6}$')

def count_tags(filename):
    """Count the tags and return a dictionary with the tags
    
    Args:
        filename: OSM filename
        
    Returns:
        tags_dict: a dictionary counting the tags       
    """
    tags_dict = defaultdict(int)
    for tag_elem in ET.iterparse(filename):
        tags_dict[tag_elem[1].tag] += 1
    print(tags_dict)
    return tags_dict

def key_type(element, keys):
    """Populate the dictionary 'keys' with element values with
    suspected problems
    
    Args:
        element: element to audit
        keys: dictionary of audit summary
    Returns:
        keys: dictionary of audit summary
    """
    if element.tag == "tag":
        value = element.get('v')
        if lower.match(value):
            keys['lower'] += 1
        elif lower_colon.match(value):
            keys['lower_colon'] += 1
        elif problemchars.match(value):
            keys['problemchars'] += 1
        else:
            keys['other'] += 1
    return keys

def audit_street_type(street_types, street_name):
    """Add the street_type in to the dictionary street_types
    
    Args:
        street_types: dictionary of street types
        street_name: string of street name to audit
    Returns:
        street_types: dictionary of street types
    """
    m_end = street_type_end.search(street_name)
    m_num = street_type_num.search(street_name)

    if m_end:
        street_type = m_end.group()
        street_types[street_type] += 1
    if m_num:
        if len(re.split(' ', street_name)) >=2:
            street_type = re.split(' ', street_name)[-2]
            street_types[street_type] += 1
        else:
            street_type = re.split(' ', street_name)[-1]
            street_types[street_type] += 1

def audit_postal_code(postal_codes_problem, postal_code):
    """Add the incorrect postal codes to the dictionary postal_codes_problem
    
    Note that in Singapore, postal codes have 6 digits, and are unique to
    each building
    
    Args:
        postal_codes_problem: dictionary of postal codes with problems
        postal_code: string of postal code to audit
    Returns:
        postal_codes_problem: dictionary of postal codes with problems
    """
    if postal_code_correct.match(postal_code) is None:
        postal_codes_problem[postal_code] += 1

def print_sorted_dict(d):
    keys = d.keys()
    keys = sorted(keys, key=lambda s: s.lower())
    for k in keys:
        v = d[k]
        print("%s: %d" % (k, v))

def is_street_name(elem):
    return (elem.tag == "tag") and (elem.attrib['k'] == "addr:street")

def is_postal_code(elem):
    return (elem.tag == "tag") and (elem.attrib['k'] == "addr:postcode")

def audit(osm_file):
    """Audit function (main function). Print sorted dictionaries
    for street names and postal codes
    
    Args:
        osm_file: OSM file to audit
    Returns:
        print out of audit dictionary results:
            count_tags
            street_types
            postal_codes_problem
    """
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    
    for event, elem in ET.iterparse(osm_file):
        keys = key_type(elem, keys)
        if is_street_name(elem):
            audit_street_type(street_types, elem.attrib['v'])
        if is_postal_code(elem):
            audit_postal_code(postal_codes_problem, elem.attrib['v'])
    print('--- Tag count ---')
    count_tags(osm_file)
    print('--- Street Types ---')
    print_sorted_dict(street_types)
    print('--- Incorrect Postal Codes ---')
    print_sorted_dict(postal_codes_problem)
    print('--- Keys with suspected problems ---')
    print(keys)
