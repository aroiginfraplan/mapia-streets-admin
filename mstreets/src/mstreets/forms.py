from django import forms
from django.contrib.admin import widgets

from mstreets.models import Campaign, Config, Poi, Zone


config_help_text = {
    'api_url': 'URL de la API de MapiaStreets que gestiona les dades de l\'aplicació',
    'api_info_url': 'URL de la API per obtenir informació extra d\'un punt o panorama',
    'folder_poi': 'Ubicació fitxers punts d\'interés (panorames, imatges...)',
    'folder_img': 'Ubicació fitxers imatges',
    'folder_pc': 'Ubicació fitxers núvols de punts',
    'page_panellum': 'Component vista panorama de MapiaStreets',
    'page_no_img': 'Imatge a mostrar quan no existeix el fitxer panorama',
    'page_potree': 'Component vista núvol de punts de MapiaStreets',
    'wms_locations': 'Ruta WMS de les ubicacions de l\'aplicació',
    'wms_zones': 'Ruta WMS amb les zones',
    'wms_campaigns': 'Ruta WMS amb les campanyes',
    'epsg_pc': 'Sistema de coordenades dels fitxers de núvols de punts',
    'radius': 'Radi de cerca inicial en la API de panorames',
    'camera_height': 'Alçada de la càmera de captura de panorames respecte el terra (valor 8m)',
    'hotspots_add': 'Si volem mostrar o no els hotspots als panorames',
    'hotspots_dist_min': 'Distància mínima a partir de la qual mostrarem els hotspots (4m)',
    'hotspots_dist_max': 'Distància màxima fins la que mostrarem hotspots (25m)',
    'hotspots_height_max': 'Dif. de elevació màxima fins la que mostrarem els hotspots (3m)',
    'pc_ini_color': 'Color inicial al visualizar el núvol de punts',
    'pc_ini_point_size': 'Mida del punt inicial al núvol de punts',
    'category': 'Categoria dels elements. Serveix per agrupar elements en llistes, per exemple els núvols de punts en la llista de capes',
}


class DefaultConfigForm(forms.ModelForm):
    api_url = forms.CharField(
        required=True, help_text=config_help_text['api_url'], widget=forms.Textarea(attrs={'cols': 150, 'rows': 1})
    )
    api_info_url = forms.CharField(
        required=True, help_text=config_help_text['api_info_url'], widget=forms.Textarea(attrs={'cols': 150, 'rows': 1})
    )
    folder_poi = forms.CharField(
        required=False, help_text=config_help_text['folder_poi'], widget=forms.Textarea(attrs={'cols': 150, 'rows': 1})
    )
    folder_img = forms.CharField(
        required=False, help_text=config_help_text['folder_img'], widget=forms.Textarea(attrs={'cols': 150, 'rows': 1})
    )
    folder_pc = forms.CharField(
        required=False, help_text=config_help_text['folder_pc'], widget=forms.Textarea(attrs={'cols': 150, 'rows': 1})
    )
    page_panellum = forms.CharField(
        required=True, help_text=config_help_text['page_panellum'], widget=forms.Textarea(attrs={'cols': 150, 'rows': 1})
    )
    page_no_img = forms.CharField(
        required=True, help_text=config_help_text['page_no_img'], widget=forms.Textarea(attrs={'cols': 150, 'rows': 1})
    )
    page_potree = forms.CharField(
        required=True, help_text=config_help_text['page_potree'], widget=forms.Textarea(attrs={'cols': 150, 'rows': 1})
    )
    wms_locations = forms.CharField(
        required=False, help_text=config_help_text['wms_locations'], widget=forms.Textarea(attrs={'cols': 150, 'rows': 1})
    )
    wms_zones = forms.CharField(
        required=False, help_text=config_help_text['wms_zones'], widget=forms.Textarea(attrs={'cols': 150, 'rows': 1})
    )
    wms_campaigns = forms.CharField(
        required=False, help_text=config_help_text['wms_campaigns'], widget=forms.Textarea(attrs={'cols': 150, 'rows': 1})
    )
    EPSG_CHOICES = (
        ('25830', '25830'),
        ('25831', '25831'),
        ('25832', '25832'),
    )
    epsg_pc = forms.ChoiceField(required=True, choices=EPSG_CHOICES, initial='25831', help_text=config_help_text['epsg_pc'])
    radius = forms.CharField(required=False, initial='50', help_text=config_help_text['radius'])
    camera_height = forms.CharField(required=False, initial='2.8', help_text=config_help_text['camera_height'])
    hotspots_add = forms.BooleanField(required=False, initial=True, help_text=config_help_text['hotspots_add'])
    hotspots_dist_min = forms.CharField(required=False, initial='4', help_text=config_help_text['hotspots_dist_min'])
    hotspots_dist_max = forms.CharField(required=False, initial='25', help_text=config_help_text['hotspots_dist_max'])
    hotspots_height_max = forms.CharField(required=False, initial='3', help_text=config_help_text['hotspots_height_max'])
    INI_COLOR_CHOICES = (
        ('rgba', 'rgba'),
        ('classification', 'classification'),
        ('intensity', 'intensity'),
        ('elevation', 'elevation'),
    )
    pc_ini_color = forms.ChoiceField(required=False, choices=INI_COLOR_CHOICES, initial='rgba', help_text=config_help_text['pc_ini_color'])
    pc_ini_point_size = forms.CharField(required=False, help_text=config_help_text['pc_ini_point_size'])
    category = forms.CharField(required=False, initial='Data', help_text=config_help_text['category'])

    class Meta:
        model = Config
        fields = [
            'api_url', 'api_info_url', 'folder_poi', 'folder_img', 'folder_pc',
            'page_panellum', 'page_no_img', 'page_potree',
            'wms_locations', 'wms_zones', 'wms_campaigns',
            'epsg_pc', 'radius', 'camera_height',
            'hotspots_add', 'hotspots_dist_min', 'hotspots_dist_max', 'hotspots_height_max',
            'pc_ini_color', 'pc_ini_point_size', 'category'
        ]


