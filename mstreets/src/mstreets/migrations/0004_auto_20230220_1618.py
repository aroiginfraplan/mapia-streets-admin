# Generated by Django 3.2 on 2023-02-20 16:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mstreets', '0003_auto_20230217_1307'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='animation',
            name='campaign',
        ),
        migrations.RemoveField(
            model_name='pc',
            name='zone',
        ),
        migrations.RemoveField(
            model_name='poi',
            name='zone',
        ),
        migrations.RemoveField(
            model_name='poi_locations',
            name='zone',
        ),
        migrations.RemoveField(
            model_name='poi_resource',
            name='zone',
        ),
    ]
