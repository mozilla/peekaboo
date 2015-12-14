# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import sorl.thumbnail.fields
import peekaboo.main.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=300)),
                ('slug', models.SlugField(unique=True, max_length=65)),
                ('timezone', models.CharField(max_length=250)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Visitor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('first_name', models.CharField(max_length=150, blank=True)),
                ('last_name', models.CharField(max_length=150, blank=True)),
                ('job_title', models.CharField(max_length=150, blank=True)),
                ('company', models.CharField(max_length=250, blank=True)),
                ('visiting', models.CharField(max_length=250, blank=True)),
                ('created', models.DateTimeField(default=peekaboo.main.models._now)),
                ('modified', models.DateTimeField(default=peekaboo.main.models._now, db_index=True)),
                ('picture', sorl.thumbnail.fields.ImageField(upload_to=peekaboo.main.models._upload_path_visitors)),
                ('location', models.ForeignKey(to='main.Location')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='VisitorCount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('count', models.IntegerField()),
                ('day', models.IntegerField()),
                ('month', models.IntegerField()),
                ('year', models.IntegerField()),
                ('location', models.ForeignKey(to='main.Location', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='visitorcount',
            unique_together=set([('day', 'month', 'year', 'location')]),
        ),
    ]
