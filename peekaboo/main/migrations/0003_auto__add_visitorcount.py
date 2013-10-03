# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'VisitorCount'
        db.create_table('main_visitorcount', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('count', self.gf('django.db.models.fields.IntegerField')()),
            ('day', self.gf('django.db.models.fields.IntegerField')()),
            ('month', self.gf('django.db.models.fields.IntegerField')()),
            ('year', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('main', ['VisitorCount'])


    def backwards(self, orm):
        # Deleting model 'VisitorCount'
        db.delete_table('main_visitorcount')


    models = {
        'main.location': {
            'Meta': {'object_name': 'Location'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '65'}),
            'timezone': ('django.db.models.fields.CharField', [], {'max_length': '250'})
        },
        'main.visitor': {
            'Meta': {'object_name': 'Visitor'},
            'company': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 10, 3, 0, 0)'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job_title': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Location']"}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 10, 3, 0, 0)', 'db_index': 'True'}),
            'picture': ('sorl.thumbnail.fields.ImageField', [], {'max_length': '100'}),
            'visiting': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'})
        },
        'main.visitorcount': {
            'Meta': {'object_name': 'VisitorCount'},
            'count': ('django.db.models.fields.IntegerField', [], {}),
            'day': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'month': ('django.db.models.fields.IntegerField', [], {}),
            'year': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['main']