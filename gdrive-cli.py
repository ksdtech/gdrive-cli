#!/usr/bin/env python
"""
Copyright 2012 Thomas Dignan <tom@tomdignan.com>

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

gdrive-cli.py command line google drive client.

Author: Tom Dignan <tom.dignan@gmail.com>
Date: Fri Apr 27 16:00:35 EDT 2012
Official Docs: https://developers.google.com/drive/
"""

import argparse
from oauth import simple_cli
from gdrive import gdrive
from os import getenv
import pickle
from db import helper as dbhelper
from db import schema as dbschema

def get_stored_credentials_path():
    home = getenv("HOME")

    # windows compat
    if home is None:
        home = getenv("HOMEPATH")

    return home + "/.gdrive_oauth"

def get_service_object():
    credentials = get_stored_credentials()
    return gdrive.build_service(credentials)

def store_credentials():
    credentials = simple_cli.authenticate()
    pickled_creds_path = get_stored_credentials_path()
    pickle.dump(credentials, open(pickled_creds_path, "wb"))

def authenticate():
    store_credentials()

def get_stored_credentials():
    pickled_creds_path = get_stored_credentials_path()
    return pickle.load(open(pickled_creds_path, "rb"))

def make_argparser():
    """
    ArgumentParser factory 
    """
    parser = argparse.ArgumentParser(description="gdrive-cli: google drive interface",
        epilog="Author: Tom Dignan <tom.dignan@gmail.com>")

    parser.add_argument("--init-database", help="must be run after install once to initialize the user local database", action="store_true")

    parser.add_argument("--authenticate", help="must be done before using other methods", action="store_true")

    parser.add_argument("--show", help="show file metadata", metavar="<file_id>")

#    parser.add_argument("--easy-upload", help="like insert, but easier", metavar=("<file_name>", "<mime_type"))

    parser.add_argument("--list", help="list application's files (uses local database)", action="store_true")

    parser.add_argument("--download", help="download file contents and print to stdout", metavar="<drive_file>")

    parser.add_argument("--insert", help="insert new file", nargs=5,
            metavar=("<title -- must include file ext>", "<description>", "<parent_id (if none, pass none)>", "<mime_type>", "<filename>"))

    parser.add_argument("--rename", help="rename a file", nargs=2,
            metavar=("<file_id>", "<new_title>"))

    parser.add_argument("--easy-rename", help="rename a file by name", nargs=2,
            metavar=("<original_name>", "<new_name>"))

    parser.add_argument("--update", help="update a file", nargs=6,
            metavar=("<file_id>", "<new_title>", "<new_description>", "<new_mime_type>",
                "<new_filename>", "<new_revision>"))

    return parser

def handle_args(args):
    if args.authenticate is True:
        handle_authenticate()
    elif args.list is True:
        handle_list()
    elif args.show is not None:
        handle_show(args.show)
    elif args.download is not None:
        handle_download(args.download)
    elif args.insert is not None:
        handle_insert(args.insert)
    elif args.rename is not None:
        handle_rename(args.rename)
    elif args.update is not None:
        handle_update(args.update)
    elif args.init_database is True:
        handle_init_database()
    elif args.easy_rename is not None:
        handle_easy_rename(args.easy_rename)

def handle_authenticate():
    authenticate()

def handle_show(file_id):
    service = get_service_object()
    gdrive.print_file(service, file_id)

def handle_download(file_id):
    service = get_service_object()
    download = gdrive.download_file_by_id(service, file_id)
    print download

def handle_insert(args):
    service = get_service_object()

    title = args[0]
    description = args[1]
    parent_id = args[2]

    if parent_id == "none":
        parent_id = None

    mime_type = args[3]
    filename = args[4]

    file = gdrive.insert_file(service, title, description, parent_id, mime_type,
            filename)

    id = dbhelper.insert_file(file)
    print "Inserted file ", id

def handle_list():
    files = dbhelper.select_all_files()
    print "filename\t\t\tid"
    for f in files:
        print "%(title)s\t\t%(id)s" % { "title" : f[0], "id" : f[1] }

def rename_file(file_id, new_name):
    service = get_service_object()
    gdrive.rename_file(service, file_id, new_name)
    dbhelper.rename_file(file_id, new_name)
    print "renamed %(file_id)s to %(new_name)s" % {"file_id" :
            file_id, "new_name" : new_name }

def handle_rename(args):
    file_id = args[0]
    new_name = args[1]
    rename_file(file_id, new_name)

def handle_easy_rename(args):
    service = get_service_object()
    old_name = args[0]
    new_name = args[1]
    
    old_id = dbhelper.get_file_id_by_name(old_name)

    if old_id is None:
        print "Unknown file: %s" % old_name
        return

    rename_file(old_id, new_name)

def handle_update(args):
    service = get_service_object()

    file_id = args[0]
    new_title = args[1]
    new_description = args[2]
    new_mime_type = args[3]
    new_filename = args[4]
    new_revision = args[5]

    if new_revision == "false":
        new_revision = False
    else:
        new_revision = True
        

    file = gdrive.update_file(service, file_id, new_title, new_description, new_mime_type, new_filename, new_revision)

    id = dbhelper.update_file(file)
    print "Updated file ", id

def handle_init_database():
    print "Creating database..."
    dbschema.create_schema()
    print "done."


if __name__ == "__main__":
    parser = make_argparser()
    args = parser.parse_args()
    handle_args(args)



