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
    for semester in [fa14, sp15, fa15, sp16, fa16, sp17dh, sp17]:
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
            new_path = f'{parent_file_path}/{title}/index.html'
        else:
            if filename.rsplit('.')[1] != 'html':
                # Ignore non-html files.
                continue
            else:
                new_path = f'{parent_file_path}/{title}.html'

        if filename in mapping.keys() and mapping[filename] != new_path:
            raise Exception(f'Key conflict:\nParent file: \'{parent_file}\'\nParent path: \'{parent_file_path}\'\nFile title: \'{title}\'\n  Key: \'{filename}\'\n  Old: \'{mapping[filename]}\'\n  New: \'{new_path}\'')

        mapping[filename] = new_path

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

    # Hard fixes because someone did something terrible 4 years ago
    fieldnotes = [note for note in fieldnotes if note[1] not in ['Jennifer Gambel Wellington - Field Notes SP17.html', 'Sasha Grabovskiy - Field Notes SP17.html']]
    fieldnotes.append((sanitize('Jennifer Gambel Wellington'), 'Jennifer Gambel Wellington - Field Notes SP17.html'))
    fieldnotes.append((sanitize('Sasha Grabovskiy'), 'Sasha Grabovskiy - Field Notes SP17.html'))

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

        # shared file dictionary
        # shared file : first author
        shared = { 'Yuanxie Shi - Field Notes SP16.html' : None,
                   'Verdigris - 5%.html' : None,
                   'Priming Canvas with earth red oil paint.html' : None,
                   'Reich Transferring Images.html' : None,
                   'Teresa Soley - Field Notes SP16 - Annotation Plans.html' : None,
                   'Goldenberg- Verdigris.html' : None,
                   'Ndungu - Field Notes SP16 - HCR.html' : None,
                   'Goldenberg-Painting_With_Distemper.html' : None,
                   'Rosenkranz Buscarino - Verdigris SP16.html' : None }

        student_notes = list(filter(lambda note: note[1] not in shared.keys() or student_file == shared[note[1]], student_notes))

        student_notes_mapping, student_notes_missing = map_links(student_file, new_path.rsplit('/index.html')[0], student_notes, as_folders=False)

        mapping = merge_no_overwrite(mapping, student_notes_mapping)
        missing.extend(student_notes_missing)

    for annotation_file, new_path in annotations_mapping.items():
        pages = get_all_links_from_file(FOLDER_PREFIX + annotation_file)

        shared = { '.htmlGNS - Field Notes SP16 - Contemporary Recipes' : None,
                   '.htmlGNS - Field Notes SP16 - Secondary Source Notes' : None,
                   '.htmlGNS - Field Notes SP16 - Experimental Field Notes' : None }
        pages = list(filter(lambda page: page[1] not in shared.keys() or annotation_file == shared[page[1]], pages))

        pages_mapping, pages_missing = map_links(annotation_file, new_path.rsplit('/index.html')[0], pages, as_folders=False)

        mapping = merge_no_overwrite(mapping, pages_mapping)
        missing.extend(pages_missing)

    return mapping, missing

