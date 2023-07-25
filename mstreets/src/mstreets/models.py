from django.contrib.auth.models import Group
from django.contrib.gis.db import models
from django.utils.translation import gettext as _


class Config(models.Model):
    variable = models.CharField('Nom variable', max_length=255, null=False, blank=False)
    value = models.CharField('Valor', max_length=1000, null=False, blank=False)
    description = models.CharField('Descripció variable', max_length=1000, null=False, blank=False)

    class Meta:
        verbose_name = 'Config'
        verbose_name_plural = '     Config'


class Zone(models.Model):
    name = models.CharField('Nom de la zona', max_length=255, null=False, blank=False)
    description = models.TextField('Descripció de la zona', null=True, blank=True)
    active = models.BooleanField('Activa', default=True)
    folder_pano = models.CharField('Ruta panorames', max_length=1000, null=True, blank=True)
    folder_img = models.CharField('Ruta imatges', max_length=1000, null=True, blank=True)
    folder_pc = models.CharField('Ruta núvols de punts', max_length=1000, null=True, blank=True)
    public = models.BooleanField('Públic', default=False)
    poi_permission = models.BooleanField('Pot veure POI', default=True, help_text="Pot veure els punts d'interès (panorames, laterals, etc) de la zona")
    pc_permission = models.BooleanField('Pot veure PC', default=True, help_text="Pot veure els núvols de punts de la zona")
    geom = models.MultiPolygonField('Perímetre zona', srid=4326, db_index=True, null=True, blank=True)

    class Meta:
        verbose_name = 'Permís territorial'
        verbose_name_plural = '     Permisos territorials'

    def __str__(self):
        return '%s' % self.name


class ZoneGroupPermission(models.Model):
    zone = models.ForeignKey(Zone, related_name='group_permissions', on_delete=models.CASCADE)
    group = models.ForeignKey(Group, verbose_name=_('Group'), on_delete=models.CASCADE)

    def __str__(self):
        return self.group.name

    class Meta:
        verbose_name = _('Group')
        verbose_name_plural = _('Groups')


class Metadata(models.Model):
    sensor = models.CharField(
        'Sensor', max_length=255, null=False, blank=False,
        help_text='Sensor làser amb el que s\'ha realizat l\'escaneig'
    )
    precision = models.CharField(
        'Precisió', max_length=1000, null=True, blank=True,
        help_text='Descripció de la precisió del resultat'
    )
    company = models.CharField(
        'Empresa', max_length=255, null=True, blank=True,
        help_text='Empresa o empreses que han realizat la captura'
    )
    contact = models.CharField(
        'Contact', max_length=255, null=True, blank=True,
        help_text='Contacte de l\'empresa o empreses (web, email...)'
    )

    class Meta:
        verbose_name = 'Metadades'
        verbose_name_plural = '   Metadades'

    def __str__(self):
        return '%s - %s' % (self.company, self.sensor)


class Campaign(models.Model):
    zones = models.ManyToManyField(Zone)
    metadata = models.ForeignKey(Metadata, on_delete=models.CASCADE, null=True, blank=True)
    active = models.BooleanField('Activa', default=True)
    name = models.CharField('Nom de la campanya', max_length=255, null=False, blank=False)
    date_start = models.DateField('Data inici', null=False, blank=False)
    date_fi = models.DateField('Data fi', null=False, blank=False)
    folder_pano = models.CharField('Ruta panorames', max_length=1000, null=True, blank=True)
    folder_img = models.CharField('Ruta imatges', max_length=1000, null=True, blank=True)
    folder_pc = models.CharField('Ruta núvols de punts', max_length=1000, null=True, blank=True)
    config = models.JSONField('Configuració de la campanya (JSON)', null=True, blank=True)
    geom = models.MultiPolygonField('Perímetre campanya', srid=4326, db_index=True, null=True, blank=True)

    class Meta:
        verbose_name = 'Campanya'
        verbose_name_plural = '    Campanyes'

    def __str__(self):
        return '%s' % self.name


