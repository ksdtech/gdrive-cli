#!/bin/sh
#
# for devs

find . -name \*.pid -or -name \*.pyc -or -name \*.swp -exec rm -i {} \;
