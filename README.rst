Peek-a-boo
==========

Peek-a-boo! Who's visiting a Mozilla office?

Migrations
----------

We're using [South][south] to handle database migrations.
To generate a schema migration, make changes to models.py, then run:

``./manage.py schemamigration peekaboo.main --auto``

To generate a blank data migration, use:

``./manage.py datamigration peekaboo.main data_migration_name``

Then fill in the generated file with logic, fixtures, etc.

To apply migrations:

``./manage.py migrate peekaboo.main``

In each command, replace peekaboo.main with the appropriate app.



Stackato
--------

To use [stackato][stackto] you need to be log in and then you can
simply run::

    $ stackato push
    $ stackato start peekaboo

Note: If it's already registered under that name you need to override
the name with something else.

If you make changes to the stackato.yml file run::

    $ stackato update
    $ stackato restart peekaboo


License
-------

This software is licensed under the `Mozilla Public License v. 2.0`_. For more
information, read the file ``LICENSE``.

.. _Mozilla Public License v. 2.0: http://mozilla.org/MPL/2.0/


[south]: http://south.aeracode.org/
[stackto]: https://mana.mozilla.org/wiki/display/websites/Dev.Paas+Stackato+Cluster
