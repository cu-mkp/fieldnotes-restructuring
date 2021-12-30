#!/bin/sh
CONTENT="/mnt/c/code/github/fieldnotes-content/content/"

replace_ann () {
    cd $CONTENT
    echo $1
    cd $1
    if [ -d annotations ] || [ -d ann ]; then
        if [ -d annotations ]; then
            git mv annotations ann
        fi
        cd ann
        echo $(pwd)
        for FOLDER in $(ls -d -- */); do
            cd $FOLDER
            for FILE in $(find . -type f -name "*_annotations_*"); do
                NEW_NAME=$1"_ann_"$(echo $FILE | cut -d'_' -f3-)
                git mv $FILE $NEW_NAME
            done
        done

    fi
    cd $CONTENT
}

replace_ann "fa14"
replace_ann "sp15"
replace_ann "fa15"
replace_ann "sp16"
replace_ann "fa16"
replace_ann "sp17"
replace_ann "sp17dh"
replace_ann "fa17"

replace_fieldnotes () {
    cd $CONTENT
    echo $1
    cd $1
    if [ -d fieldnotes ] || [ -d fld ]; then
        if [ -d fieldnotes ]; then
            git mv fieldnotes fld
        fi
        cd fld
        for FOLDER in $(ls -d -- */); do
            cd $FOLDER
            for FILE in $(find . -type f -name "*_fieldnotes_*"); do
                NEW_NAME=$1"_fld_"$(echo $FILE | cut -d'_' -f3-)
                git mv $FILE $NEW_NAME
            done
        done

    fi
    cd $CONTENT
}

replace_fieldnotes "fa14"
replace_fieldnotes "sp15"
replace_fieldnotes "fa15"
replace_fieldnotes "sp16"
replace_fieldnotes "fa16"
replace_fieldnotes "sp17"
replace_fieldnotes "sp17dh"
replace_fieldnotes "fa17"

