# rename all archival index.html to [sem]_[category]_[student/project]_index-superseded.html

logfile="/Users/gregory/Code/github/fieldnotes-restructuring/intermediate-indexes/rename-log.txt"

semesters="fa14 sp15 fa15 sp16 fa16 sp17 sp17dh fa17"
content="/Users/gregory/Code/github/fieldnotes-content/content/"

cd "$content"

for sem in $semesters
do
    cd "$content"
    # sem
    if [ -d "$sem" ];
    then
        cd "$sem"
        sem_dir="$(pwd)"
    else
        continue
    fi

    [ -f "index.html" ] && mv -i "index.html" $sem"_index-superseded.html" && echo "$(ls *superseded*)" >> $logfile
    cd "$sem_dir"

    # ann
    if [ -d "$sem_dir/ann" ];
    then
        cd "$sem_dir/ann"
        [ -f "index.html" ] && mv -i "index.html" $sem"_ann_index-superseded.html" && echo "$(ls *superseded*)" >> $logfile

        # ann projects
        for project in $(find . -mindepth 1 -maxdepth 1 -type d | cut -c 3-)
        do
            if [ -d "$project" ];
            then
                cd "$project"
                [ -f "index.html" ] && mv -i "index.html" $sem"_ann_"$project"_index-superseded.html" && echo "$(ls *superseded*)" >> $logfile
                cd "$sem_dir/ann"
            fi
        done
        cd "$sem_dir"
    fi

    # fld
    if [ -d "$sem_dir/fld" ];
    then
        cd "$sem_dir/fld"
        [ -f "index.html" ] && mv -i "index.html" $sem"_fld_index-superseded.html" && echo "$(ls *superseded*)" >> $logfile

        # fld student
        for student in $(find . -mindepth 1 -maxdepth 1 -type d | cut -c 3-)
        do
            if [ -d "$student" ];
            then
                cd "$student"
                [ -f "index.html" ] && mv -i "index.html" $sem"_fld_"$student"_index-superseded.html" && echo "$(ls *superseded*)" >> $logfile
                cd "$sem_dir/fld"
            fi
        done
        cd "$sem_dir"
    fi

    # profiles
    if [ -d "$sem_dir/profiles" ];
    then
        cd "$sem_dir/profiles"
        [ -f "index.html" ] && mv -i "index.html" $sem"_profiles_index-superseded.html" && echo "$(ls *superseded*)" >> $logfile
        cd "$content"
    fi
done
