#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep  9 11:55:19 2017

@author: rogerduong
"""

import transform
import schema

import csv
import codecs
import os
import pprint
import re
import xml.etree.cElementTree as ET
import cerberus

OSM_PATH = "data/osm/singapore.osm"

NODES_PATH = "data/nodes.csv"
NODE_TAGS_PATH = "data/nodes_tags.csv"
WAYS_PATH = "data/ways.csv"
WAY_NODES_PATH = "data/ways_nodes.csv"
WAY_TAGS_PATH = "data/ways_tags.csv"

dataset = [OSM_PATH, NODES_PATH, NODE_TAGS_PATH, WAYS_PATH, WAY_NODES_PATH, WAY_TAGS_PATH]

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

SCHEMA = schema.schema

# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']

# ================================================== #
#               Extract Functions                  #
# ================================================== #

def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict
    
    Args:
        element:
        node_attr_fields=NODE_FIELDS
        way_attr_fields=WAY_FIELDS
        problem_chars=PROBLEMCHARS
    Returns:
        A dictionary
    
    """

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements

    # YOUR CODE HERE
    if element.tag == 'node':
        #attribs
        for key in node_attr_fields:
            node_attribs[key] = element.attrib[key]
        #tags
        for child in element:
            if child.tag == 'tag':
                child_attribs = {}
                child_attribs['id'] = node_attribs['id']
                child_attribs['value'] = child.attrib['v']
                
                #Handle problem characters and colons
                if PROBLEMCHARS.match(child.attrib['k']):
                    child_attribs['type'] = default_tag_type
                    child_attribs['key'] = ''
                elif LOWER_COLON.match(child.attrib['k']): #Split if tag contains colon
                    child_attribs['type'] = re.split(':', child.attrib['k'], maxsplit = 1)[0]
                    child_attribs['key'] = re.split(':', child.attrib['k'], maxsplit = 1)[1]
                else:
                    child_attribs['type'] = default_tag_type
                    child_attribs['key'] = child.attrib['k']
                #Add tags    
                tags.append(child_attribs)

        return {'node': node_attribs, 'node_tags': tags}
    
    elif element.tag == 'way':
        #attribs
        for key in way_attr_fields:
            way_attribs[key] = element.attrib[key]
        #tags
        for child in element:
            child_attribs = {} 
            child_attribs['id'] = way_attribs['id']
            
            if child.tag == 'tag':        
                child_attribs['value'] = child.attrib['v']

                #Handle problem characters and colons
                if PROBLEMCHARS.match(child.attrib['k']):
                    child_attribs['type'] = default_tag_type
                    child_attribs['key'] = ''
                elif LOWER_COLON.match(child.attrib['k']): #Split if tag contains colon
                    child_attribs['type'] = re.split(':', child.attrib['k'], maxsplit = 1)[0]
                    child_attribs['key'] = re.split(':', child.attrib['k'], maxsplit = 1)[1]
                else:
                    child_attribs['type'] = default_tag_type
                    child_attribs['key'] = child.attrib['k']
                #Add tags   
                tags.append(child_attribs)
                
            elif child.tag == 'nd':
                child_attribs['node_id'] = child.attrib['ref']
                child_attribs['position'] = element.getchildren().index(child)
                way_nodes.append(child_attribs)
            
            
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}

# ================================================== #
#               Extract Helper Functions             #
# ================================================== #

def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag
    
    Args:
        osm_file: OSM file
        tags: tags type to select

    Returns:
        element   
        
    """

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()

# ================================================== #
#               Transform Functions                  #
# ================================================== #

def clean_element_dict(element_dict, tag_type):
    """Retrieve street name, postal code, and house number for cleaning
    
    This function calls functions in transform.py
    
    Args:
        element_dict: element dictionary to clean
        tag_type: tag type to select
    Returns:
        element_dict: cleaned element dictionary
    
    """
    street_name = ''
    postal_code = ''
    house_number = ''
    
    for child in element_dict[tag_type]:
        if child['key'] == 'street':
            #Clean Street name in place (does not need to wait for all parameters)
            street_name = child['value']
            child['value'] = transform.clean_street_name(street_name,transform.mapping)
        elif child['key'] == 'postcode':
            postal_code = child['value'].strip()
        elif child['key'] == 'housenumber':
            house_number = child['value']
            
    #Clean postal code when all parameters are collected
    if (street_name != '') and (postal_code != '') and (house_number != ''):
        new_postal_code = transform.clean_postal_code(postal_code, house_number, street_name)        
        for child in element_dict[tag_type]:
            if child['key'] == 'postcode':
                child['value'] = new_postal_code
        
    return element_dict
    
# ================================================== #
#               Load Helper Functions                #
# ================================================== #

def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema
    
    Args:
        element: element to validate
        validator: validator (cerberus)
        schema: schema to validate against
    Returns:
        validation results
    """
    #v = validator(schema)
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)
        
        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: v for k, v in row.items()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

def summarize_dataset(dataset):
    """Return summary of dataset filesize
    
    Args:
        dataset: list of files to summarize
    Returns:
        print out of file size summary
    
    """
    for file in dataset:
        filename = re.split('/', file)[-1]
        print(filename + '\t{0:.2f} MB'.format(os.path.getsize(file)/(10**6)))
        

        
# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)
    
    Args:
        file_in: input OSM file
        validate: boolean to specify if data must be validated or not
    Returns:
        csv files
    
    """

    with codecs.open(NODES_PATH, 'w') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'w') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            elem = shape_element(element)
            if elem:                
                if validate is True:
                    validate_element(elem, validator)

                if element.tag == 'node':
                    el = clean_element_dict(elem, 'node_tags')
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    el = clean_element_dict(elem, 'way_tags')
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])

    print('Loading successful')


if __name__ == '__main__':
    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the map when validating.
    process_map(OSM_PATH, validate=False)
    summarize_dataset(dataset)