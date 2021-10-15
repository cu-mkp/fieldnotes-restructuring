#!/bin/sh
DIR='/mnt/c/code/github/fieldnotes-content/content/'
OUT='rename_history.csv'
TMPOUT='/tmp/gitlogout.txt'
TMPHIST='/tmp/gitloghistrenames.txt'
CWD=$(pwd)

cd $DIR
find $DIR -type f -printf "\"%p\"\n" -o -type d -name '.git' -prune > $TMPOUT

set -f
while IFS= read -r line;
do
    echo $line
    git log -M --format='' --name-only --summary --follow -- "$line"
    #sed -n '1p;$p' $TMPHIST
done < $TMPOUT

cd $CWD
