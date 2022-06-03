from django import forms

from mstreets.models import Config


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
