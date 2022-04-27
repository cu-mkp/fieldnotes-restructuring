# fieldnotes
Various tasks and records regarding the Making and Knowing Project's fieldnotes produced as part of Project courses and activities of hands-on skillbuilding and historical reconstructions.

Works in tandem with https://github.com/cu-mkp/fieldnotes-content where html content pages for M&amp;K fieldnotes are housed

The Project strives to create an openly-accessible and long-term sustainable online versions of these fieldnotes at http://fieldnotes.makingandknowing.org/. 

**NOTE:** the current landing page is an incomplete index.

From 2014-2017, the Making and Knowing Project recorded fieldnotes using a Columbia University wikispace. As of Fall 2018, this service was no longer supported and all data was exported into a s3 bucket in order to preserve all notes. However, this did not preserve the navigation of the wikispace (as these were simply 'pages' and not actually structured in any sort of hierarchy).

From Fall 2018 onwards, fieldnotes were kept as googledocs (and suite) within the Project Google Drive.

## Goals:
- create user-friendly and complete index of pages
- ensure pages are as complete as possible (internal links, images) and maintain page html in most sustainable way possible

## Summary of tasks and progress

For fieldnotes originally from the wiki:
- Within the wiki, the pages were organized as follows:
     - Semester + Year
          - Student Names
               - Activities
               
- This hierarchy was not preserved but is the desired one in order to organize and understand all the pages archived in the original export to s3.
- `organize_field_notes.py` represents an attempt to recreate the original structure
     - Starting from the wiki's original side navigation bar as the highest level, it attempts to recursively follow links down from Semester+Year -> Fieldnotes -> Student Names -> Activities wherever possible
     - By creating a tree structure out of these links, this results in something close to the original structure of the wikispace
     - Unfortunately, many links are broken, missing, incorrect, or do not follow the typical structure
     - In order to document and fix these errors, they are compiled in various CSVs which can be used to manually correct the links where it is obvious where they should point

- Another source of complication is the encoding of various special characters, e.g. accented vowels
     - It appears that during the many conversions from original documents to wikispace pages to Google Docs to AWS S3 Bucket to Windows files, some of files had their special characters modified, which results in links breaking when, for example, two different encodings of `é` are used.

- Remaining hurdles include:
     - fixing HTML hyperlinks so that they point to the correct file in the new structure
