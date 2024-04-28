# Python version: 3.11.8

import os
import os.path
import re
from bs4 import BeautifulSoup # you can just `pip install bs4` i guess

def list_html_files(directory):
    file_list = []
    for root, _, files in os.walk(directory):
        for f in files:
            if os.path.splitext(f)[1] == '.html':
                file_list.append(os.path.join(root, f))
    return file_list

def main():
    # please run this file from the directory which contains all the HTML files
    # (possibly within subfolders) you want to modify.

    ROOT_DIR = os.getcwd()

    # a list of files to modify.
    # in theory you could derive this by grepping for flickr links.
    # in practice to be safe I'm just going to check every HTML file in the repo.
    plan = list_html_files(ROOT_DIR)

    albums = {}

    for f in plan:
        with open(f, 'r') as fo:
            print(f)

            soup = BeautifulSoup(fo, 'html.parser')

            # look for flickr anchors that have the special embedding method
            anchors_with_embed = soup.find_all('a', href=re.compile('flickr'), attrs={'data-flickr-embed': 'true'})
            for anchor in anchors_with_embed:
                # look for the img tag associated with the anchor
                img = anchor.img
                assert img['alt'] == anchor['title']

                # look for the script tag associated with the anchor, and destroy it.
                script = anchor.next_sibling
                assert script.name == 'script'
                assert script['src'] == '//embedr.flickr.com/assets/client-code.js'
                script.decompose()

                if '/in/album' in anchor['href']:
                    album_id = anchor['href'].split('/in/album-')[1] # does this work?
                else:
                    album_id = None

                img_id = img['alt']
                new_link = 'https://backupmakingandknowing.s3.amazonaws.com/Flickr+Public/My+Photostream/' + img_id

                # modify the anchor to use the AWS link
                #anchor.href = new_link

                # modify the img to use the AWS link
                img.src = new_link
                
                # save the album id, if any.
                #
                # NOTE: this is sort of lossy. While we do save the association
                # of an image to an album, we are not recording which
                # *instance* of the image in the document carries the album
                # info. It is fathomable that the same image may be linked in
                # multiple places, with album info in some places and not in
                # others.  In order to make it possible to recover the exact
                # img/anchor tag which has the info, we save the filename, and
                # we save it even when there is no album ID - so in theory you
                # can look up the file and look sequentially through the
                # anchors as we have done here to locate the exact tag.
                if img_id in albums:
                    albums[img].append((f, album_id))
                else:
                    albums[img] = [(f, album_id)]

                print(anchor)

            # look for remaining flickr anchors
            anchors = soup.find_all('a', href=re.compile("flickr"))
            print(anchors)
            # TODO

            # handle remaining flickr images
            imgs = soup.find_all('img', src=re.compile("flickr"))
            print(imgs)
            # TODO

if __name__ == "__main__":
    main()
