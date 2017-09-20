#gdrive-cli 

Please see http://tomdignan.com/projects/gdrive-cli for a video introduction.

##ksdtech Enhancements

* TODO: Update to Google Drive v3 API
* TODO: Enable Team Drive support

##Dependencies

    sudo pip install google-api-python-client
    sudo pip install httplib2

##Chrome Application

To use this, you need to register a chrome application. It must be at least installable by you, but need not be published. There is a boilerplate app in the repo you can use to base yours off of. I highly encourage you to take this code and use it to work towards developing useful and profitable chrome apps on the chrome web store!

You *must* publish the chrome app for this to work. It need not be published publically, but you must at least make use of the "publish to test accounts feature" or you will get error 403.

##Installation

1. Visit [http://developers.google.com/drive](http://developers.google.com/drive) and perform all the required steps to publish a chrome app with Google Drive enabled. Don't hestitate to contact me if you have trouble with this, because it is tricky.
2. You must create this chrome app, put it in the chrome web store, and install it in your browser!
3. git clone https://tom-dignan@github.com/tom-dignan/gdrive-cli.git
4. Using the information you got from google, create a $HOME/.gdrive_client_secrets file. Remove the trailing "apps.googleusercontent.com" from the id as well as the prepending word "secret" from the client secret.
5. **./gdrive-cli --init-database** to create your local database. You may remove the ~/.gdrive prefixed files if necessary, but if you remove your client secrets file you should back it up. Removing these files will revoke your ability to list uploaded files permanently, as gdrive-cli relies on a local SQLite database to list files, since files are private to the Google Drive app that creates them. Google Docs supports listings, if you want to write support for that, but I like the speed of local metadata.
6. **./gdrive-cli --authenticate** will open an oauth dialog in your default browser. For official support, you must make chrome your default browser. Click this.
7. You are ready to issue gdrive-cli commands. Have fun. If your session expires, reauthenticate.

##Setting the default browser

gdrive-cli uses python's webbrowser module to find your default browser. You can set the BROWSER environment variable to override this. For more information, see [webbrowser](http://docs.python.org/library/webbrowser.html)

    export BROWSER="google-chrome"

##Client Secrets File

In step 4, you made a client secrets file. This is what it MUST look like:

    {
        "web": {
            "client_id" : "_REDACTED_",
            "client_secret": "_REDACTED_",
            "redirect_uris": ["URIsurn:ietf:wg:oauth:2.0:oob", "http://tomdignan.com/projects/gdrive-cli/"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://accounts.google.com/o/oauth2/token"
        }
    }

* Your client_id must NOT contain "apps.googleusercontent.com"
* Your client_secret must not have the word "secret" prepended to it.

Valid places for this file are, in order

1. $CWD/.private/client_secrets.json
2. $HOME/.gdrive_client_secrets
3. /etc/gdrive-cli

##How to upload a file, show its remote metadata, and then download it.

To upload a file you must have enabled its mime type in the Google API console under Google Drive SDK, and filled out all other fields of this form. You must supply the file extension in the title. For now, just use "none" as the parent id. The code will see "none" and ignore the field.

    gdrive-cli --insert foo.txt "my foo document" none "text/plain" foo.txt
    gdrive-cli --show <hash_that_insert_printed>
    gdrive-cli --download <hash_that_insert_printed>

##Listing files

You can list files with
    
    gdrive-cli --list

##FAQ

Q. Can I use this code to make a FUSE filesystem? 

A. Yes, use fuse-python. There is currently a C project underway as well that you should check out https://github.com/jcline/fuse-google-drive although I am unsure of the status at this time.

Q. Why am I am getting "The authenticated user has not installed the app with client id” error?

A. [Read my answer on Stack Overflow](http://stackoverflow.com/questions/10345904/why-am-i-getting-the-authenticated-user-has-not-installed-the-app-with-client-i/10352692#10352692)

##Credits

###Patch Contributors

* [Chris Knutson](https://github.com/Canuteson/)

###Packagers

Thanks to

* [Daniel Wallace](http://code.gtmanfred.com) aka gtmanfred for being the first to install gdrive-cli and creating a package for arch linux's AUR.

##Support

Live support in #gdrive-cli on irc.freenode.net and development discussion! You *may* have to idle a bit.

##Known Issues

* UTF-8 files might not work for --insert [see this stackoverflow post](http://stackoverflow.com/questions/10372370/when-attempting-to-upload-a-utf-8-text-file-to-google-drive-with-the-google-api) and this [bug report](http://code.google.com/p/google-api-python-client/issues/detail?id=131&thanks=131&ts=1335708962)
