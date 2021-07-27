#!/bin/env python3
import csv
import os
import shutil

SOURCE_PREFIX = '/mnt/c/code/github/fieldnotes-content/content/'
DEST_PREFIX = '/mnt/c/code/github/fieldnotes-content/content/'
MAPPING_FILE = '/mnt/c/code/github/fieldnotes-restructuring/rename.csv'

METHOD = 'move'
HAS_HEADING = False

def main():
    process()

def process():
    with open(MAPPING_FILE, 'r') as fp:
        reader = csv.reader(fp)
        first = True if HAS_HEADING else False
        for src, dst in reader:
            if first:
                first = False
                continue
            if METHOD == 'dryrun':
                global NEW_FILES
                NEW_FILES = []
                dry_run(os.path.join(SOURCE_PREFIX, src), os.path.join(DEST_PREFIX, dst))
            elif METHOD == 'move':
                move_file(os.path.join(SOURCE_PREFIX, src), os.path.join(DEST_PREFIX, dst))
            elif METHOD == 'copy':
                copy_file(os.path.join(SOURCE_PREFIX, src), os.path.join(DEST_PREFIX, dst))
            else:
                raise Exception('Unrecognized method:', METHOD)

def copy_file(src, dst):
    if os.path.exists(dst):
        raise Exception('Oops! Problem when copying from source. Destination file already exists:\n' + os.path.relpath(src, SOURCE_PREFIX) + ' -> ' + os.path.relpath(dst, DEST_PREFIX))
    print('making dirs:', os.path.dirname(dst))
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    print('copying file:', os.path.relpath(src, SOURCE_PREFIX), '->', os.path.relpath(dst, DEST_PREFIX))
    shutil.copy(src, dst)

def move_file(src, dst):
    if os.path.exists(dst):
        raise Exception('Oops! Problem when moving from source. Destination file already exists:\n' + os.path.relpath(src, SOURCE_PREFIX) + ' -> ' + os.path.relpath(dst, DEST_PREFIX))
    print('making dirs:', os.path.dirname(dst))
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    print('moving file:', os.path.relpath(src, SOURCE_PREFIX), '->', os.path.relpath(dst, DEST_PREFIX))
    shutil.move(src, dst)

def dry_run(src, dst):
    global NEW_FILES
    if os.path.exists(dst) or dst in NEW_FILES:
        raise Exception('Oops! Problem when moving from source. Destination file already exists:\n', os.path.relpath(src, SOURCE_PREFIX), '->', os.path.relpath(dst, DEST_PREFIX))
    print('dirs to make:', os.path.dirname(dst))
    print('file move:', os.path.relpath(src, SOURCE_PREFIX), '->', os.path.relpath(dst, DEST_PREFIX))
    NEW_FILES.append(dst)

if __name__ == '__main__':
    main()
