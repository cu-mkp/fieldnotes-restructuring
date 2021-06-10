#!/bin/env python3
import csv
import os
import shutil

SOURCE_PREFIX = '/mnt/c/code/misc/mkp/fieldnotes/archive/mainSpace/'
DEST_PREFIX = '/mnt/c/code/misc/mkp/fieldnotes/restructure/'

def main():
    with open('mapping.csv', 'r') as fp:
        reader = csv.reader(fp)
        first = True
        for src, dst in reader:
            if first:
                first = False
                continue
            copy_file(os.path.join(SOURCE_PREFIX, src),
                      os.path.join(DEST_PREFIX, dst))

def copy_file(src, dst):
    print('making dirs:', os.path.dirname(dst))
    print('copying file:', os.path.relpath(src, SOURCE_PREFIX), '->', os.path.relpath(dst, DEST_PREFIX))
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy(src, dst)

if __name__ == '__main__':
    main()
