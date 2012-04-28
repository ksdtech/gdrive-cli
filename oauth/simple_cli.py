""" Copyright 2012 Thomas Dignan <tom@tomdignan.com>

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
import httplib2
from apiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run
from pprint import pprint
import os
import sys

home = os.getenv("HOME")

global_location = "/etc/gdrive-client"
local_location = home + "/.gdrive_client_secrets"
test_location = ".private/client_secrets.json"

if os.path.isfile(test_location):
    client_secrets_location = test_location
elif os.path.isfile(local_location):
    client_secrets_location = local_location
elif os.path.isfile(global_location):
    client_secrets_location = global_location
else:
    print "No client_secrets.json file was found! Exiting."
    sys.exit(1)

SCOPES = [
        'https://www.googleapis.com/auth/drive.file',
        'https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/userinfo.profile',
]

def authenticate():
    """
    Authenticates and returns OAuth2 credentials.

    Warning, this launches a web browser! You will need to click.
    """
    storage_path = home + "/.gdrivefs.dat"
    storage = Storage(storage_path)
    flow = flow_from_clientsecrets(client_secrets_location, ' '.join(SCOPES))
    credentials = run(flow, storage)
    return credentials

