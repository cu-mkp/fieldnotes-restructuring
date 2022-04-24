logfile="/Users/gregory/Code/github/fieldnotes-restructuring/intermediate-indexes/log.txt"

semesters="fa14 sp15 fa15 sp16 fa16 sp17 sp17dh"
content="/Users/gregory/Code/github/fieldnotes-content/content/"

template_sem="/Users/gregory/Code/github/fieldnotes-content/content/fa17/index.md"
template_ann="/Users/gregory/Code/github/fieldnotes-content/content/fa17/ann/index.md"
template_fld="/Users/gregory/Code/github/fieldnotes-content/content/fa17/fld/index.md"
template_profiles="/Users/gregory/Code/github/fieldnotes-content/content/fa17/profiles/index.md"
template_ann_student="/Users/gregory/Code/github/fieldnotes-content/content/fa17/ann/stucco_elizondo-garza/index.md"
template_fld_student="/Users/gregory/Code/github/fieldnotes-content/content/fa17/fld/elizondo-garza_nina/index.md"

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

    cp -i "$template_sem" ./
    echo "$(pwd)/index.md" >> $logfile
    cd "$sem_dir"

    # ann
    if [ -d "$sem_dir/ann" ];
    then
        cd "$sem_dir/ann"
        cp -i "$template_ann" ./
        echo "$(pwd)/index.md" >> $logfile

        # ann projects
        for project in $(find . -maxdepth 1 -type d)
        do
            if [ -d "$project" ];
            then
                cd "$project"
                cp -i "$template_ann_student" ./
                echo "$(pwd)/index.md" >> $logfile
                cd "$sem_dir/ann"
            fi
        done
        cd "$sem_dir"
    fi

    # fld
    if [ -d "$sem_dir/fld" ];
    then
        cd "$sem_dir/fld"
        cp -i "$template_fld" ./
        echo "$(pwd)/index.md" >> $logfile

        # fld student
        for student in $(find . -maxdepth 1 -type d)
        do
            if [ -d "$student" ];
            then
                cd "$student"
                cp -i "$template_fld_student" ./
                echo "$(pwd)/index.md" >> $logfile
                cd "$sem_dir/fld"
            fi
        done
        cd "$sem_dir"
    fi

    # profiles
    if [ -d "$sem_dir/profiles" ];
    then
        cd "$sem_dir/profiles"
        cp -i "$template_profiles" ./
        echo "$(pwd)/index.md" >> $logfile
        cd "$content"
    fi
done
