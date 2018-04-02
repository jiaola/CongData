# Usage: python scripts/extract_text.py s|hr year
# Output: A tablular file. Each line is in this format: id[tab]comma-dilimited-sponsors[tab]bill-text

import os, re, glob, codecs, sys
import xml.etree.ElementTree as ET
import collections

bill_type, year = sys.argv[1].split('-')

def extract_text(file):
    tree = ET.parse(file)
    root = tree.getroot()
    namespaces = {'dc': 'http://purl.org/dc/elements/1.1/'}
    title = root.find('.//form/official-title').text
    return title + ' ' + ' '.join(root.find('.//legis-body').itertext())

def extract_summary(file):
    tree = ET.parse(file)
    root = tree.getroot()
    title = root.find('.//title').text    
    summary = title + ' ' + ' '.join(root.find('.//summary/summary-text').itertext())
    summary = summary.replace('\n', ' ').replace('\r', ' ')
    cleanr = re.compile('<.*?>')
    summary = re.sub(cleanr, ' ', summary)
    summary = re.sub('\s+', ' ', summary).strip()
    return summary

def identifier(filename):
    match = re.search('.*-(\d+(?:s|hr)\d+).*', filename)
    return match.group(1)

def extract_sponsor_ids(file):
    tree = ET.parse(file)
    sponsors = []
    root = tree.getroot()
    sponsors = [n.text for n in root.findall('.//sponsors/item/bioguideId')]
    sponsors.extend([n.text for n in root.findall(".//cosponsors/item/bioguideId")])
    return sponsors 

files = glob.glob(f'data/bills/{bill_type}/BILLS-{year}*.xml')
bills = collections.OrderedDict()

sponsors = dict()
status_files = glob.glob(f'data/status/{bill_type}/BILLSTATUS-{year}*.xml')
for file in status_files:
    sponsor_ids = extract_sponsor_ids(file)
    id = identifier(file)
    sponsors[id] = sponsor_ids

for file in files:
    id = identifier(file)
    try:
        txt = extract_text(file)
    except:
        print("Error parsing: " + file)
        continue  
    if id in bills:
        if len(txt) > len(bills[id]):
            bills[id] = txt
    else:
        bills[id] = txt

output = codecs.open(f'corpus/{bill_type}-{year}.txt', 'w', 'utf-8')
for id, txt in bills.items():
    txt = txt.replace('\n', ' ').replace('\r', ' ')
    txt = re.sub('\s+', ' ', txt).strip()   
    if id in sponsors:
        if len(txt) > 100000:
            if os.path.isfile(f'data/summary/{bill_type}/BILLSUM-{id}.xml'):
                summary = extract_summary(f'data/summary/{bill_type}/BILLSUM-{id}.xml')
                output.write(id + "\t" + ",".join(sponsors[id]) + "\t" + summary + "\n")
            else:
                print("Can't find summary for: " + id)
        else:
            output.write(id + "\t" + ",".join(sponsors[id]) + "\t" + txt + "\n")
    else:
        print("No sponsors found for id: " + id)

output.close()
