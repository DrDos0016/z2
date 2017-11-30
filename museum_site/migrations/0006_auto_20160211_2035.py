# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-02-12 01:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('museum_site', '0005_auto_20160207_1547'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Genre',
        ),
        migrations.AlterField(
            model_name='file',
            name='genre',
            field=models.CharField(blank=True, default=b'', max_length=80),
        ),
        migrations.AlterField(
            model_name='file',
            name='rating',
            field=models.FloatField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='file',
            name='release_source',
            field=models.CharField(blank=True, default=None, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='file',
            name='screenshot',
            field=models.CharField(blank=True, default=None, max_length=80, null=True),
        ),
    ]
