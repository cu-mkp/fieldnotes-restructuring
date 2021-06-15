#!/bin/env python3
import csv
import os
import shutil

SOURCE_PREFIX = '/mnt/c/code/github/fieldnotes-content/mainSpace/'
DEST_PREFIX = '/mnt/c/code/github/fieldnotes-content/mainSpace/'
MAPPING_FILE = '/mnt/c/code/github/fieldnotes-reindex/mapping.csv'

METHOD = 'move'

def main():
    with open(MAPPING_FILE, 'r') as fp:
        reader = csv.reader(fp)
        first = True
        for src, dst in reader:
            if first:
                first = False
                continue
            if METHOD = 'move':
                move_file(os.path.join(SOURCE_PREFIX, src), os.path.join(DEST_PREFIX, dst))
            elif METHOD = 'copy':
                copy_file(os.path.join(SOURCE_PREFIX, src), os.path.join(DEST_PREFIX, dst))
            else:
                raise Exception('Unrecognized method:', METHOD)

def copy_file(src, dst):
    if os.path.exists(dst):
        raise Exception('Oops! Problem when copying from source. Destination file already exists:\n', os.path.relpath(src, SOURCE_PREFIX), '->', os.path.relpath(dst, DEST_PREFIX))
    print('making dirs:', os.path.dirname(dst))
    print('copying file:', os.path.relpath(src, SOURCE_PREFIX), '->', os.path.relpath(dst, DEST_PREFIX))
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy(src, dst)

def move_file(src, dst):
    if os.path.exists(dst):
        raise Exception('Oops! Problem when moving from source. Destination file already exists:\n', os.path.relpath(src, SOURCE_PREFIX), '->', os.path.relpath(dst, DEST_PREFIX))
    print('making dirs:', os.path.dirname(dst))
    print('moving file:', os.path.relpath(src, SOURCE_PREFIX), '->', os.path.relpath(dst, DEST_PREFIX))
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.move(src, dst)

if __name__ == '__main__':
    main()
