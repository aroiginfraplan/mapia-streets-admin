# Generated by Django 3.2 on 2023-07-27 11:52

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mstreets', '0011_alter_zone_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pc',
            name='geom',
            field=django.contrib.gis.db.models.fields.PolygonField(blank=True, db_index=True, null=True, srid=4326, verbose_name='Perímetre núvol de punts'),
        ),
    ]
