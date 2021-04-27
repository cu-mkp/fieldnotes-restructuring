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
        for row in reader:
            if row[0] in CORRECTIONS.keys():
                raise Exception(f'Key conflict:\n Key: \'{row[0]}\'\n Old: \'{CORRECTIONS[row[0]]}\'\n New: \'{row[1]}\'')
            else:
                CORRECTIONS[row[0]] = row[1]
    mapping = {}
    missing = []
    for semester in [sp16]:
        temp_mapping, temp_missing = semester()
        mapping = merge_no_overwrite(mapping, temp_mapping)
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

def merge_no_overwrite(dict1, dict2):
    new_dict = {}
    for k,v in dict1.items():
        new_dict[k] = v
    for k,v in dict2.items():
        if k in new_dict.keys():
            raise Exception(f'Key conflict:\n  Key: \'{k}\'\n  Old: \'{new_dict[k]}\'\n  New: \'{v}\'')
        else:
            new_dict[k] = v
    return new_dict

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
    links = [(sanitize(e.string), unquote(e['href'])) for e in soup.find_all(lambda t: t.name=='a' and t.has_attr('href') and t['href'][0] != '#')]
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
            elif '.html' not in filename:
                # TODO: determine if this is proper behavior.
                # The idea here is to not add a link as missing if it's an external link.
                continue
            else:
                missing.append((parent_file, filename))
                continue   # don't add to mapping

        if as_folders:
            mapping[filename] = f'{parent_file_path}/{title}/index.html'
        else:
            if filename.rsplit('.')[1] != 'html':
                # TODO: figure out what to do with non-html files
                #mapping[filename] = f'{parent_file_path}/{filename}'
                continue # don't add to mapping
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
    profiles_mapping, profiles_missing = map_links(profiles_file, f'{semester_name}/{PROFILES_FOLDER_NAME}', profiles, as_folders=False)

    mapping = merge_no_overwrite(mapping, fieldnotes_mapping)
    mapping = merge_no_overwrite(mapping, profiles_mapping)
    missing.extend(fieldnotes_missing)
    missing.extend(profiles_missing)

    for student_file, new_path in fieldnotes_mapping.items():
        student_notes = get_all_links_from_file(FOLDER_PREFIX + student_file)
        student_notes_mapping, student_notes_missing = map_links(student_file, new_path.rsplit('/index.html')[0], student_notes, as_folders=False)

        mapping = merge_no_overwrite(mapping, student_notes_mapping)
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

    mapping = merge_no_overwrite(mapping, fieldnotes_mapping)
    missing.extend(fieldnotes_missing)

    for student_file, new_path in fieldnotes_mapping.items():
        # Nikhil and Wenrui's fieldnotes are just one file directly linked to by their name.
        # Hence do not attempt to map them.
        if student_file in ['Nikhil Ramachandran - DH Field Notes SP17.html', 'Wenrui Zhao - DH Field Notes SP17.html']:
            continue

        student_notes = get_all_links_from_file(FOLDER_PREFIX + student_file)
        student_notes_mapping, student_notes_missing = map_links(student_file, new_path.rsplit('/index.html')[0], student_notes, as_folders=False)

        mapping = merge_no_overwrite(mapping, student_notes_mapping)
        missing.extend(student_notes_missing)

    return mapping, missing

def fa16():
    # TODO: confirm the placement of example in profiles
    mapping = {}
    missing = []
    semester_name = 'fa16'

    filename = unquote('Fall%202016%20Archive.html')
    mapping[filename] = f'{semester_name}/index.html'

    soup = BeautifulSoup(get_html_from_file(FOLDER_PREFIX + filename), 'html.parser')

    fieldnotes_file = unquote(soup.find(string=re.compile('Field Notes')).parent['href'])
    profiles_file = unquote(soup.find(string=re.compile('Student')).parent['href'])
    mapping[fieldnotes_file] = f'{semester_name}/{FIELDNOTES_FOLDER_NAME}/index.html'
    mapping[profiles_file] = f'{semester_name}/{PROFILES_FOLDER_NAME}/index.html'

    fieldnotes = get_all_links_from_file(FOLDER_PREFIX + fieldnotes_file)
    profiles = get_all_links_from_file(FOLDER_PREFIX + profiles_file)

    fieldnotes_mapping, fieldnotes_missing = map_links(fieldnotes_file, f'{semester_name}/{FIELDNOTES_FOLDER_NAME}', fieldnotes, as_folders=True)
    profiles_mapping, profiles_missing = map_links(profiles_file, f'{semester_name}/{PROFILES_FOLDER_NAME}', profiles, as_folders=False)

    mapping = merge_no_overwrite(mapping, fieldnotes_mapping)
    mapping = merge_no_overwrite(mapping, profiles_mapping)
    missing.extend(fieldnotes_missing)
    missing.extend(profiles_missing)

    for student_file, new_path in fieldnotes_mapping.items():
        student_notes = get_all_links_from_file(FOLDER_PREFIX + student_file)
        student_notes_mapping, student_notes_missing = map_links(student_file, new_path.rsplit('/index.html')[0], student_notes, as_folders=False)

        mapping = merge_no_overwrite(mapping, student_notes_mapping)
        missing.extend(student_notes_missing)

    return mapping, missing