def fa15():
    mapping = {}
    missing = []
    semester_name = 'fa15'

    filename = unquote('Fall%202015.html')
    mapping[filename] = f'{semester_name}/index.html'

    soup = BeautifulSoup(get_html_from_file(FOLDER_PREFIX + filename), 'html.parser')

    fieldnotes_file = unquote(soup.find(string=re.compile('Field Notes')).parent['href'])
    annotations_file = unquote(soup.find(string=re.compile('Annotations')).parent['href'])
    profiles_file = unquote(soup.find(string=re.compile('Student Profiles')).parent['href'])
    calendar_file = unquote(soup.find(string=re.compile('Calendar')).parent['href'])
    hrr_file = unquote(soup.find(string=re.compile('Historical Recipe Reconstruction')).parent['href'])
    mapping[fieldnotes_file] = f'{semester_name}/{FIELDNOTES_FOLDER_NAME}/index.html'
    mapping[annotations_file] = f'{semester_name}/annotations/index.html'
    mapping[profiles_file] = f'{semester_name}/{PROFILES_FOLDER_NAME}/index.html'
    mapping[calendar_file] = f'{semester_name}/calendar.html'
    mapping[hrr_file] = f'{semester_name}/historical-recipe-reconstruction.html'

    mapping[unquote('pH%20Strip%20Identification%20Charts.html')] = f'{semester_name}/{FIELDNOTES_FOLDER_NAME}/{sanitize("pH Strip Identification Charts")}.html' # pH strip file

    fieldnotes = get_all_links_from_file(FOLDER_PREFIX + fieldnotes_file)
    fieldnotes = list(filter(lambda page: page[0] not in [sanitize('Spring 2015 Field Notes'), sanitize('Fall 2014 Field Notes'), sanitize('pH Strip Identification Charts')], fieldnotes)) # Ignore non-field note links.
    annotations = get_all_links_from_file(FOLDER_PREFIX + annotations_file)
    profiles = get_all_links_from_file(FOLDER_PREFIX + profiles_file)

    fieldnotes_mapping, fieldnotes_missing = map_links(fieldnotes_file, f'{semester_name}/{FIELDNOTES_FOLDER_NAME}', fieldnotes, as_folders=True)
    annotations_mapping, annotations_missing = map_links(annotations_file, f'{semester_name}/annotations', annotations, as_folders=False)
    profiles_mapping, profiles_missing = map_links(profiles_file, f'{semester_name}/{PROFILES_FOLDER_NAME}', profiles, as_folders=False)

    mapping = merge_no_overwrite(mapping, fieldnotes_mapping)
    mapping = merge_no_overwrite(mapping, annotations_mapping)
    mapping = merge_no_overwrite(mapping, profiles_mapping)
    missing.extend(fieldnotes_missing)
    missing.extend(annotations_missing)
    missing.extend(profiles_missing)

    for student_file, new_path in fieldnotes_mapping.items():
        direct_linkers = ['Jenny Boulboulle - Field Notes FA15.html']
        if student_file in direct_linkers:
            continue

        student_notes = get_all_links_from_file(FOLDER_PREFIX + student_file)

        # Field notes with multiple authors are saved in the folder of the first author listed on the page.
        # shared file : student name to be saved under
        shared = { 'Red Lake Pigments Reconstruction - Cochineal EF-SM.html' : 'Emilie Foyer - Field Notes FA15.html',
                   'Logwood - EF-SM.html' : 'Emilie Foyer - Field Notes FA15.html',
                   'Annotation Preparation.html' : 'Marilyn Bowen - Field Notes FA15.html',
                   'new.html' : 'Danielle Carr - Field Notes - FA15.html',
                   'Red Lake Pigments.html' : 'Kathryn Kremnitzer - Field Notes FA15.html'
                   }

        student_notes = list(filter(lambda note: note[1] not in shared.keys() or student_file == shared[note[1]], student_notes))

        student_notes_mapping, student_notes_missing = map_links(student_file, new_path.rsplit('/index.html')[0], student_notes, as_folders=False)

        mapping = merge_no_overwrite(mapping, student_notes_mapping)
        missing.extend(student_notes_missing)

    return mapping, missing

