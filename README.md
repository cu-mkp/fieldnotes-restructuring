# fieldnotes
Various tasks and records regarding the Making and Knowing Project's fieldnotes produced as part of Project courses and activities of hands-on skillbuilding and historical reconstructions.

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
- This has been dones through GREG_CODE
     - It uses the page that contained the information from the wiki side navigation bar to recursively find the linked pages from Semester+Year down
     - This results in BLAH
     - If there are any broken links, they are compiled in a single ERRORS-CSV which can be used to manually correct the links (by looking at context)
