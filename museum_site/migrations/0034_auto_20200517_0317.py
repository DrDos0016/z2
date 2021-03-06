# Generated by Django 3.0.3 on 2020-05-17 03:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('museum_site', '0033_zeta_config_category'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='zeta_config',
            options={'ordering': ('category', 'name')},
        ),
        migrations.AlterField(
            model_name='zeta_config',
            name='category',
            field=models.CharField(choices=[(0, 'Recommended'), (1, 'Alternative'), (2, 'File Specific')], max_length=64),
        ),
    ]