class Poi(models.Model):
    TYPE_CHOICES = (
        ('PANO', 'PANO'),
        ('IMG', 'IMG'),
        ('ELEVATION', 'ELEVATION'),
    )

    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    filename = models.CharField('Nom fitxer', max_length=1000, null=True, blank=True)
    format = models.CharField('Format fitxer', max_length=10, null=True, blank=True)
    type = models.CharField('Tipus de punt', choices=TYPE_CHOICES, max_length=10, null=False, blank=False)
    date = models.DateTimeField('Data i hora captura', null=False, blank=False)
    altitude = models.FloatField('Altura (Z)', null=False, blank=False)
    roll = models.FloatField('Roll', null=False, blank=True)
    pitch = models.FloatField('Pitch', null=False, blank=True)
    pan = models.FloatField('Pan', null=False, blank=True)
    has_mini = models.BooleanField('Hi ha imatge reduida', default=False)
    folder = models.CharField('Ruta', max_length=1000, null=True, blank=True)
    tag = models.CharField('Tag', max_length=255, null=True, blank=True)
    config = models.JSONField('Configuració del POI', null=True, blank=True)
    geom = models.PointField('Geometria', srid=4326, db_index=True)

    class Meta:
        verbose_name = 'Punt d\'interès'
        verbose_name_plural = '  Punts d\'interès'

    def __str__(self):
        return '%s/%s' % (self.folder, self.filename)


class Poi_Resource(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    poi = models.ForeignKey(Poi, on_delete=models.CASCADE, related_name='resources')
    filename = models.CharField('Nom fitxer', max_length=1000, null=False, blank=False)
    format = models.CharField('Format', max_length=10, null=False, blank=False)
    pan = models.FloatField('Orientació respecte panorama', null=True, blank=True)
    pitch = models.FloatField('Inclinació vertical respecte panorama', null=True, blank=True)
    folder = models.CharField('Ruta', max_length=1000, null=True, blank=True)
    tag = models.CharField('Tag', max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = 'Recurs auxiliar a un POI'
        verbose_name_plural = 'Recursos auxiliars a POI'

    def __str__(self):
        return '%s/%s (%s)' % (self.folder, self.filename, self.poi)


class Poi_Locations(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    tag = models.CharField('Tag', max_length=255, null=True, blank=True)
    color = models.CharField('Color', max_length=15, null=True, blank=True)
    geom = models.GeometryField('Geometria')

    class Meta:
        verbose_name = 'Localització'
        verbose_name_plural = ' Localitzacions'

    def __str__(self):
        return '%s' % self.tag


class PC(models.Model):
    TYPE_CHOICES = (
        ('POTREE', 'POTREE'),
        ('POTREE2', 'POTREE2'),
        ('LAS', 'LAS'),
        ('POD', 'POD'),
    )

    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    name = models.CharField('Nom (visible usuari)', max_length=255, null=True, blank=True)
    filename = models.CharField('Nom fitxer', max_length=1000, null=True, blank=True)
    is_local = models.BooleanField('Per entorn local', default=False)
    is_downloadable = models.BooleanField('Descarregable', default=False)
    format = models.CharField('Tipus de punt', choices=TYPE_CHOICES, max_length=25, null=False, blank=False)
    folder = models.CharField('Ruta', max_length=1000, null=True, blank=True)
    tag = models.CharField('Tag', max_length=255, null=True, blank=True)
    config = models.JSONField('Configuració del PC', null=True, blank=True)
    geom = models.PolygonField('Perímetre núvol de punts', srid=4326, db_index=True)

    class Meta:
        verbose_name = 'Núvol de punts'
        verbose_name_plural = '  Núvols de punts'

    def __str__(self):
        return '%s' % self.name


class Animation(models.Model):
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE)
    name = models.CharField('Nom animació', max_length=255, null=False, blank=False)
    tag = models.CharField('Tag', max_length=255, null=True, blank=True)
    geom_source = models.GeometryField('Localitzacions càmera', srid=4326)
    geom_target = models.GeometryField(
        'Localitzacions vista', srid=4326,
        help_text='Ha de tenir la mateixa geometria i número de vèrtexs que localitzacions càmera')
    duration = models.IntegerField('Temps recorregut', help_text='Temps en segons', null=True, blank=True)

    class Meta:
        verbose_name = 'Animació 3D'
        verbose_name_plural = 'Animacions 3D'

    def __str__(self):
        return '%s' % self.name
