# Generated by Django 3.0.3 on 2020-05-10 02:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('museum_site', '0028_auto_20191227_0408'),
    ]

    operations = [
        migrations.CreateModel(
            name='Zeta_Config',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('executable', models.CharField(blank=True, default='/static/data/zeta86_engines/zzt.zip', max_length=128)),
                ('arguments', models.CharField(blank=True, default='', max_length=128)),
                ('comamnds', models.CharField(blank=True, default='', max_length=256)),
                ('blink_duration', models.DecimalField(decimal_places=3, default=0.466, max_digits=6)),
                ('charset', models.CharField(default='cp437', max_length=64)),
                ('audio_buffer', models.IntegerField(default=2048)),
                ('sample_rate', models.IntegerField(default=48000)),
                ('note_delay', models.IntegerField(default=1)),
                ('volume', models.DecimalField(decimal_places=2, default=0.2, max_digits=3)),
            ],
        ),
    ]
