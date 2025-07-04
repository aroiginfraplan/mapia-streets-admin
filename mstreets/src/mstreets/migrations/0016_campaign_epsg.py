# Generated by Django 3.2 on 2025-05-02 10:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mstreets', '0015_alter_metadata_method'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaign',
            name='epsg',
            field=models.CharField(choices=[('25829', 'EPSG:25829 - ETRS89 / UTM Zone 29N'), ('25830', 'EPSG:25830 - ETRS89 / UTM Zone 30N'), ('25831', 'EPSG:25831 - ETRS89 / UTM Zone 31N'), ('27563', 'EPSG:27563 - NTF (Paris) / Lambert Sud France'), ('4326', 'EPSG:4326 - WGS84')], default='25831', max_length=5, verbose_name='SRS'),
        ),
    ]
