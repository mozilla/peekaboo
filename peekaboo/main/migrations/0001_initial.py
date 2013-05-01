# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Location'
        db.create_table('main_location', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=65)),
            ('timezone', self.gf('django.db.models.fields.CharField')(max_length=250)),
        ))
        db.send_create_signal('main', ['Location'])

        # Adding model 'Visitor'
        db.create_table('main_visitor', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('location', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Location'])),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=150, blank=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=150, blank=True)),
            ('job_title', self.gf('django.db.models.fields.CharField')(max_length=150, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('company', self.gf('django.db.models.fields.CharField')(max_length=250, blank=True)),
            ('visiting', self.gf('django.db.models.fields.CharField')(max_length=250, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 5, 1, 0, 0))),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 5, 1, 0, 0), db_index=True)),
            ('picture', self.gf('sorl.thumbnail.fields.ImageField')(max_length=100)),
        ))
        db.send_create_signal('main', ['Visitor'])


    def backwards(self, orm):
        # Deleting model 'Location'
        db.delete_table('main_location')

        # Deleting model 'Visitor'
        db.delete_table('main_visitor')


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
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 5, 1, 0, 0)'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job_title': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Location']"}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 5, 1, 0, 0)', 'db_index': 'True'}),
            'picture': ('sorl.thumbnail.fields.ImageField', [], {'max_length': '100'}),
            'visiting': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'})
        }
    }

    complete_apps = ['main']