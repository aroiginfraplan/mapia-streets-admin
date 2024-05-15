# Generated by Django 3.2 on 2024-05-15 13:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mstreets', '0012_alter_pc_geom'),
    ]

    operations = [
        migrations.CreateModel(
            name='Campaign_Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Nom')),
                ('order', models.SmallIntegerField(blank=True, null=True, verbose_name='Ordre')),
            ],
        ),
        migrations.AddField(
            model_name='campaign',
            name='default',
            field=models.BooleanField(default=True, verbose_name='Per defecte'),
        ),
        migrations.AddField(
            model_name='campaign',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='mstreets.campaign_category', verbose_name='Categoria'),
        ),
    ]
