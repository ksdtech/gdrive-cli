#!/bin/sh
# for users and devs

echo "warning, choosing yes will delete your gdrive data..."

rm -i ${HOME}/.gdrive-cli.db
rm -i ${HOME}/.gdrivefs.dat
rm -i ${HOME}/.gdrive_oauth
