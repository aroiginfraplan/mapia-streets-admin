from django.conf import settings
from django.contrib import admin
from django.contrib.gis.geos import GEOSGeometry
from django.utils.html import format_html
from django.utils.translation import gettext as _

from django_admin_listfilter_dropdown.filters import DropdownFilter
from django_vue_tabs.admin import TabsMixin

from mstreets.models import (
    Animation, PC, Campaign, Config, Metadata, Poi, Poi_Locations, Poi_Resource, Zone, ZoneGroupPermission
)
from mstreets.actions import edit_multiple_poi
from mstreets.forms import CampaignForm, PCForm, ZoneForm


@admin.register(Config)
class ConfigAdmin(admin.ModelAdmin):
    list_display = ['variable', 'description', 'value']
    change_list_template = 'admin/mstreets/config/change_list.html'

    def get_ordering(self, request):
        return ['id']


class ZoneGroupPermissionInline(admin.TabularInline):
    model = ZoneGroupPermission
    extra = 0
    classes = ('tab-permissions',)
    verbose_name = _('Group')
    verbose_name_plural = _('Groups')


@admin.register(Zone)
class ZoneAdmin(TabsMixin, admin.ModelAdmin):
    form = ZoneForm

    list_display = ['name', 'active_icon', 'poi_permission_icon', 'pc_permission_icon', 'public_icon']
    fieldsets = [
        (None, {
            'classes': ('tab-dades_generals',),
            'fields': [
                'name',
                'description',
                'active',
                'folder_pano',
                'folder_img',
                'folder_pc',
                'public',
                'poi_permission',
                'pc_permission',
                'wkt_geom',
            ]
        }),
        (None, {
            'classes': ('tab-geom',),
            'fields': [
                'geom',
            ]
        })
    ]
    inlines = (ZoneGroupPermissionInline,)
    tabs = (
        ("Dades generals", ('tab-dades_generals', )),
        (_('Permissions'), ('tab-permissions',)),
        ("Geometria", ('tab-geom',)),
    )

    def save_model(self, request, obj, form, change):
        wkt_geom = form.cleaned_data['wkt_geom'].strip() if form.cleaned_data['wkt_geom'] else False
        if wkt_geom:
            polygon = GEOSGeometry(wkt_geom, srid=4326)
            obj.geom = polygon
        obj.save()

    def get_icon(self, is_true):
        if is_true:
            return format_html(f'<img src="{settings.STATIC_URL}/admin/img/icon-yes.svg" alt="Consolidat">')
        else:
            return format_html(f'<img src="{settings.STATIC_URL}/admin/img/icon-no.svg" alt="Editat">')

    def active_icon(self, obj):
        return self.get_icon(obj.active)
    active_icon.short_description = 'Actiu'

    def poi_permission_icon(self, obj):
        return self.get_icon(obj.poi_permission)
    poi_permission_icon.short_description = 'Pot veure POI'

    def pc_permission_icon(self, obj):
        return self.get_icon(obj.pc_permission)
    pc_permission_icon.short_description = 'Pot veure PC'

    def public_icon(self, obj):
        return self.get_icon(obj.public)
    public_icon.short_description = 'Públic'


@admin.register(Metadata)
class MetadataAdmin(admin.ModelAdmin):
    pass


@admin.register(Campaign)
class CampaignAdmin(TabsMixin, admin.ModelAdmin):
    form = CampaignForm

    list_display = ['name', 'date_start', 'date_fi', 'active_icon']
    list_filter = [('zones__name', DropdownFilter)]
    filter_horizontal = ['zones']
    fieldsets = [
        (None, {
            'classes': ('tab-dades_generals',),
            'fields': [
                'name',
                'zones',
                'metadata',
                ('date_start', 'date_fi',),
                'folder_pano',
                'folder_img',
                'folder_pc',
                'config',
                'active',
                'wkt_geom',
            ]
        }),
        (None, {
            'classes': ('tab-geom',),
            'fields': [
                'geom',
            ]
        })
    ]
    tabs = (
        ("Dades generals", ('tab-dades_generals', )),
        ("Geometria", ('tab-geom',)),
    )

    @admin.display(description='Activa', ordering='active')
    def active_icon(self, obj):
        if obj.active:
            return format_html(f'<img src="{settings.STATIC_URL}/admin/img/icon-yes.svg">')
        else:
            return format_html(f'<img src="{settings.STATIC_URL}/admin/img/icon-no.svg">')

    def save_model(self, request, obj, form, change):
        wkt_geom = form.cleaned_data['wkt_geom'].strip() if form.cleaned_data['wkt_geom'] else False
        if wkt_geom:
            polygon = GEOSGeometry(wkt_geom, srid=4326)
            obj.geom = polygon
        obj.save()


