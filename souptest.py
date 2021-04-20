import os
import sys
import re
import urllib.request
import urllib.error
import urllib.parse
import csv
import unicodedata

from bs4 import BeautifulSoup

def get_html(url): return urllib.request.urlopen(url).read().decode('utf-8')

def main():
    spring_2017()

URL_PREFIX = 'http://fieldnotes.makingandknowing.org/mainSpace/'

mainspace_url = 'http://fieldnotes.makingandknowing.org/mainSpace/space.menu.html'
#mainspace_doc = get_html(mainspace_url)

# What to call the folders for profiles and fieldnotes within each semester in the structure
PROFILES_FOLDER_NAME = 'profiles'
FIELDNOTES_FOLDER_NAME = 'fieldnotes'

def get_all_links(url):
    soup = BeautifulSoup(get_html(url), 'html.parser')
    links = [(sanitize(e.string), URL_PREFIX + e['href']) for e in soup.find_all(lambda t: t.name=='a' and t.has_attr('href'))]
    return links

def sanitize(string):
    replacements = { ' ' : '-',
                     '/' : '-',
                     ':' : '-',
                     '.' : '-' }
    table = string.maketrans(replacements)
    return string.translate(table).lower()

def spring_2017():
    semester_name = 'Spring 2017'
    table = {}

    url = 'http://fieldnotes.makingandknowing.org/mainSpace/Spring%202017%20Archive.html'
    table[url] = f'{semester_name}/index.html'

    soup = BeautifulSoup(get_html(url), 'html.parser')

    fieldnotes_url = URL_PREFIX + soup.find(string=re.compile('Field Notes')).parent['href']
    profiles_url = URL_PREFIX + soup.find(string=re.compile('Student')).parent['href']
    table[fieldnotes_url] = f'{semester_name}/{FIELDNOTES_FOLDER_NAME}/index.html'
    table[profiles_url] = f'{semester_name}/{PROFILES_FOLDER_NAME}/index.html'

    fieldnotes = get_all_links(fieldnotes_url)
    profiles = get_all_links(profiles_url)

    # TODO: sanitize student names and fieldnote titles
    for student, student_url in fieldnotes:
        table[student_url] = f'{semester_name}/{FIELDNOTES_FOLDER_NAME}/{student}/index.html'
        pages = get_all_links(student_url)
        for title, note_url in pages:
            table[note_url] = f'{semester_name}/{FIELDNOTES_FOLDER_NAME}/{student}/{title}.html'

    for student, student_url in profiles:
        table[student_url] = f'{semester_name}/{PROFILES_FOLDER_NAME}/{student}.html'

    [print(k, v) for k,v in table.items()]


def spring_2017_digital():
    url = 'http://fieldnotes.makingandknowing.org/mainSpace/Spring%202017%20Digital%20Archive.html'
    soup = BeautifulSoup(get_html(url), 'html.parser')

def fall_2016():
    url = 'http://fieldnotes.makingandknowing.org/mainSpace/Fall%202016%20Archive.html'
    soup = BeautifulSoup(get_html(url), 'html.parser')

def spring_2016():
    url = 'http://fieldnotes.makingandknowing.org/mainSpace/Spring%202016%20archive.html'
    soup = BeautifulSoup(get_html(url), 'html.parser')

def fall_2015():
    url = 'http://fieldnotes.makingandknowing.org/mainSpace/Fall%202015.html'
    soup = BeautifulSoup(get_html(url), 'html.parser')

def spring_2015():
    url = 'http://fieldnotes.makingandknowing.org/mainSpace/Spring%202015.html'
    soup = BeautifulSoup(get_html(url), 'html.parser')

def fall_2014():
    url = 'http://fieldnotes.makingandknowing.org/mainSpace/Fall%202014%20Archives.html'
    soup = BeautifulSoup(get_html(url), 'html.parser')

if __name__ == '__main__':
    main()
