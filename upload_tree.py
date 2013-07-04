#!/usr/bin/python

from __future__ import print_function
from oauth import simple_cli
from gdrive import gdrive
import mimetypes
import os
import pickle
import random
import re
import sys
import time

# A collection of file extensions we did not have mimetypes for
missing = { }

# A list of extensions that will be mapped to 'text/plain'
# Unknown file extensions will be mapped to 'application/octect-stream'
plain_texts = ['.cs', '.m', '.php', '.properties', '.rb', '.yaml', '.yml']

def init_mimetypes():
    mimetypes.add_type('application/gzip', '.gz', True)
    mimetypes.add_type('application/vnd.apple.pages', '.pages', True)  
    mimetypes.add_type('application/vnd.apple.keynote', '.key', True)  
    mimetypes.add_type('application/vnd.apple.numbers', '.numbers', True) 
    mimetypes.add_type('application/clarisworks', '.cwk', True)
    mimetypes.add_type('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', '.xlsx', True)
    mimetypes.add_type('application/vnd.openxmlformats-officedocument.spreadsheetml.template', '.xltx', True)
    mimetypes.add_type('application/vnd.openxmlformats-officedocument.presentationml.template', '.potx', True)
    mimetypes.add_type('application/vnd.openxmlformats-officedocument.presentationml.slideshow', '.ppsx', True)
    mimetypes.add_type('application/vnd.openxmlformats-officedocument.presentationml.presentation', '.pptx', True)
    mimetypes.add_type('application/vnd.openxmlformats-officedocument.presentationml.slide', '.sldx', True)
    mimetypes.add_type('application/vnd.openxmlformats-officedocument.wordprocessingml.document', '.docx', True)
    mimetypes.add_type('application/vnd.openxmlformats-officedocument.wordprocessingml.template', '.dotx', True)
    mimetypes.add_type('application/vnd.ms-excel.addin.macroEnabled.12', '.xlam', True)
    mimetypes.add_type('application/vnd.ms-excel.sheet.binary.macroEnabled.12', '.xlsb', True)
    mimetypes.add_type('text/x-markdown', '.md', True)  
    for ext in plain_texts:
        mimetypes.add_type('text/plain', ext, True)  

# Debugging information post-mortem
def dump_missing_mimetypes():
    for ext in missing:
        print("No mimetype mapped to", ext, "for", missing[ext], file=sys.stderr)

# The GDrive mimetype for a folder
def get_folder_mimetype():
    return 'application/vnd.google-apps.folder'

# Use extensions or guess mimetypes
def get_file_mimetype(file_path):
    base, ext = os.path.splitext(file_path)
    mt = None
    if ext:
        ext = ext.lower()
    try:
        mt = mimetypes.types_map[ext]
    except KeyError as e:
        missing[ext] = file_path
    if mt is None:
        mt, enc = mimetypes.guess_type(file_path, False)
    return mt
  
# Change ':' to '/' in file/folder titles
def map_mac_filename(filename):
    return re.sub(r'\:', "/", filename)

def get_stored_credentials_path():
    home = os.getenv("HOME")

    # windows compat
    if home is None:
        home = os.getenv("HOMEPATH")

    return home + "/.gdrive_oauth"

def get_service_object():
    credentials = get_stored_credentials()
    return gdrive.build_service(credentials)

def store_credentials(scopes):
    credentials = simple_cli.authenticate(scopes)
    pickled_creds_path = get_stored_credentials_path()
    pickle.dump(credentials, open(pickled_creds_path, "wb"))

def authenticate(scopes=None):
    store_credentials(scopes)

def get_stored_credentials():
    pickled_creds_path = get_stored_credentials_path()
    return pickle.load(open(pickled_creds_path, "rb"))
    
def rate_limited_create_folder(service, title, parent=None):
    folder_id = None
    for retries in range(5):
        folder, code, reason = gdrive.insert_folder(service, title, "", parent)
        if folder:
            return folder['id']
        if not gdrive.is_rate_limited_error(code, reason):
            break
        # Apply exponential backoff.
        wait = (2 ** retries) + random.randint(0, 1000) / 1000.
        print("retrying after %f" % wait)
        time.sleep(wait)
    return None

def rate_limited_create_file(service, title, description, parent_id, mime_type, filename):
    file_id = None
    for retries in range(5):
        file, code, reason = gdrive.insert_file(service, title, description, parent_id, mime_type, filename)
        if file:
            return file['id']
        if not gdrive.is_rate_limited_error(code, reason):
            break
        # Apply exponential backoff.
        wait = (2 ** retries) + random.randint(0, 1000) / 1000.
        print("retrying after %f" % wait)
        time.sleep(wait)
    return None
    
def find_or_create_folder(service, title, parent=None):
    folder_id = None
    folder, code, reason = gdrive.find_folder(service, title, parent)
    if folder:
        folder_id = folder['id']
        print("found folder:", title, "id:", folder_id, "in parent", parent)
    else:
        folder_id = rate_limited_create_folder(service, title, parent)
        if folder_id:
            print("created folder:", title, "id:", folder_id, "in parent", parent)
        else:
            print("failed to create folder:", title, "in parent", parent)
    return folder_id

# Walk a file tree and upload folders and files to new
# destination in GDrive.  Requires full access to GDrive
# scope ('https://www.googleapis.com/auth/drive')
def upload_tree(service, rootdir, destroot):
    init_mimetypes()
    path_mapping = { }
    title = map_mac_filename(destroot)
    root_folder_id = find_or_create_folder(service, title)
    path_mapping[rootdir] = root_folder_id
    print("root", destroot, "id:", root_folder_id)
    for folder, subs, files in os.walk(rootdir):
        parent, title = os.path.split(folder)
        if title[0] == ".":
            continue
            
        parent_id = None
        try:
            parent_id = path_mapping[folder]
        except KeyError:
            pass
        if parent_id:
            print("in folder:", folder)
        else:
            grandparent_id = None
            try:
                grandparent_id = path_mapping[parent]
            except KeyError:
                print("no path mapping for", folder)
                raise
            title = map_mac_filename(title)
            parent_id = find_or_create_folder(service, title, grandparent_id)
            if parent_id:
                path_mapping[folder] = parent_id

        for dirname in subs:
            folder_path = os.path.join(folder, dirname)
            if dirname[0] == ".":
                subs.remove(dirname)
            else:
                title = map_mac_filename(dirname)
                folder_id = find_or_create_folder(service, title, parent_id)
                if folder_id:
                    path_mapping[folder_path] = folder_id

        for filename in files:
            if filename[0] != ".":
                file_path = os.path.join(folder, filename)
                mt = get_file_mimetype(file_path)
                if mt is None:
                    print("no mime type for", file_path, "; using octet-stream")
                    mt = 'application/octet-stream'
                title = map_mac_filename(filename)
                new_file_id = rate_limited_create_file(service, title, "", parent_id, mt, file_path)
                if new_file_id:
                    print("created file:", title, "in parent", parent_id)
                else:
                    print("failed to create file", title, "in parent", parent_id)
    # dump_missing_mimetypes()

if __name__ == "__main__":
    authenticate('https://www.googleapis.com/auth/drive')
    service = get_service_object()
    upload_tree(service, '/Users/pz/Desktop/Test', 'Shared Folder')
