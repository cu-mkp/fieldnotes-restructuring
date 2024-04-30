# Python version: 3.11.8

import sys
import os
import os.path
import re
import json
from bs4 import BeautifulSoup # you can just `pip install bs4` i guess
import requests

def list_html_files(directory):
    file_list = []
    for root, _, files in os.walk(directory):
        for f in files:
            if os.path.splitext(f)[1] == '.html':
                file_list.append(os.path.join(root, f))
    return file_list

def flickr_photo_getInfo(photo_id):
    key = os.environ['FLICKR_API_KEY']
    api_prefix = 'https://www.flickr.com/services/rest/?format=json&nojsoncallback=1&method='
    method = 'flickr.photos.getInfo'
    url = api_prefix + method + '&api_key=' + key + '&photo_id=' + photo_id

    print("GET " + photo_id)
    r = requests.get(url)
    assert r.status_code == 200, r.headers
    raw_json = r.json()
    if raw_json['stat'] != 'ok':
        print("Error in GET request to photo:", photo_id, file=sys.stderr)
        print(raw_json['stat'], file=sys.stderr)
        print(raw_json, file=sys.stderr)
        return None
    data = r.json()['photo']

    result = {}
    result['request'] = url

    result['title'] = data['title']['_content']
    result['s3_object_name'] = data['title']['_content']
    result['original_format'] = data['originalformat']

    media_type = data['media']
    result['media_type'] = media_type
    if media_type == 'video':
        result['width'] = data['video']['width']
        result['height'] = data['video']['height']

    # You would think we should do the following to make sure we have the right extension for S3:
    #
    #     elif media_type == 'photo' and not result['title'].endswith(result['original_format']):
    #         result['object_name'] = result['title'] + '.' + result['original_format']
    #
    # In fact, it looks like the s3 object name always has a jpg extension, for some reason.
    # So we insist it always has a jpg extension.
    #
    # on the one hand, I hate this because what the f*ck. On the other hand,
    # this makes it really easy to discern the object name.
    #
    # I would do .endswith() but there's some weird cases...
    if '.jpg' not in result['s3_object_name']:
        result['s3_object_name'] = result['title'] + '.jpg'

    return result

def flickr_photoset_getInfo(photoset_id, user_id):
    # photoset is the internal name of album
    key = os.environ['FLICKR_API_KEY']
    api_prefix = 'https://www.flickr.com/services/rest/?format=json&nojsoncallback=1&method='
    method = 'flickr.photosets.getInfo'
    url = api_prefix + method + '&api_key=' + key + '&photoset_id=' + photoset_id + '&user_id=' + user_id

    r = requests.get(url)
    assert r.status_code == 200, r.headers
    raw_json = r.json()
    if raw_json['stat'] != 'ok':
        print("Error in GET request to photoset:", photoset_id, file=sys.stderr)
        print(raw_json['stat'], file=sys.stderr)
        print(raw_json, file=sys.stderr)
        return None
    data = r.json()['photoset']

    title = data['title']['_content']

    return title

def main(dry_run=True):
    fix_tags(dry_run=dry_run)