def sp16():
    mapping = {}
    missing = []
    semester_name = 'sp16'

    filename = unquote('Spring%202016%20archive.html')
    mapping[filename] = f'{semester_name}/index.html'

    soup = BeautifulSoup(get_html_from_file(FOLDER_PREFIX + filename), 'html.parser')

    fieldnotes_file = unquote(soup.find(string=re.compile('Field Notes')).parent['href'])
    annotations_file = unquote(soup.find(string=re.compile('Annotation')).parent['href'])
    profiles_file = unquote(soup.find(string=re.compile('Student')).parent['href'])
    mapping[fieldnotes_file] = f'{semester_name}/{FIELDNOTES_FOLDER_NAME}/index.html'
    mapping[annotations_file] = f'{semester_name}/annotation-field-notes/index.html'
    mapping[profiles_file] = f'{semester_name}/{PROFILES_FOLDER_NAME}/index.html'

    fieldnotes = get_all_links_from_file(FOLDER_PREFIX + fieldnotes_file)
    fieldnotes = [page for page in fieldnotes if page[0] not in [sanitize('Annotation Field Notes'), sanitize('Field Notes Fall 2015')]]
    annotations = get_all_links_from_file(FOLDER_PREFIX + annotations_file)
    profiles = get_all_links_from_file(FOLDER_PREFIX + profiles_file)

    fieldnotes_mapping, fieldnotes_missing = map_links(fieldnotes_file, f'{semester_name}/{FIELDNOTES_FOLDER_NAME}', fieldnotes, as_folders=True)
    annotations_mapping, annotations_missing = map_links(annotations_file, f'{semester_name}/annotation-field-notes', annotations, as_folders=True)
    profiles_mapping, profiles_missing = map_links(profiles_file, f'{semester_name}/{PROFILES_FOLDER_NAME}', profiles, as_folders=False)

    mapping = merge_no_overwrite(mapping, fieldnotes_mapping)
    mapping = merge_no_overwrite(mapping, annotations_mapping)
    mapping = merge_no_overwrite(mapping, profiles_mapping)
    missing.extend(fieldnotes_missing)
    missing.extend(annotations_missing)
    missing.extend(profiles_missing)

    for student_file, new_path in fieldnotes_mapping.items():
        # skip the students whose pages link directly to fieldnotes (no index)
        direct_linkers = ['Amy Chang - Field Notes SP16.html', 'Cleo Nisse - Field Notes SP16.html', 'Yuanxie Shi - Field Notes SP16.html', 'Olivia Clemens - Field Notes SP16.html']
        if student_file in direct_linkers:
            continue

        student_notes = get_all_links_from_file(FOLDER_PREFIX + student_file)
        # Some students share links with other students; we put the shared ones in the other students' folders
        # TODO: confirm how to handle these cases
        if student_file == 'Robin Reich - Field Notes SP16.html':
            shared_pages = ['Yuanxie Shi - Field Notes SP16.html', 'Verdigris - 5%.html', 'Priming Canvas with earth red oil paint.html', 'Reich Transferring Images.html']
            student_notes = filter(lambda page: page[1] not in shared_pages, student_notes)
        if student_file == 'Teresa Soley - Field Notes SP16.html':
            shared_pages = ['Goldenberg- Verdigris.html', 'Ndungu - Field Notes SP16 - HCR.html', 'Goldenberg-Painting_With_Distemper.html', 'Teresa Soley - Field Notes SP16 - Annotation Plans.html']
            student_notes = filter(lambda page: page[1] not in shared_pages, student_notes)
        if student_file == 'Safety Protocol Examples.html':
            shared_pages = ['Rosenkranz Buscarino - Verdigris SP16.html']
            student_notes = filter(lambda page: page[1] not in shared_pages, student_notes)

        student_notes_mapping, student_notes_missing = map_links(student_file, new_path.rsplit('/index.html')[0], student_notes, as_folders=False)

        mapping = merge_no_overwrite(mapping, student_notes_mapping)
        missing.extend(student_notes_missing)

    for annotation_file, new_path in annotations_mapping.items():
        pages = get_all_links_from_file(FOLDER_PREFIX + annotation_file)

        if annotation_file == 'Soley - Field Notes SP16 - Varnish Annotation.html':
            shared_pages = ['.htmlGNS - Field Notes SP16 - Contemporary Recipes', '.htmlGNS - Field Notes SP16 - Secondary Source Notes', '.htmlGNS - Field Notes SP16 - Experimental Field Notes']
            pages = filter(lambda page: page[1] not in shared_pages, pages)

        pages_mapping, pages_missing = map_links(annotation_file, new_path.rsplit('/index.html')[0], pages, as_folders=False)

        mapping = merge_no_overwrite(mapping, pages_mapping)
        missing.extend(pages_missing)

    return mapping, missing

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
