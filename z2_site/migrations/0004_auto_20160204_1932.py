# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-02-05 00:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('z2_site', '0003_auto_20160131_2349'),
    ]

    operations = [
        migrations.RenameField(
            model_name='file',
            old_name='released',
            new_name='release_date',
        ),
        migrations.RemoveField(
            model_name='article',
            name='file',
        ),
        migrations.AddField(
            model_name='file',
            name='articles',
            field=models.ManyToManyField(to='z2_site.Article'),
        ),
        migrations.AddField(
            model_name='file',
            name='release_source',
            field=models.CharField(default=None, max_length=20, null=True),
        ),
    ]
