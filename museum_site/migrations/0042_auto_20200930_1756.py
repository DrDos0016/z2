# Generated by Django 3.0.7 on 2020-09-30 17:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('museum_site', '0041_upload'),
    ]

    operations = [
        migrations.AlterField(
            model_name='upload',
            name='notes',
            field=models.TextField(blank=True),
        ),
    ]
