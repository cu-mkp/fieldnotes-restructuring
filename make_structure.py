#!/bin/python3
import os
#import sys
import re
#import urllib.request
#import urllib.error
from urllib.parse import unquote
import csv
#import unicodedata

from bs4 import BeautifulSoup

def main():
    with open(CORRECTIONS_FILE, 'r') as fp:
        reader = csv.reader(fp)
        CORRECTIONS = {row[0]:row[1] for row in reader}
    mapping = {}
    missing = []
    for semester in [sp17]:
        temp_mapping, temp_missing = semester()
        mapping.update(temp_mapping)
        missing.extend(temp_missing)
    #print(mapping)
    #print(missing)
    #print(CORRECTIONS)

    with open('mapping.csv', 'w') as fp:
        writer = csv.writer(fp)
        writer.writerow(['old', 'new'])
        for old, new in mapping.items():
            writer.writerow([old, new])

    with open('missing.csv', 'w') as fp:
        writer = csv.writer(fp)
        writer.writerow(['parent', 'file'])
        writer.writerows(missing)

#URL_PREFIX = 'http://fieldnotes.makingandknowing.org/mainSpace/'
FOLDER_PREFIX = '/mnt/c/code/misc/mkp/fieldnotes/mainSpace/'

#mainspace_url = URL_PREFIX + 'space.menu.html'
#mainspace_doc = get_html(mainspace_url)

# What to call the folders for profiles and fieldnotes within each semester in the structure
PROFILES_FOLDER_NAME = 'profiles'
FIELDNOTES_FOLDER_NAME = 'fieldnotes'

CORRECTIONS_FILE = 'corrections.csv'
CORRECTIONS = {}

#def get_html_from_url(url): return urllib.request.urlopen(url).read().decode('utf-8')
def get_html_from_file(filename):
    with open(filename, 'r') as fp:
        doc = fp.read()
    return doc

#def get_all_links_from_url(url):
#    soup = BeautifulSoup(get_html_from_url(url), 'html.parser')
#    links = [(sanitize(e.string), URL_PREFIX + e['href']) for e in soup.find_all(lambda t: t.name=='a' and t.has_attr('href'))]
#    return links

def get_all_links_from_file(filename):
    soup = BeautifulSoup(get_html_from_file(filename), 'html.parser')
    links = [(sanitize(e.string), unquote(e['href'])) for e in soup.find_all(lambda t: t.name=='a' and t.has_attr('href'))]
    return links

def sanitize(string):
    replacements = { ' ' : '-',
                     '/' : '-',
                     ':' : '-',
                     '.' : '-' }
    table = string.maketrans(replacements)
    return string.translate(table).lower()

def sp17():
    mapping = {}
    missing = []
    semester_name = 'sp17'

    filename = unquote('Spring%202017%20Archive.html')
    mapping[filename] = f'{semester_name}/index.html'

    soup = BeautifulSoup(get_html_from_file(FOLDER_PREFIX + filename), 'html.parser')

    fieldnotes_file = unquote(soup.find(string=re.compile('Field Notes')).parent['href'])
    profiles_file = unquote(soup.find(string=re.compile('Student')).parent['href'])
    mapping[fieldnotes_file] = f'{semester_name}/{FIELDNOTES_FOLDER_NAME}/index.html'
    mapping[profiles_file] = f'{semester_name}/{PROFILES_FOLDER_NAME}/index.html'

    fieldnotes = get_all_links_from_file(FOLDER_PREFIX + fieldnotes_file)
    profiles = get_all_links_from_file(FOLDER_PREFIX + profiles_file)

    for student, student_file in fieldnotes:
        if not os.path.exists(FOLDER_PREFIX + student_file):
            if student_file in CORRECTIONS.keys():
                student_file = CORRECTIONS[student_file]
            else:
                missing.append((fieldnotes_file, student_file))
                continue   # don't add to mapping

        mapping[student_file] = f'{semester_name}/{FIELDNOTES_FOLDER_NAME}/{student}/index.html'
        pages = get_all_links_from_file(FOLDER_PREFIX + student_file)
        for title, note_file in pages:
            mapping[note_file] = f'{semester_name}/{FIELDNOTES_FOLDER_NAME}/{student}/{title}.html'

    for student, student_file in profiles:
        if not os.path.exists(FOLDER_PREFIX + student_file):
            if student_file in CORRECTIONS.keys():
                student_file = CORRECTIONS[student_file]
            else:
                missing.append((profiles_file, student_file))
                continue   # don't add to mapping

        mapping[student_file] = f'{semester_name}/{PROFILES_FOLDER_NAME}/{student}.html'

    return mapping, missing

def sp17dh():
    semester_name = 'sp17dh'
    url = 'http://fieldnotes.makingandknowing.org/mainSpace/Spring%202017%20Digital%20Archive.html'
    soup = BeautifulSoup(get_html(url), 'html.parser')

def fa16():
    url = 'http://fieldnotes.makingandknowing.org/mainSpace/Fall%202016%20Archive.html'
    soup = BeautifulSoup(get_html(url), 'html.parser')

def sp16():
    url = 'http://fieldnotes.makingandknowing.org/mainSpace/Spring%202016%20archive.html'
    soup = BeautifulSoup(get_html(url), 'html.parser')

def fa15():
    url = 'http://fieldnotes.makingandknowing.org/mainSpace/Fall%202015.html'
    soup = BeautifulSoup(get_html(url), 'html.parser')

def sp15():
    url = 'http://fieldnotes.makingandknowing.org/mainSpace/Spring%202015.html'
    soup = BeautifulSoup(get_html(url), 'html.parser')

def fa14():
    url = 'http://fieldnotes.makingandknowing.org/mainSpace/Fall%202014%20Archives.html'
    soup = BeautifulSoup(get_html(url), 'html.parser')

if __name__ == '__main__':
    main()
