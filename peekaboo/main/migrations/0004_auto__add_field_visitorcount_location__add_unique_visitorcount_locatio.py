# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'VisitorCount.location'
        db.add_column(u'main_visitorcount', 'location',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Location'], null=True),
                      keep_default=False)

        # Adding unique constraint on 'VisitorCount', fields ['location', 'year', 'day', 'month']
        db.delete_unique(u'main_visitorcount', ['year', 'day', 'month'])
        db.create_unique(u'main_visitorcount', ['location_id', 'year', 'day', 'month'])


    def backwards(self, orm):
        # Removing unique constraint on 'VisitorCount', fields ['location', 'year', 'day', 'month']
        db.delete_unique(u'main_visitorcount', ['location_id', 'year', 'day', 'month'])
        db.create_unique(u'main_visitorcount', ['year', 'day', 'month'])

        # Deleting field 'VisitorCount.location'
        db.delete_column(u'main_visitorcount', 'location_id')


    models = {
        u'main.location': {
            'Meta': {'object_name': 'Location'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '65'}),
            'timezone': ('django.db.models.fields.CharField', [], {'max_length': '250'})
        },
        u'main.visitor': {
            'Meta': {'object_name': 'Visitor'},
            'company': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 5, 16, 0, 0)'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job_title': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Location']"}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 5, 16, 0, 0)', 'db_index': 'True'}),
            'picture': ('sorl.thumbnail.fields.ImageField', [], {'max_length': '100'}),
            'visiting': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'})
        },
        u'main.visitorcount': {
            'Meta': {'unique_together': "(('day', 'month', 'year', 'location'),)", 'object_name': 'VisitorCount'},
            'count': ('django.db.models.fields.IntegerField', [], {}),
            'day': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Location']", 'null': 'True'}),
            'month': ('django.db.models.fields.IntegerField', [], {}),
            'year': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['main']
