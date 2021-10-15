#!/bin/sh
DIR='/mnt/c/code/github/fieldnotes-content/content/'
TMPOUT='/tmp/grepout.txt'

grep_semester () {
    # If you're curious what this grep means:
    # -o means print only the part that matches
    # -i means ignore case
    # -n means print line number
    # -r means recurse into subdirectories
    # -P means use Perl syntax
    # -v means match everything EXCEPT this pattern
    # [^x]* means "match any character except x any number of times"
    #     (and adding a ? at the end makes it non-greedy)
    # (?!xyz) is a negative lookahead for xyz, which means "if you see xyz ahead of this, don't match!"
    grep -oinrP '<a[^>]*href="(?!http)(?!files)(?!mailto:)([^#]*?)"[^>]*>[^<]*<\/a>' $DIR$1 > $TMPOUT
    cat $TMPOUT | grep -niv "index.html" | grep -niv "fa14_ann_2014-field-notes"
}

grep_semester $1
