# Generated by Django 3.0.7 on 2020-09-08 18:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('museum_site', '0039_wozzt_queue_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='company',
            field=models.CharField(blank=True, default='', max_length=80),
        ),
    ]