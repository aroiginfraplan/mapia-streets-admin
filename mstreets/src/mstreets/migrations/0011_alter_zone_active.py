# Generated by Django 3.2 on 2023-07-25 10:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mstreets', '0010_alter_campaign_zones'),
    ]

    operations = [
        migrations.AlterField(
            model_name='zone',
            name='active',
            field=models.BooleanField(default=True, verbose_name='Actiu'),
        ),
    ]
