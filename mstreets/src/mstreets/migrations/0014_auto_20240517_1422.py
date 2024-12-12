# Generated by Django 3.2 on 2024-05-17 14:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mstreets', '0013_auto_20240515_1331'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='campaign_category',
            options={'verbose_name': 'Categoria de campanya', 'verbose_name_plural': '   Categories de campanya'},
        ),
        migrations.AddField(
            model_name='metadata',
            name='method',
            field=models.CharField(blank=True, choices=[(1, 'Avió'), (2, 'Helicòpter'), (3, 'Dron'), (4, 'Mobile Mapping'), (5, 'Estàtic'), (6, 'Altres')], max_length=5, null=True, verbose_name='Mètode de captura'),
        ),
    ]