#gdrive-cli 

Please see http://tomdignan.com/projects/gdrive-cli for a video introduction.

##Dependencies

sudo pip install google-api-python-client
sudo pip install httplib2

##Installation

1. Visit [http://developers.google.com/drive](http://developers.google.com/drive) and perform all the required steps to publish a chrome app with Google Drive enabled. Don't hestitate to contact me if you have trouble with this, because it is tricky.
2. You must create this chrome app, put it in the chrome web store, and install it in your browser!
3. git clone git@github.com:tom-dignan/gdrive-cli
4. Using the information you got from google, create a $HOME/.gdrive_client_secrets file. Remove the trailing "apps.googleusercontent.com" from the id as well as the prepending word "secret" from the client secret.
5. ./gdrive-cli --init-database to create your local database. You may remove the ~/.gdrive prefixed files if necessary, but if you remove your client secrets file you should back it up. Removing these files will revoke your ability to list uploaded files permanently, as gdrive-cli relies on a local SQLite database to list files, since files are private to the Google Drive app that creates them. Google Docs supports listings, if you want to write support for that, but I like the speed of local metadata.
6. ./gdrive-cli --authenticate will open an oauth dialog in your default browser. For official support, you must make chrome your default browser. Click this.
7. You are ready to issue gdrive-cli commands. Have fun. If your session expires, reauthenticate.

##How to upload a file. Show its remote metadata, and then download it.

To upload a file you must have enabled its mime type in the Google API console under Google Drive SDK, and filled out all other fields of this form. You must supply the file extension in the title. For now, just use "none" as the parent id. The code will see "none" and ignore the field.

    gdrive --insert foo.txt "my foo document" none "text/plain" foo.txt
    gdrive --show <hash_that_insert_printed>
    gdrive --download <hash_that_insert_printed>

##Listing files

You can list files with
    
    gdrive --list

##TODO

The following features need to be implemented

   --rename
   --update

##FAQ

Q. Can I use this code to make a FUSE filesystem? 

A. Yes, use fuse-python. There is currently a C project underway as well that you should check out https://github.com/jcline/fuse-google-drive although I am unsure of the status at this time.


