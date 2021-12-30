#include <unistd.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>

const size_t MAX_N_FILES = 30;
const size_t MAX_FILE_NAME_LENGTH = 256;

char *CONTENT = "/mnt/c/code/github/fieldnotes-content/content/";
int dry_run;

void fix_semester(const char *semester);
void fix_subfolder(const char *subfolder, const char *abbreviation);
void git_mv(const char *src, const char *dst, const int dry_run);
void pwd();
size_t replace_substring(char *out, const char *str, const char *substr, const char *replacement);
size_t split_lines(char **out, const char *in);
void read_command(char *out, const char *command);

int main(int argc, char **argv) {
    if (strcmp(argv[0], "-n")) {
        dry_run = 1;
    } else {
        dry_run = 0;
    }

    char *SEMESTER[8] = {"fa14/", "sp15/", "fa15/", "sp16/", "fa16/", "sp17/", "sp17dh/", "fa17/"};

    // Go to CONTENT directory.
    chdir(CONTENT);

    char newstr[100];
    replace_substring(newstr, "fa14_annotations_test.html", "annotations", "ann");
    printf("%s\n", newstr);

    char result[MAX_N_FILES * MAX_FILE_NAME_LENGTH];
    read_command(result, "ls -d -- */");
    printf("%s\n", result);

    char **lines = malloc(MAX_N_FILES * sizeof(char*));
    for (int i=0; i<MAX_N_FILES; i++) {
        lines[i] = malloc(MAX_FILE_NAME_LENGTH + 1);
    }
    size_t size = split_lines(lines, "test1\ntest2\n\n");
    for (int i=0; i<size; i++) {
        printf("%s", lines[i]);
    }
    printf("\n");
    for (int i=0; i<size; i++) {
        free(lines[i]);
    }
    free(lines);

    /*
    // Loop over semesters.
    for (int i=0; i<8; i++) {
        //fix_semester(SEMESTER[i]);
        chdir(CONTENT); // Return to CONTENT directory, just in case.
    }
    */

    return 0;
}

void fix_semester(const char *semester) {
    chdir(semester);
    pwd();

    if (strcmp(semester, "sp17dh") == 0) // don't do this for sp17dh
        fix_subfolder("annotations", "ann"); // rename annotations to ann

    fix_subfolder("fieldnotes", "fld"); // rename fieldnotes to fld
}

void fix_subfolder(const char *subfolder, const char *abbrev) {
    git_mv(subfolder, abbrev, dry_run);

    if (dry_run)
        chdir(subfolder);
    else
        chdir(abbrev);

    char **folders = malloc(MAX_N_FILES * sizeof(char*));
    for (int i=0; i<MAX_N_FILES; i++) {
        folders[i] = malloc(MAX_FILE_NAME_LENGTH);
    }
    char output[MAX_N_FILES * MAX_FILE_NAME_LENGTH];
    read_command(output, "ls -1 -d -- */");
    size_t n_folders = split_lines(folders, output); // Get directories in semester.
    //free(output);

    for (int i=0; i<n_folders; i++) {
        chdir(folders[i]);
        pwd();

        char command[256];
        snprintf(command, sizeof(command), "find . -name '*%s*'", subfolder);
        char output[MAX_N_FILES * MAX_FILE_NAME_LENGTH];
        read_command(output, command);

        char **files = malloc(MAX_N_FILES * sizeof(char*));
        for (int j=0; j<MAX_N_FILES; j++) {
            files[j] = malloc(MAX_FILE_NAME_LENGTH);
        }
        size_t n_files = split_lines(files, output); // Get files with subfolder in the name.
        //free(output);

        for (int j=0; j<n_files; j++) {
            char new_filename[MAX_FILE_NAME_LENGTH];
            replace_substring(new_filename, files[j], subfolder, abbrev);
            git_mv(files[j], new_filename, dry_run);
        }
        for (int j=0; j<n_files; j++) {
            free(files[j]);
        }
        free(files);
        chdir("../");
    }
    for (int i=0; i<n_folders; i++) {
        free(folders[i]);
    }
    free(folders);
    chdir("../");
}

size_t split_lines(char **out, const char *in) {
    size_t n = strlen(in);
    char in_copy[n];
    strncpy(in_copy, in, n);
    in_copy[n] = '\0';

    size_t count = 0;

    out[count] = strtok(in_copy, "\n");
    while (out[count] != NULL) {
        count++;
        out[count] = strtok(NULL, "\n");
    }

    return count + 1;
}

void read_command(char *out, const char *command) {
    char buf[256];
    FILE *pipe;

    pipe = popen(command, "w");
    while (fgets(buf, 256, pipe) != NULL) {
        strncat(out, buf, 256);
    }
}

size_t replace_substring(char *out, const char *str, const char *substr, const char *replacement) {
    size_t str_size = strlen(str);
    size_t substr_size = strlen(substr);
    size_t replacement_size = strlen(replacement);

    size_t size = str_size + replacement_size - substr_size;

    char *p = strstr(str, substr);
    if (p == NULL)
        return 0;

    strncat(out, str, p - str);
    strncat(out, replacement, replacement_size);
    strcat(out, p + substr_size);

    return size;
}

void git_mv(const char *src, const char *dst, const int dry_run) {
    char command[256];
    if (dry_run)
        snprintf(command, sizeof(command), "git mv -n %s %s > /dev/null", src, dst);
    else
        snprintf(command, sizeof(command), "git mv %s %s > /dev/null", src, dst);

    system(command);
}

void pwd() {
    char buf[MAX_FILE_NAME_LENGTH];
    printf("%s\n", getcwd(buf, MAX_FILE_NAME_LENGTH));
}
