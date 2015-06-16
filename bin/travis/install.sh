#!/bin/bash
# pwd is the git repo.
set -e

# Before installation, we'll run ``pip wheel``, this will build wheels for
# anything that doesn't already have one on PyPI.
pip wheel -r requirements/compiled.txt
pip wheel -r requirements/dev.txt

echo "Install Python dependencies"
pip install --no-deps -r requirements/compiled.txt
pip install -r requirements/dev.txt

# install the same stuff with peep (slow)
# pip install bin/peep-2.4.1.tar.gz
# peep install -r requirements.txt

echo "Creating a test database"
mysql -e 'create database peekaboo;'
# psql -c 'create database airmozilla;' -U postgres
