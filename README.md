Peek-a-boo
==========

Peek-a-boo! Who's visiting a Mozilla office?

Production environment: https://peekaboo.mozilla.org

Dev/Stage environment: https://peekaboo.allizom.org

Filing bugs
-----------

File bugs on bugzilla under [Webtools:Peekaboo](https://bugzilla.mozilla.org/enter_bug.cgi?product=Webtools&component=Peekaboo).

Getting Your Dev Environment Up
-------------------------------

First of you will need to clone this project (If you are planning on working on the
project and submitting pull requests, first fork this repo and clone your fork).

    git clone --init --recursive https://github.com/youruser/peekaboo.git && cd peekaboo

The next dependency you will need is MySQL, you can have a look at the download instructions at:
http://dev.mysql.com/downloads/ or, if you have brew installed, just run:

    brew install mysql

Once MySQL is installed, we need to create the database for peekaboo. If your instance of MySQL
is not already running, start it up.

Log into your MySQL instance using the username and password you have set, and create the DB:

    create database peekaboo;

Next step is to create and update your local settings to reflect this. From the root of your repo run:

    cp peekaboo/settings/local.py-dist peekaboo/settings/local.py

With an editor open up local.py and update the database credentials you will find at line 12 - 14.

Lastly install your remaining dependencies using pip:

    pip install -r requirements/dev.txt
    pip install -r requirements/compiled.txt

With all of this done, you are ready to move on to the next step below.


Setting up database
-------------------

From a blank newly created database with no tables, run:

``./manage.py syncdb --noinput``

followed by:

``./manage.py migrate peekaboo.main``

This will apply the migration ``migrations/0001_initial.py``. If you
haven't already created this file you first have to run:

``./manage.py schemamigration main --initial``

Migrations
----------

We're using [South](http://south.aeracode.org/) to handle database migrations.
To generate a schema migration, make changes to models.py, then run:

``./manage.py schemamigration peekaboo.main --auto``

To generate a blank data migration, use:

``./manage.py datamigration peekaboo.main data_migration_name``

Then fill in the generated file with logic, fixtures, etc.

To apply migrations:

``./manage.py migrate peekaboo.main``

In each command, replace peekaboo.main with the appropriate app.


Setting up superusers
---------------------

To be able to get any access you need to be a staff user or a superuser.

Only superusers can decide who can be staff and superuser. To
bootstrap, if there are no superusers available at all, you can create
one like this::

    ./manage.py make-superuser pbengtsson@mozilla.com


What's deployed
---------------

To find out what commits have made it where, use the
[Whatsdeployed tool for
peekaboo](https://whatsdeployed.paas.allizom.org/?owner=mozilla&repo=peekaboo&name[]=Stage&url[]=https%3A%2F%2Fpeekaboo.allizom.org%2Fmedia%2Frevision.txt&name[]=Prod&url[]=https%3A%2F%2Fpeekaboo.mozilla.org%2Fmedia%2Frevision.txt).

Stackato
--------

To use [stackato](http://api.stacka.to/docs/) you need to be log in and then you can
simply run::

    $ stackato push -n

Note: If it's already registered under that name you need to override
the name with something else.

If you make changes to the stackato.yml file run::

    $ stackato update -n

License
-------

This software is licensed under the
[Mozilla Public License v. 2.0](http://mozilla.org/MPL/2.0/).
For more
information, read the file ``LICENSE``.
