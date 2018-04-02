import os, re, glob, codecs, sys
import xml.etree.ElementTree as ET
import collections

def extract_sponsors(file):
    tree = ET.parse(file) 
    sponsors = dict()
    root = tree.getroot()
    for element in root.findall('.//sponsors/item'):
        sponsor = dict()
        for node in element.getiterator():
            if node.tag != 'identifiers' and node.tag != 'byRequestType' and node.tag != 'item':
                sponsor[node.tag] = node.text
        if 'bioguideId' in sponsor:
          sponsors[sponsor['bioguideId']] = sponsor 
    return sponsors 
    
output = codecs.open('corpus/sponsors.txt', 'w', 'utf-8')
sponsors = dict()
files = glob.glob('data/status/s/*.xml')
for file in files:
  sponsors.update(extract_sponsors(file))

files = glob.glob('data/status/hr/*.xml')
for file in files:
  sponsors.update(extract_sponsors(file))

for key in sorted(sponsors.keys()):
  sponsor = sponsors[key]
  if sponsor['middleName'] is None:
    sponsor['middleName'] = '' 
  full_name = sponsor['fullName']
  status = full_name.split()[0]
  value = [key, status, sponsor['fullName'], sponsor['firstName'], sponsor['lastName'], sponsor['middleName'], sponsor['state'], sponsor['party']]
  output.write('\t'.join(value) + '\n')

output.close()