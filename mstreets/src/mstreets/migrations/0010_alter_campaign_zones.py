# Generated by Django 3.2 on 2023-07-25 10:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mstreets', '0009_auto_20230725_0804'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campaign',
            name='zones',
            field=models.ManyToManyField(to='mstreets.Zone', verbose_name='Permisos territorials'),
        ),
    ]
