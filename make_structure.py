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
    global CORRECTIONS
    with open(CORRECTIONS_FILE, 'r') as fp:
        reader = csv.reader(fp)
        CORRECTIONS = {row[0]:row[1] for row in reader}
    mapping = {}
    missing = []
    for semester in [sp17dh]:
        temp_mapping, temp_missing = semester()
        mapping.update(temp_mapping)
        missing.extend(temp_missing)
    #print(mapping)
    [print(x) for x in missing]
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

def map_links(parent_file, parent_file_path, files, as_folders=False):
    mapping = {}
    missing = []
    for title, filename in files:
        if not os.path.exists(FOLDER_PREFIX + filename):
            if filename in CORRECTIONS.keys():
                filename = CORRECTIONS[filename]
            else:
                missing.append((parent_file, filename))
                continue   # don't add to mapping

        if as_folders:
            mapping[filename] = f'{parent_file_path}/{title}/index.html'
        else:
            mapping[filename] = f'{parent_file_path}/{title}.html'
    return mapping, missing

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

    fieldnotes_mapping, fieldnotes_missing = map_links(fieldnotes_file, f'{semester_name}/{FIELDNOTES_FOLDER_NAME}', fieldnotes, as_folders=True)
    profiles_mapping, profiles_missing = map_links(profiles_file, f'{semester_name}/{PROFILES_FOLDER_NAME}', profiles, as_folders=false)

    mapping.update(fieldnotes_mapping)
    mapping.update(profiles_mapping)
    missing.extend(fieldnotes_missing)
    missing.extend(profiles_missing)

    for student_file, new_path in fieldnotes_mapping.items():
        student_notes = get_all_links_from_file(FOLDER_PREFIX + student_file)
        student_notes_mapping, student_notes_missing = map_links(student_file, new_path.rsplit('/index.html')[0], student_notes, as_folders=False)

        mapping.update(student_notes_mapping)
        missing.extend(student_notes_missing)

    return mapping, missing

def sp17dh():
    mapping = {}
    missing = []
    semester_name = 'sp17dh'

    filename = unquote('Spring%202017%20Digital%20Archive.html')
    mapping[filename] = f'{semester_name}/index.html'

    soup = BeautifulSoup(get_html_from_file(FOLDER_PREFIX + filename), 'html.parser')

    fieldnotes_file = CORRECTIONS[unquote(soup.find(string=re.compile('Field Notes')).parent['href'])]
    mapping[fieldnotes_file] = f'{semester_name}/{FIELDNOTES_FOLDER_NAME}/index.html'

    # Course page
    course_link = soup.find(string=re.compile('HIST GR8975')).parent
    course_title = sanitize(course_link.string)
    course_file = unquote(course_link['href'])
    mapping[course_file] = f'{semester_name}/{course_title}.html'

    # field notes, including TA field notes and example DH
    # TODO: confirm folder structure for TA field notes and example DH
    fieldnotes = get_all_links_from_file(FOLDER_PREFIX + fieldnotes_file)
    fieldnotes_mapping, fieldnotes_missing = map_links(fieldnotes_file, f'{semester_name}/{FIELDNOTES_FOLDER_NAME}', fieldnotes, as_folders=True)

    mapping.update(fieldnotes_mapping)
    missing.extend(fieldnotes_missing)

    for student_file, new_path in fieldnotes_mapping.items():
        student_notes = get_all_links_from_file(FOLDER_PREFIX + student_file)
        student_notes_mapping, student_notes_missing = map_links(student_file, new_path.rsplit('/index.html')[0], student_notes, as_folders=False)

        mapping.update(student_notes_mapping)
        missing.extend(student_notes_missing)

    return mapping, missing

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
