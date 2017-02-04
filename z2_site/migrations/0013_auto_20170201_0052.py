# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-02-01 00:52
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('z2_site', '0012_auto_20170112_0212'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='content_warning',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='file',
            name='checksum',
            field=models.CharField(blank=True, default='', max_length=32, null=True),
        ),
        migrations.AddField(
            model_name='file',
            name='superceded',
            field=models.ForeignKey(db_column='superceded_id', default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='z2_site.File'),
        ),
        migrations.AlterField(
            model_name='article',
            name='parent',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='z2_site.Article'),
        ),
        migrations.AlterField(
            model_name='file',
            name='category',
            field=models.CharField(choices=[('ZZT', 'ZZT World'), ('ZZM', 'ZZM Soundtrack'), ('ZIG', 'ZIG World'), ('Utility', 'External Utility'), ('SZZT', 'Super ZZT World'), ('Etc', 'Etc.')], max_length=10),
        ),
    ]
