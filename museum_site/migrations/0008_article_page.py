# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-03-05 18:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('museum_site', '0007_article_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='page',
            field=models.IntegerField(default=1),
        ),
    ]
