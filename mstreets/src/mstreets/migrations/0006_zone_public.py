# Generated by Django 3.2 on 2023-03-15 10:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mstreets', '0005_poi_has_mini'),
    ]

    operations = [
        migrations.AddField(
            model_name='zone',
            name='public',
            field=models.BooleanField(default=False, verbose_name='Públic'),
        ),
    ]
