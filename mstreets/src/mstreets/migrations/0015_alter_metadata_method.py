# Generated by Django 3.2 on 2024-05-17 14:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mstreets', '0014_auto_20240517_1422'),
    ]

    operations = [
        migrations.AlterField(
            model_name='metadata',
            name='method',
            field=models.SmallIntegerField(blank=True, choices=[(1, 'Avió'), (2, 'Helicòpter'), (3, 'Dron'), (4, 'Mobile Mapping'), (5, 'Estàtic'), (6, 'Altres')], null=True, verbose_name='Mètode de captura'),
        ),
    ]
