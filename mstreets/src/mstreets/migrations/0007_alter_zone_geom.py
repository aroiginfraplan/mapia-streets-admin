# Generated by Django 3.2 on 2023-07-13 15:42

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mstreets', '0006_zone_public'),
    ]

    operations = [
        migrations.AlterField(
            model_name='zone',
            name='geom',
            field=django.contrib.gis.db.models.fields.MultiPolygonField(blank=True, db_index=True, null=True, srid=4326, verbose_name='Perímetre zona'),
        ),
    ]
