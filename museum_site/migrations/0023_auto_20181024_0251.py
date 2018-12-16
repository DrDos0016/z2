# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2018-10-24 02:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('museum_site', '0022_file_archive_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Alias',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('alias', models.CharField(max_length=80)),
            ],
        ),
        migrations.AddField(
            model_name='file',
            name='aliases',
            field=models.ManyToManyField(blank=True, default=None, to='museum_site.Alias'),
        ),
    ]