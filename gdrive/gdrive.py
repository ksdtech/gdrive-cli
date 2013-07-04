from apiclient import errors
from apiclient.discovery import build
from apiclient.http import MediaFileUpload
import cgi
import httplib2
import os
import simplejson
import sys
import traceback

"""
Google Drive python module. The code in this file is taken directly from
Google's API reference.

https://developers.google.com/drive/v1/reference/

ALL CODE IN THIS FILE IS A DERIVED WORK OF THE SDK EXAMPLE CODE.

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
"""

################################################################################
# Service Object (do this first)                                                                                             #
################################################################################

def build_service(credentials):
    """Build a Drive service object.

    Args:
        credentials: OAuth 2.0 credentials.

    Returns:
        Drive service object.
    """
    http = httplib2.Http()
    http = credentials.authorize(http)
    return build('drive', 'v2', http=http)

################################################################################
# Error handling: we re-raise errors that can be retried
# See https://developers.google.com/drive/handle-errors                                                                                                                         #
################################################################################

def is_rate_limited_error(code, reason):
    return (code == 403 or code == 503) and reason in ['rateLimitExceeded', 'userRateLimitExceeded']
    
def http_error_tuple(rv, content):
    print 'An error occurred: %s' % content
    try:
        # differs from documentation, possibly changed in v2
        error = simplejson.loads(content).get('error')
        code = error.get('code')
        first_error = error.get('errors')[0]
        reason = first_error.get('reason')
        return (rv, code, reason)
    except:
        print "problem parsing http error"
        traceback.print_exc(file=sys.stdout)
    return (rv, 500, 'parseError')

################################################################################
# Files: get                                                                                                                                     #
################################################################################

def print_file(service, file_id):
    """Print a file's metadata.

    Args:
        service: Drive API service instance.
        file_id: ID of the file to print metadata for.
    """
    try:
        file = service.files().get(fileId=file_id).execute()

        print 'Title: %s' % file['title']
        print 'Description: %s' % file['description']
        print 'MIME type: %s' % file['mimeType']
        return (True, 200, '')
    except errors.HttpError, error:
        return http_error_tuple(False, error.content)

def get_file_instance(service, file_id):
    """Print a file's metadata.

    Args:
        service: Drive API service instance.
        file_id: ID of the file to print metadata for.

    Returns:
        file instance or None
    """
    try:
        file = service.files().get(fileId=file_id).execute()
        return (file, 200, '')
    except errors.HttpError, error:
        print "error %s" % error
        return http_error_tuple(None, error.content)
        
def query_escape(s):
    return s.replace("'", "\\'")

def find_file(service, title, parent=None):
    query = "mimeType != 'application/vnd.google-apps.folder' and title = '%s'" % query_escape(title)
    if parent:
        query += (" and '%s' in parents" % parent)
    param = { }
    param['q'] = query
    param['maxResults'] = 10
    try:
        files = service.files().list(**param).execute()
        for file in files['items']:
            return (file, 200, '')
        return (None, 404, 'notFound')
    except errors.HttpError, error:
        return http_error_tuple(None, error.content)

def find_folder(service, title, parent=None):
    query = "mimeType = 'application/vnd.google-apps.folder' and title = '%s'" % query_escape(title)
    if parent:
        query += (" and '%s' in parents" % parent)
    param = { }
    param['q'] = query
    param['maxResults'] = 10
    try:
        files = service.files().list(**param).execute()
        for folder in files['items']:
            return (folder, 200, '')
        return (None, 404, 'notFound')
    except errors.HttpError, error:
        return http_error_tuple(None, error.content)

def download_file_by_id(service, file_id):
    """
    Download file content by id
    """
    drive_file, reason, code = get_file_instance(service, file_id)
    if drive_file:
        return download_file(service, drive_file)
    return (None, reason, code)

def download_file(service, drive_file):
    """Download a file's content.

    Args:
        service: Drive API service instance.
        drive_file: Drive File instance.

    Returns:
        File's content if successful, None otherwise.
    """
    download_url = drive_file.get('downloadUrl')
    if download_url:
        resp, content = service._http.request(download_url)
        print 'Status: %s' % resp
        if resp.status == 200:
            return (content, 200, '')
        else:
            return (None, resp.status, repr(resp))
    # The file doesn't have any content stored on Drive.
    return (None, 200, '')

################################################################################
# Files: insert                                                                                                                                #
################################################################################