class Poi_ResourceInlineMixin(admin.StackedInline):
    model = Poi_Resource
    extra = 0
    classes = ('tab-recursos',)
    fields = [
        'folder',
        'filename',
        'format',
        'pan',
        'pitch',
        'tag',
    ]


@admin.register(Poi)
class PoiAdmin(TabsMixin, admin.ModelAdmin):
    list_display = ['filename', 'folder', 'campaign']
    actions = [edit_multiple_poi]
    list_filter = [
        ('campaign__name', DropdownFilter),
        ('folder', DropdownFilter),
    ]
    inlines = (Poi_ResourceInlineMixin,)
    fieldsets = [
        (None, {
            'classes': ('tab-dades_generals',),
            'fields': [
                'campaign',
                ('folder', 'filename', 'format',),
                'type',
                'date',
                ('pan', 'roll', 'pitch',),
                'tag',
                'config',
            ]
        }),
        (None, {
            'classes': ('tab-geom',),
            'fields': [
                'altitude',
                'geom'
            ]
        })
    ]
    tabs = (
        ("Dades generals", ('tab-dades_generals', )),
        ("Recursos", ('tab-recursos', )),
        ("Geometria", ('tab-geom',)),
    )

    def save_formset(self, request, form, formset, change):
        if formset.model != Poi_Resource:
            return super(PoiAdmin, self).save_formset(request, form, formset, change)
        instances = formset.save(commit=False)
        for instance in instances:
            instance.campaign = instance.poi.campaign
            instance.save()
        formset.save_m2m()


@admin.register(Poi_Locations)
class Poi_LocationsAdmin(TabsMixin, admin.ModelAdmin):
    list_display = ['tag', 'campaign']
    list_filter = [
        ('campaign__name', DropdownFilter),
    ]
    fieldsets = [
        (None, {
            'classes': ('tab-dades_generals',),
            'fields': [
                'campaign',
                'tag',
                'color',
            ]
        }),
        (None, {
            'classes': ('tab-geom',),
            'fields': [
                'geom'
            ]
        })
    ]
    tabs = (
        ("Dades generals", ('tab-dades_generals', )),
        ("Geometria", ('tab-geom',)),
    )


@admin.register(PC)
class PCAdmin(TabsMixin, admin.ModelAdmin):
    form = PCForm

    list_display = ['name', 'filename', 'campaign']
    list_filter = [
        ('campaign__name', DropdownFilter),
    ]
    fieldsets = [
        (None, {
            'classes': ('tab-dades_generals',),
            'fields': [
                'campaign',
                'name',
                ('folder', 'filename',),
                'is_local',
                'is_downloadable',
                'format',
                'tag',
                'config',
                'wkt_geom',
            ]
        }),
        (None, {
            'classes': ('tab-geom',),
            'fields': [
                'geom',
            ]
        })
    ]
    tabs = (
        ("Dades generals", ('tab-dades_generals', )),
        ("Geometria", ('tab-geom',)),
    )

    def save_model(self, request, obj, form, change):
        wkt_geom = form.cleaned_data['wkt_geom'].strip() if form.cleaned_data['wkt_geom'] else False
        if wkt_geom:
            polygon = GEOSGeometry(wkt_geom, srid=4326)
            obj.geom = polygon
        obj.save()


@admin.register(Animation)
class AnimationAdmin(TabsMixin, admin.ModelAdmin):
    list_display = ['name', 'zone']
    list_filter = [
        ('zone__name', DropdownFilter),
    ]
    fieldsets = [
        (None, {
            'classes': ('tab-dades_generals',),
            'fields': [
                'name',
                'zone',
                'tag',
            ]
        }),
        (None, {
            'classes': ('tab-geom',),
            'fields': [
                ('geom_source', 'geom_target',)
            ]
        })
    ]
    tabs = (
        ("Dades generals", ('tab-dades_generals', )),
        ("Geometria", ('tab-geom',)),
    )
