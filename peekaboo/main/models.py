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


# The reason this function is not *inside* _upload_path() is
# because of migrations.
def _upload_path_tagged(tag, instance, filename):
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


def _upload_path_visitors(instance, filename):
    return _upload_path_tagged('visitors', instance, filename)


class Visitor(models.Model):
    location = models.ForeignKey(Location, db_index=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    job_title = models.CharField(max_length=150, blank=True)
    company = models.CharField(max_length=250, blank=True)
    visiting = models.CharField(max_length=250, blank=True)
    created = models.DateTimeField(default=_now)
    modified = models.DateTimeField(default=_now, db_index=True)
    picture = ImageField(upload_to=_upload_path_visitors)

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


class VisitorCount(models.Model):
    count = models.IntegerField()
    day = models.IntegerField()
    month = models.IntegerField()
    year = models.IntegerField()
    # the reason for allowing `null=True` here is because of legacy
    # see https://bugzilla.mozilla.org/show_bug.cgi?id=1011556
    location = models.ForeignKey(Location, null=True)

    class Meta:
        unique_together = ('day', 'month', 'year', 'location')

    def __repr__(self):
        return (
            '<%s: %d (%d/%d/%d)>' % (
                self.__class__.__name__,
                self.count,
                self.year,
                self.month,
                self.day,
            )
        )

    @classmethod
    def create_from_visitor(self, visitor):
        day = visitor.created.day
        month = visitor.created.month
        year = visitor.created.year
        try:
            record = VisitorCount.objects.get(
                day=day,
                month=month,
                year=year,
                location=visitor.location
            )
            record.count += 1
            record.save()
            return record
        except VisitorCount.DoesNotExist:
            return VisitorCount.objects.create(
                count=1,
                day=day,
                month=month,
                year=year,
                location=visitor.location
            )
