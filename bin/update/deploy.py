"""
Deploy this project in dev/stage/production.

Requires commander_ which is installed on the systems that need it.

.. _commander: https://github.com/oremj/commander
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from commander.deploy import task
import commander_settings as settings

venv_path = '../venv'
py_path = venv_path + '/bin/python'


@task
def update_code(ctx, tag):
    """Update the code to a specific git reference (tag/sha/etc)."""
    with ctx.lcd(settings.SRC_DIR):
        ctx.local('git fetch')
        ctx.local('git checkout -f %s' % tag)
        ctx.local("find . -type f -name '*.pyc' -delete")

        # Creating a virtualenv tries to open virtualenv/bin/python for
        # writing, but because virtualenv is using it, it fails.
        # So we delete it and let virtualenv create a new one.
        ctx.local('rm -f {}/bin/python {}/bin/python2.7'.format(
            venv_path,
            venv_path,
        ))
        ctx.local('virtualenv-2.7 {}'.format(venv_path))

        # Activate virtualenv to append to path.
        activate_env = os.path.join(
            settings.SRC_DIR, venv_path, 'bin', 'activate_this.py'
        )
        execfile(activate_env, dict(__file__=activate_env))

        ctx.local('{}/bin/pip install bin/peep-2.*.tar.gz'.format(venv_path))
        ctx.local('{}/bin/peep install -r requirements.txt'.format(venv_path))
        ctx.local('virtualenv-2.7 --relocatable {}'.format(venv_path))

        ctx.local('./bin/peep install -r requirements.txt')


@task
def update_assets(ctx):
    with ctx.lcd(settings.SRC_DIR):
        ctx.local('{} manage.py collectstatic --noinput'.format(py_path))


@task
def update_db(ctx):
    """Update the database schema, if necessary."""

    with ctx.lcd(settings.SRC_DIR):
        ctx.local(
            '{}/bin/python manage.py migrate'.format(py_path)
        )


@task
def install_cron(ctx):
    """Use gen-crons.py method to install new crontab.

    Ops will need to adjust this to put it in the right place.

    """
    with ctx.lcd(settings.SRC_DIR):
        ctx.local(
            '{} ./bin/crontab/gen-crons.py -w {} -u apache > '
            '/etc/cron.d/.{}'.format(
                py_path,
                settings.SRC_DIR,
                settings.CRON_NAME
            )
        )
        ctx.local(
            'mv /etc/cron.d/.{} /etc/cron.d/{}'.format(
                settings.CRON_NAME,
                settings.CRON_NAME
            )
        )


@task
def deploy_app(ctx):
    """Call the remote update script to push changes to webheads."""
    ctx.local('/bin/touch %s' % settings.LOCAL_WSGI)


@task
def update_info(ctx):
    """Write info about the current state to a publicly visible file."""
    with ctx.lcd(settings.SRC_DIR):
        ctx.local('date')
        ctx.local('git branch')
        ctx.local('git log -3')
        ctx.local('git status')
        ctx.local('git submodule status')
        ctx.local('git rev-parse HEAD > media/revision.txt')


@task
def pre_update(ctx, ref=settings.UPDATE_REF):
    """Update code to pick up changes to this file."""
    update_code(ref)


@task
def update(ctx):
    update_assets()
    # update_locales()  # commented out till we switch on i18n
    update_db()


@task
def deploy(ctx):
    install_cron()
    deploy_app()
    update_info()


@task
def update_site(ctx, tag):
    """Update the app to prep for deployment."""
    pre_update(tag)
    update()