class MultiplePoiForm(forms.ModelForm):
    TYPE_CHOICES = (
        ('PANO', 'PANO'),
        ('IMG', 'IMG'),
        ('ELEVATION', 'ELEVATION'),
    )

    folder = forms.CharField(label='Ruta', required=False)
    type = forms.ChoiceField(label='Tipus de punt', required=False, choices=TYPE_CHOICES)

    class Meta:
        model = Poi
        fields = ['folder', 'type']
        help_texts = {
            'valors_diferents': 'Group to which this message belongs to',
        }


poi_file_text = {
    'file_format': 'Format del fitxer',
    'file': 'Ruta del fitxer',
    'zone': 'Zona',
    'campaign': 'Campanya',
    'epsg': 'Input coord SRS',
    'x_translation': 'Translació X',
    'y_translation': 'Translació Y',
    'z_translation': 'Translació Z',
    'file_folder': 'Carpeta fitxers',
    'is_file_folder_prefix': 'Afegir \'Carpeta fitxers\' com prefix del nom del POI',
    'tag': 'Categoria',
    'date': 'Data i hora',
    'angle_format': 'Format angle',
    'pan_correction': 'Correcció asimut'
}


class DateTimePickerInput(forms.DateTimeInput):
    input_type = 'datetime'


class UploadPoiFileForm(forms.Form):
    FORMAT_CHOICES = (
        ('iml', 'IML'),
        ('csv', 'Infraplan CSV'),
        ('xyz', 'xyz'),
    )
    file_format = forms.ChoiceField(required=True, choices=FORMAT_CHOICES, initial='iml', label=poi_file_text['file_format'])
    file = forms.FileField(required=True, label=poi_file_text['file'])
    zone = forms.ModelChoiceField(required=True, queryset=Zone.objects.all(), label=poi_file_text['zone'])
    campaign = forms.ModelChoiceField(required=True, queryset=Campaign.objects.all(), label=poi_file_text['campaign'])
    EPSG_CHOICES = (
        ('4326', 'EPSG: 4326'),
        ('25830', 'EPSG: 25830'),
        ('25831', 'EPSG: 25831'),
        ('25832', 'EPSG: 25832'),
    )
    epsg = forms.ChoiceField(
        required=True, choices=EPSG_CHOICES, initial='25831', label=poi_file_text['epsg']
    )
    x_translation = forms.IntegerField(required=False, initial=0, label=poi_file_text['x_translation'])
    y_translation = forms.IntegerField(required=False, initial=0, label=poi_file_text['y_translation'])
    z_translation = forms.IntegerField(required=False, initial=0, label=poi_file_text['z_translation'])
    file_folder = forms.CharField(required=False, label=poi_file_text['file_folder'])
    is_file_folder_prefix = forms.BooleanField(
        required=False, initial=False, label=poi_file_text['is_file_folder_prefix']
    )
    tag = forms.CharField(required=False, label=poi_file_text['tag'])
    date = forms.SplitDateTimeField(
        required=True,
        label=poi_file_text['date'],
        widget=widgets.AdminSplitDateTime()
    )
    ANGLE_FORMATS = (
        ('sex', 'Sexa.'),
        ('rad', 'Radians'),
        ('gra', 'Gradians'),
        ('vec', 'Vector'),
    )
    angle_format = forms.ChoiceField(
        required=True, choices=ANGLE_FORMATS, initial='Sex', label=poi_file_text['angle_format']
    )
    pan_correction = forms.IntegerField(
        required=False, initial=0, label=poi_file_text['pan_correction']
    )

    class Media:
        css = {
            'all': (
                '/static/admin/css/widgets.css',
            )
        }
        js = [
            '/static/admin/js/core.js',
        ]