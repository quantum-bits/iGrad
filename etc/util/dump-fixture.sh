#!/bin/sh

## Dump the contents of the database in a way that's suitable for populating a new
## database right after a syncdb. Mostly just excludes stuff that will be created by the
## syncdb operation itself.

python ./manage.py dumpdata		\
    --indent=4				\
    --exclude=admin.logentry		\
    --exclude=auth.permission		\
    --exclude=contenttypes.contenttype	\
    --exclude=sessions.session
