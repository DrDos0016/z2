# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-02-01 04:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('museum_site', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Detail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('detail', models.CharField(max_length=20)),
            ],
        ),
        migrations.AddField(
            model_name='file',
            name='company',
            field=models.CharField(blank=True, default=b'', max_length=80),
        ),
        migrations.AddField(
            model_name='file',
            name='rating',
            field=models.FloatField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='file',
            name='details',
            field=models.ManyToManyField(to='museum_site.Detail'),
        ),
    ]
