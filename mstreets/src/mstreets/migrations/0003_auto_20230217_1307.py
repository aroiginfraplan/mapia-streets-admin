# Generated by Django 3.2 on 2023-02-17 13:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mstreets', '0002_auto_20230217_1303'),
    ]

    operations = [
        migrations.RenameField(
            model_name='campaign',
            old_name='zone',
            new_name='zones',
        ),
        migrations.AlterField(
            model_name='campaign',
            name='config',
            field=models.JSONField(blank=True, null=True, verbose_name='Configuració de la campanya (JSON)'),
        ),
    ]