def sp15():
    mapping = {}
    missing = []
    semester_name = 'sp15'

    filename = unquote('Spring%202015.html')
    mapping[filename] = f'{semester_name}/index.html'

    soup = BeautifulSoup(get_html_from_file(FOLDER_PREFIX + filename), 'html.parser')

    fieldnotes = [(sanitize(title), unquote(url)) for title, url in
            [('Guilia Chiostrini', 'Chiostrini%2C%20Giuila.html'),
             ('Celia Durkin', 'Durkin%2C%20Celia.html'),
             ('Shiye Fu', 'Fu%20Shiye%20Fieldnotes.html'),
             ('Sofia Gans', 'Gans%2C%20Sofia.html'),
             ('Caroline Marris', 'Marris%2C%20Caroline.html'),
             ('Jef Palframan', 'Palframan%2C%20Jef.html'),
             ('Stephanie Pope', 'Pope%2C%20Stephanie.html'),
             ('Zhiqi Zhang', 'Zhang%2C%20Zhiqi.html'),
             ('Jenny Boulboulle', 'Boulboullé%2C%20Jenny.html')]]
    assignments = [(sanitize(title), unquote(url)) for title, url in
            [('Bread molding', 'Bread%20Molding%20Reconstruction%20-%20Spring%202015.html'),
             ('Sand casting recipes', 'Sand%20casting%20recipes.html'),
             ('Plaster casting', 'Plaster%20Casting%20Recipes.html')]]

    fieldnotes_mapping, fieldnotes_missing = map_links(filename, f'{semester_name}/{FIELDNOTES_FOLDER_NAME}', fieldnotes, as_folders=True)
    assignments_mapping, assignments_missing = map_links(filename, f'{semester_name}/assignments', assignments, as_folders=False)

    mapping = merge_no_overwrite(mapping, fieldnotes_mapping)
    mapping = merge_no_overwrite(mapping, assignments_mapping)
    missing.extend(fieldnotes_missing)
    missing.extend(assignments_missing)

    for student_file, new_path in fieldnotes_mapping.items():
        direct_linkers = []
        if student_file in direct_linkers:
            continue

        student_notes = get_all_links_from_file(FOLDER_PREFIX + student_file)

        # Field notes with multiple authors are saved in the folder of the first author listed on the page.
        # If the authors aren't listed on the page, we base it on the url.
        # shared file : student name to be saved under
        shared = { 'HRR Marchpane Reconstruction.html' : 'Fu Shiye Fieldnotes.html',
                   'Bread Molding Reconstruction.html' : 'Gans, Sofia.html',
                   'gans-durkin alabaster.html' : 'Gans, Sofia.html',
                   'gans-durkin sand casting.html' : 'Durkin, Celia.html',
                   'durkin-gans sugar casting.html' : 'Durkin, Celia.html',
                   'Durkin-Marris Historical Recipe Reconstruction.html' : 'Durkin, Celia.html',
                   'Marris-Pope Bread Molding Reconstruction.html' : 'Marris, Caroline.html',
                   'Plaster casting with flowers - field notes.html' : 'Pope, Stephanie.html',
                   'Sand Casting Field Notes - Giulia Chiostrini.html' : 'Chiostrini, Giulia.html',
                   'Palframan - Plaster Molding Spring 2015.html' : 'Palframan - Field Notes Spring 2015.html',
                   }

        student_notes = list(filter(lambda note: note[1] not in shared.keys() or student_file == shared[note[1]], student_notes))

        if student_file == 'Palframan - Field Notes Spring 2015.html':
            student_notes = list(filter(lambda note: note[1] != 'Palframan - Fieldnotes Fall 2014.html', student_notes))

        student_notes_mapping, student_notes_missing = map_links(student_file, new_path.rsplit('/index.html')[0], student_notes, as_folders=False)

        mapping = merge_no_overwrite(mapping, student_notes_mapping)
        missing.extend(student_notes_missing)

    return mapping, missing

def fa14():
    mapping = {}
    missing = []
    semester_name = 'fa14'

    filename = unquote('Fall%202014%20Archives.html')
    mapping[filename] = f'{semester_name}/index.html'

    #soup = BeautifulSoup(get_html_from_file(FOLDER_PREFIX + filename), 'html.parser')

    # TODO: this mess
    links = get_all_links_from_file(FOLDER_PREFIX + filename)

    all_mapping, all_missing = map_links(filename, semester_name, links, as_folders=False)
    del all_mapping['Bread Molding Reconstruction - Spring 2015.html'] # as the name implies, this actually belongs in Spring 2015
    mapping = merge_no_overwrite(mapping, all_mapping)
    missing.extend(all_missing)

    return mapping, missing

if __name__ == '__main__':
    main()
