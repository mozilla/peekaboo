import os
import datetime
import hashlib
import unicodedata

from django.db import models
from django.utils.timezone import utc
from django.dispatch import receiver

from sorl.thumbnail import ImageField


def _now():
    return datetime.datetime.utcnow().replace(tzinfo=utc)


class Location(models.Model):
    name = models.CharField(max_length=300)
    slug = models.SlugField(max_length=65, unique=True, db_index=True)
    timezone = models.CharField(max_length=250)

    def __unicode__(self):
        return self.name


def _upload_path(tag):
    def _upload_path_tagged(instance, filename):
        if isinstance(filename, unicode):
            filename = (
                unicodedata
                .normalize('NFD', filename)
                .encode('ascii', 'ignore')
            )
        now = datetime.datetime.now()
        path = os.path.join(now.strftime('%Y'), now.strftime('%m'),
                            now.strftime('%d'))
        hashed_filename = (hashlib.md5(filename +
                           str(now.microsecond)).hexdigest())
        __, extension = os.path.splitext(filename)
        return os.path.join(tag, path, hashed_filename + extension)
    return _upload_path_tagged


class Visitor(models.Model):
    location = models.ForeignKey(Location, db_index=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    job_title = models.CharField(max_length=150, blank=True)
    company = models.CharField(max_length=250, blank=True)
    visiting = models.CharField(max_length=250, blank=True)
    created = models.DateTimeField(default=_now)
    modified = models.DateTimeField(default=_now, db_index=True)
    picture = ImageField(upload_to=_upload_path('visitors'))

    def get_name(self, formal=False):
        return ("%s %s" % (self.first_name, self.last_name)).strip()

    def __unicode__(self):
        return self.get_name()


@receiver(models.signals.pre_save, sender=Visitor)
def update_modified(sender, instance, raw, *args, **kwargs):
    if raw:
        return

    now = _now()
    if instance.modified < now:
        # only if it's not already been set
        instance.modified = now
