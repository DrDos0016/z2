# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-08-16 03:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('museum_site', '0017_auto_20170415_0102'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='file',
            name='category',
        ),
        migrations.AlterField(
            model_name='file',
            name='article_count',
            field=models.IntegerField(default=0, help_text='Set automatically. Do not adjust.'),
        ),
        migrations.AlterField(
            model_name='file',
            name='review_count',
            field=models.IntegerField(default=0, help_text='Set automatically. Do not adjust.'),
        ),
    ]
