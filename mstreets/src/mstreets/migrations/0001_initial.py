# Generated by Django 3.2 on 2022-06-03 10:27

import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Campaign',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True, verbose_name='Activa')),
                ('name', models.CharField(max_length=255, verbose_name='Nom de la campanya')),
                ('date_start', models.DateField(verbose_name='Data inici')),
                ('date_fi', models.DateField(verbose_name='Data fi')),
                ('folder_pano', models.CharField(blank=True, max_length=1000, null=True, verbose_name='Ruta panorames')),
                ('folder_img', models.CharField(blank=True, max_length=1000, null=True, verbose_name='Ruta imatges')),
                ('folder_pc', models.CharField(blank=True, max_length=1000, null=True, verbose_name='Ruta núvols de punts')),
                ('config', models.JSONField(blank=True, null=True, verbose_name='Configuració de la campanya')),
                ('geom', django.contrib.gis.db.models.fields.MultiPolygonField(db_index=True, srid=4326, verbose_name='Perímetre campanya')),
            ],
            options={
                'verbose_name': 'Campanya',
                'verbose_name_plural': '    Campanyes',
            },
        ),
        migrations.CreateModel(
            name='Config',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('variable', models.CharField(max_length=255, verbose_name='Nom variable')),
                ('value', models.CharField(max_length=1000, verbose_name='Valor')),
                ('description', models.CharField(max_length=1000, verbose_name='Descripció variable')),
            ],
            options={
                'verbose_name': 'Config',
                'verbose_name_plural': '     Config',
            },
        ),
        migrations.CreateModel(
            name='Metadata',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sensor', models.CharField(help_text="Sensor làser amb el que s'ha realizat l'escaneig", max_length=255, verbose_name='Sensor')),
                ('precision', models.CharField(blank=True, help_text='Descripció de la precisió del resultat', max_length=1000, null=True, verbose_name='Precisió')),
                ('company', models.CharField(blank=True, help_text='Empresa o empreses que han realizat la captura', max_length=255, null=True, verbose_name='Empresa')),
                ('contact', models.CharField(blank=True, help_text="Contacte de l'empresa o empreses (web, email...)", max_length=255, null=True, verbose_name='Contact')),
            ],
            options={
                'verbose_name': 'Metadades',
                'verbose_name_plural': '   Metadades',
            },
        ),
        migrations.CreateModel(
            name='Poi',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filename', models.CharField(blank=True, max_length=1000, null=True, verbose_name='Nom fitxer')),
                ('format', models.CharField(blank=True, max_length=10, null=True, verbose_name='Format fitxer')),
                ('type', models.CharField(choices=[('PANO', 'PANO'), ('IMG', 'IMG'), ('ELEVATION', 'ELEVATION')], max_length=10, verbose_name='Tipus de punt')),
                ('date', models.DateTimeField(verbose_name='Data i hora captura')),
                ('altitude', models.FloatField(verbose_name='Altura (Z)')),
                ('roll', models.FloatField(blank=True, verbose_name='Roll')),
                ('pitch', models.FloatField(blank=True, verbose_name='Pitch')),
                ('pan', models.FloatField(blank=True, verbose_name='Pan')),
                ('folder', models.CharField(blank=True, max_length=1000, null=True, verbose_name='Ruta')),
                ('tag', models.CharField(blank=True, max_length=255, null=True, verbose_name='Tag')),
                ('config', models.JSONField(blank=True, null=True, verbose_name='Configuració del POI')),
                ('geom', django.contrib.gis.db.models.fields.PointField(db_index=True, srid=4326, verbose_name='Geometria')),
                ('campaign', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mstreets.campaign')),
            ],
            options={
                'verbose_name': "Punt d'interès",
                'verbose_name_plural': "  Punts d'interès",
            },
        ),
        migrations.CreateModel(
            name='Zone',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Nom de la zona')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Descripción de la zona')),
                ('active', models.BooleanField(default=True, verbose_name='Activa')),
                ('folder_pano', models.CharField(blank=True, max_length=1000, null=True, verbose_name='Ruta panorames')),
                ('folder_img', models.CharField(blank=True, max_length=1000, null=True, verbose_name='Ruta imatges')),
                ('folder_pc', models.CharField(blank=True, max_length=1000, null=True, verbose_name='Ruta núvols de punts')),
                ('geom', django.contrib.gis.db.models.fields.MultiPolygonField(db_index=True, srid=4326, verbose_name='Perímetre zona')),
            ],
            options={
                'verbose_name': 'Zona',
                'verbose_name_plural': '     Zones',
            },
        ),
        migrations.CreateModel(
            name='Poi_Resource',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filename', models.CharField(max_length=1000, verbose_name='Nom fitxer')),
                ('format', models.CharField(max_length=10, verbose_name='Format')),
                ('pan', models.FloatField(blank=True, null=True, verbose_name='Orientació respecte panorama')),
                ('pitch', models.FloatField(blank=True, null=True, verbose_name='Inclinació vertical respecte panorama')),
                ('folder', models.CharField(blank=True, max_length=1000, null=True, verbose_name='Ruta')),
                ('tag', models.CharField(blank=True, max_length=255, null=True, verbose_name='Tag')),
                ('campaign', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mstreets.campaign')),
                ('poi', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='resources', to='mstreets.poi')),
                ('zone', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mstreets.zone')),
            ],
            options={
                'verbose_name': 'Recurs auxiliar a un POI',
                'verbose_name_plural': 'Recursos auxiliars a POI',
            },
        ),
        migrations.CreateModel(
            name='Poi_Locations',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag', models.CharField(blank=True, max_length=255, null=True, verbose_name='Tag')),
                ('color', models.CharField(blank=True, max_length=15, null=True, verbose_name='Color')),
                ('geom', django.contrib.gis.db.models.fields.GeometryField(srid=4326, verbose_name='Geometria')),
                ('campaign', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mstreets.campaign')),
                ('zone', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mstreets.zone')),
            ],
            options={
                'verbose_name': 'Localització',
                'verbose_name_plural': ' Localitzacions',
            },
        ),
        migrations.AddField(
            model_name='poi',
            name='zone',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mstreets.zone'),
        ),
        migrations.CreateModel(
            name='PC',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Nom (visible usuari)')),
                ('filename', models.CharField(blank=True, max_length=1000, null=True, verbose_name='Nom fitxer')),
                ('is_local', models.BooleanField(default=False, verbose_name='Per entorn local')),
                ('is_downloadable', models.BooleanField(default=False, verbose_name='Descarregable')),
                ('format', models.CharField(choices=[('POTREE', 'POTREE'), ('POTREE2', 'POTREE2'), ('LAS', 'LAS'), ('POD', 'POD')], max_length=25, verbose_name='Tipus de punt')),
                ('folder', models.CharField(blank=True, max_length=1000, null=True, verbose_name='Ruta')),
                ('tag', models.CharField(blank=True, max_length=255, null=True, verbose_name='Tag')),
                ('config', models.JSONField(blank=True, null=True, verbose_name='Configuració del PC')),
                ('geom', django.contrib.gis.db.models.fields.PolygonField(db_index=True, srid=4326, verbose_name='Perímetre núvol de punts')),
                ('campaign', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mstreets.campaign')),
                ('zone', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mstreets.zone')),
            ],
            options={
                'verbose_name': 'Núvol de punts',
                'verbose_name_plural': '  Núvols de punts',
            },
        ),
        migrations.AddField(
            model_name='campaign',
            name='metadata',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='mstreets.metadata'),
        ),
        migrations.AddField(
            model_name='campaign',
            name='zone',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mstreets.zone'),
        ),
        migrations.CreateModel(
            name='Animation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Nom animació')),
                ('tag', models.CharField(blank=True, max_length=255, null=True, verbose_name='Tag')),
                ('geom_source', django.contrib.gis.db.models.fields.GeometryField(srid=4326, verbose_name='Localitzacions càmera')),
                ('geom_target', django.contrib.gis.db.models.fields.GeometryField(help_text='Ha de tenir la mateixa geometria i número de vèrtexs que localitzacions càmera', srid=4326, verbose_name='Localitzacions vista')),
                ('duration', models.IntegerField(blank=True, help_text='Temps en segons', null=True, verbose_name='Temps recorregut')),
                ('campaign', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mstreets.campaign')),
                ('zone', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mstreets.zone')),
            ],
            options={
                'verbose_name': 'Animació 3D',
                'verbose_name_plural': 'Animacions 3D',
            },
        ),
    ]
