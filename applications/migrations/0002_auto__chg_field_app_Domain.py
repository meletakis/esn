# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'App.Domain'
        db.alter_column(u'applications_app', 'Domain_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['applications.Domain'], null=True))

    def backwards(self, orm):

        # User chose to not deal with backwards NULL issues for 'App.Domain'
        raise RuntimeError("Cannot reverse this migration. 'App.Domain' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'App.Domain'
        db.alter_column(u'applications_app', 'Domain_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['applications.Domain']))

    models = {
        u'applications.action': {
            'Meta': {'ordering': "('-timestamp',)", 'object_name': 'Action'},
            'action_object_content_type': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'app_action_object'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"}),
            'action_object_object_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'actor_content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'app_actor'", 'to': u"orm['contenttypes.ContentType']"}),
            'actor_object_id': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'data': ('jsonfield.fields.JSONField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'target_content_type': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'app_target'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"}),
            'target_object_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'verb': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'applications.app': {
            'Author_email': ('django.db.models.fields.EmailField', [], {'max_length': '70'}),
            'Description': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'Domain': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['applications.Domain']", 'null': 'True', 'blank': 'True'}),
            'Meta': {'object_name': 'App'},
            'Name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'Source_code_host': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'responsibility': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['responsibilities.Responsibility']"})
        },
        u'applications.data': {
            'App': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['applications.App']"}),
            'Data_Type': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '50'}),
            'Domain': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['applications.Domain']"}),
            'Expiration_period': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'Meta': {'object_name': 'Data'},
            'Name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'Required': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'Semantics': ('jsonfield.fields.JSONField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'applications.domain': {
            'Description': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'Meta': {'object_name': 'Domain'},
            'Name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'applications.ioregistry': {
            'App': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['applications.App']"}),
            'Data': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['applications.Data']"}),
            'Meta': {'object_name': 'IORegistry'},
            'Type': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'responsibilities.responsibility': {
            'Meta': {'object_name': 'Responsibility'},
            'Name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['applications']