def insert_file(service, title, description, parent_id, mime_type, filename):
    """Insert new file.

    Args:
        service: Drive API service instance.
        title: Title of the file to insert, including the extension.
        description: Description of the file to insert.
        parent_id: Parent folder's ID.
        mime_type: MIME type of the file to insert.
        filename: Filename of the file to insert.
    Returns:
        Inserted file metadata if successful, None otherwise.
    """
    if os.path.getsize(filename) > 5*2**20:
        media_body = MediaFileUpload(filename, mimetype=mime_type, chunksize=1024*1024, resumable=True)
    else:
        media_body = MediaFileUpload(filename, mimetype=mime_type)
    body = {
        'title': title,
        'description': description,
        'mimeType': mime_type
    }

    # Set the parent folder.
    if parent_id:
        body['parents'] = [{'id': parent_id}]

    try:
        file = service.files().insert(
                body=body,
                media_body=media_body).execute()

        # Uncomment the following line to print the File ID
        # print 'File ID: %s' % file['id']

        return (file, 200, '')
    except errors.HttpError, error:
        return http_error_tuple(None, error.content)


################################################################################
# Files: insert                                                                                                                                #
################################################################################

def insert_folder(service, title, description, parent_id):
    """Insert new folder.

    Args:
        service: Drive API service instance.
        title: Title of the folder to insert, including the extension.
        description: Description of the folder to insert.
        parent_id: Parent folder's ID.
    Returns:
        Inserted folder metadata if successful, None otherwise.
    """
    body = {
        'title': title,
        'description': description,
        'mimeType': 'application/vnd.google-apps.folder'
    }

    # Set the parent folder.
    if parent_id:
        body['parents'] = [{'id': parent_id}]

    try:
        folder = service.files().insert(
                body=body).execute()

        # Uncomment the following line to print the Folder ID
        # print 'Folder ID: %s' % folder['id']

        return (folder, 200, '')
    except errors.HttpError, error:
        return http_error_tuple(None, error.content)


################################################################################
# Files: patch                                                                                                                                #
################################################################################

def rename_file(service, file_id, new_title):
    """Rename a file.

    Args:
        service: Drive API service instance.
        file_id: ID of the file to rename.
        new_title: New title for the file.
    Returns:
        Updated file metadata if successful, None otherwise.
    """
    try:
        file = {'title': new_title}

        # Rename the file.
        updated_file = service.files().patch(
                fileId=file_id,
                body=file,
                fields='title').execute()

        return (updated_file, 200, '')
    except errors.HttpError, error:
        return http_error_tuple(None, error.content)

################################################################################
# Files: delete                                                                                                                                #
################################################################################

def delete_file_by_id(service, file_id):
    """Delete a file.

    Args:
        service: Drive API Service instance.
        file_id: ID of the file to delete.
    Returns:
        Success status message if successful, None otherwise.
    """
    try:
        delete_file = service.files().delete(
            fileId=file_id).execute()

        return (file_id, 200, '')
    except errors.HttpError, error:
        return http_error_tuple(None, error.content)
        


################################################################################
# Files: update                                                                                                                                #
################################################################################

def update_file(service, file_id, new_title, new_description, new_mime_type,
                                new_filename, new_revision):
    """Update an existing file's metadata and content.

    Args:
        service: Drive API service instance.
        file_id: ID of the file to update.
        new_title: New title for the file.
        new_description: New description for the file.
        new_mime_type: New MIME type for the file.
        new_filename: Filename of the new content to upload.
        new_revision: Whether or not to create a new revision for this file.
    Returns:
        Updated file metadata if successful, None otherwise.
    """
    try:
        # First retrieve the file from the API.
        file = service.files().get(fileId=file_id).execute()

        # File's new metadata.
        file['title'] = new_title
        file['description'] = new_description
        file['mimeType'] = new_mime_type

        # File's new content.
        if os.path.getsize(new_filename) > 5*2**20:
            media_body = MediaFileUpload(new_filename, mimetype=new_mime_type, chunksize=1024*1024, resumable=True)
        else:
            media_body = MediaFileUpload(new_filename, mimetype=new_mime_type, resumable=False)

        # Send the request to the API.
        updated_file = service.files().update(
                fileId=file_id,
                body=file,
                newRevision=new_revision,
                media_body=media_body).execute()
        return (updated_file, 200, '')
    except errors.HttpError, error:
        return http_error_tuple(None, error.content)
