git diff --name-status bf838..HEAD | grep ^R | cut -f2- | sed -e "s/\(.*\)\t\(.*\)/\"\1\",\"\2\"/g"