def record_tag_flickr_data():
    # please run this file from the directory which contains all the HTML files
    # (possibly within subfolders) you want to modify.
    ROOT_DIR = os.getcwd()

    # a list of files to modify.
    # in theory you could derive this by grepping for flickr links.
    # in practice to be safe I'm just going to check every HTML file in the repo.
    plan = list_html_files(ROOT_DIR)

    albums = {}
    exceptions = []
    missing = []
    rewrites = {}

    for f in plan:
        rewrites[f] = {}

        with open(f, 'r') as fo:
            print(f)

            soup = BeautifulSoup(fo, 'html.parser')

            # look for flickr anchors that have the special embedding method
            anchors_with_embed = soup.find_all('a', href=re.compile(r'flickr.com/photos/[^/]+/\d+/'), attrs={'data-flickr-embed': 'true'})
            n_embed = len(anchors_with_embed)
            for anchor in anchors_with_embed:
                # look for the img tag associated with the anchor
                img = anchor.img
                assert img['alt'] == anchor['title']

                print(anchor['href'])
                album_id = match.group(1) if (match := re.search('/in/album-([^/]+)', anchor['href'])) else None
                user_id = re.search('flickr.com/photos/([^/]+)', anchor['href']).group(1)
                photo_id = re.search('flickr.com/photos/[^/]+/([^/]+)', anchor['href']).group(1)

                album_title = None if album_id == None else flickr_photoset_getInfo(album_id, user_id)
                subfolder = 'My+Photostream' if album_title == None else 'Albums/' + album_title

                data = flickr_photo_getInfo(photo_id)
                if data == None:
                    missing.append({'file'        : f,
                                    'photo_id'    : photo_id,
                                    'title'       : anchor['title'],
                                    'flickr_url'  : anchor['href'],
                                    'album_id'    : album_id,
                                    'album_title' : album_title})
                    continue

                title = data['title']
                s3_object_name = data['s3_object_name']

                new_link = 'https://backupmakingandknowing.s3.amazonaws.com/Flickr+Public/' + subfolder + '/' + s3_object_name
                r = requests.get(new_link)
                assert r.status_code == 200, f'file {f}: could not locate object:\n  {s3_object_name}\nfrom flickr url:\n  {anchor["href"]}\nat s3 url:\n  {new_link}\nGot response code: {str(r.status_code)}.\nDebug request:\n  {data["request"]}'

                # look for the script tag associated with the anchor, and destroy it.
                script = anchor.next_element
                assert script.name == 'script', f
                assert script['src'] == '//embedr.flickr.com/assets/client-code.js'
                
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
                v = {'file': f, 'album_id': album_id, 'album_title': album_title}
                if photo_id not in albums:
                    albums[photo_id] = []
                albums[photo_id].append(v)

                # save all this info to a JSON
                rewrites[f][photo_id] = { 'photo_id': photo_id
                                        , 'title': anchor['title']
                                        , 'flickr_url': anchor['href']
                                        , 's3_url': new_link
                                        , 'original_format': data['original_format']
                                        , 'album_id': album_id
                                        , 'album_title': album_title
                                        , 'media_type': data['media_type']
                                        }

            # look for remaining flickr anchors
            anchors = soup.find_all('a', href=re.compile("flickr"))
            n_anchors = len(anchors)
            print("Non-embedded anchors with flickr links:", n_anchors - n_embed)

            # handle remaining flickr images
            imgs = soup.find_all('img', src=re.compile("flickr"))
            if imgs != []:
                exceptions.append({'file': f, 'imgs': list(map(str, imgs))})
            print("img tags with flickr links:", len(imgs))

    # debug info
    debug_folder = '../../fieldnotes-restructuring/archive-flickr-links'

    # write missing
    missing_debug_file = os.path.join(debug_folder, 'missing.json')
    with open(missing_debug_file, 'w') as f:
        json.dump(missing, f, ensure_ascii=False, indent=4)

    # write rewrite log
    rewrites_debug_file = os.path.join(debug_folder, 'rewrites.json')
    with open(rewrites_debug_file, 'w') as f:
        json.dump(rewrites, f, ensure_ascii=False, indent=4)

    # write exceptions
    exceptions_debug_file = os.path.join(debug_folder, 'exceptions.json')
    with open(exceptions_debug_file, 'w') as f:
        json.dump(exceptions, f, ensure_ascii=False, indent=4)

    # write albums
    albums_debug_file = os.path.join(debug_folder, 'albums.json')
    with open(albums_debug_file, 'w') as f:
        json.dump(albums, f, ensure_ascii=False, indent=4)

def fix_tags(dry_run=True):
    # please run this file from the directory which contains all the HTML files
    # (possibly within subfolders) you want to modify.

    ROOT_DIR = os.getcwd()

    # a list of files to modify.
    # in theory you could derive this by grepping for flickr links.
    # in practice to be safe I'm just going to check every HTML file in the repo.
    plan = list_html_files(ROOT_DIR)

    # json info
    json_folder = '../../fieldnotes-restructuring/archive-flickr-links'

    # write rewrite log
    rewrites_json_file = os.path.join(json_folder, 'rewrites.json')
    with open(rewrites_json_file, 'r') as f:
        rewrites = json.load(f)

    for f in plan:
        with open(f, 'r') as fo:
            soup = BeautifulSoup(fo, 'html.parser')

            # look for flickr anchors that have the special embedding method
            anchors_with_embed = soup.find_all('a', href=re.compile(r'flickr.com/photos/[^/]+/\d+/'), attrs={'data-flickr-embed': 'true'})
            for anchor in anchors_with_embed:
                # look for the img tag associated with the anchor
                img = anchor.img
                assert img['alt'] == anchor['title']

                album_id = match.group(1) if (match := re.search('/in/album-([^/]+)', anchor['href'])) else None
                user_id = re.search('flickr.com/photos/([^/]+)', anchor['href']).group(1)
                photo_id = re.search('flickr.com/photos/[^/]+/([^/]+)', anchor['href']).group(1)

                data = rewrites[f].get(photo_id)
                if data == None:
                    continue

                s3_url = data['s3_url']

                # if it's a video, change it to a video. otherwise just change the src.
                if data['media_type'] == 'video':
                    img.name = 'video'
                    del img['alt']
                    del img['src']
                    img['controls'] = None
                    #img['width'] = data['width']
                    #img['height'] = data['height']
                    src = soup.new_tag('source')
                    src['src'] = s3_url
                    img.append(src)
                    img.append('Your browser does not support the video tag.')
                else:
                    # modify the img to use the AWS link
                    img['src'] = s3_url

                del anchor['data-flicker-embed']

                # look for the script tag associated with the anchor, and destroy it.
                script = anchor.parent.script
                assert script.name == 'script', anchor.parent
                assert script['src'] == '//embedr.flickr.com/assets/client-code.js'
                script.decompose()

        # write the file
        if not dry_run:
            with open(f, 'wb') as fo:
                fo.write(soup.prettify('utf-8'))

if __name__ == "__main__":

    dry_run = any(map(lambda x: x in ['-d', '--dry-run'], sys.argv))
    if any(map(lambda x: x in ['-h', '--help'], sys.argv)):
        print(f"""Usage: {sys.argv[0]} [-d] [-h]

    -h, --help        display this message
    -d, --dry-run     do not write any files""")
        sys.exit(0)

    if dry_run:
        print("This is a dry run. No files will be written.")

    main(dry_run=dry_run)
