from django.contrib import admin
from django.utils.translation import gettext as _

from django_admin_listfilter_dropdown.filters import DropdownFilter
from django_vue_tabs.admin import TabsMixin

from mstreets.models import (
    Animation, PC, Campaign, Config, Metadata, Poi, Poi_Locations, Poi_Resource, Zone, ZoneGroupPermission
)
from mstreets.actions import edit_multiple_poi


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
    list_display = ['name', 'folder_pano', 'folder_img', 'folder_pc']
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


@admin.register(Metadata)
class MetadataAdmin(admin.ModelAdmin):
    pass


@admin.register(Campaign)
class CampaignAdmin(TabsMixin, admin.ModelAdmin):
    list_display = ['name', 'zone', 'folder_pano', 'folder_img', 'folder_pc']
    list_filter = [('zone__name', DropdownFilter)]
    fieldsets = [
        (None, {
            'classes': ('tab-dades_generals',),
            'fields': [
                'name',
                'zone', 'metadata',
                ('date_start', 'date_fi',),
                'folder_pano',
                'folder_img',
                'folder_pc',
                'config',
                'active',
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
    change_list_template = 'admin/mstreets/poi/change_list.html'

    list_display = ['filename', 'folder', 'zone', 'campaign']
    actions = [edit_multiple_poi]
    list_filter = [
        ('zone__name', DropdownFilter),
        ('campaign__name', DropdownFilter),
    ]
    inlines = (Poi_ResourceInlineMixin,)
    fieldsets = [
        (None, {
            'classes': ('tab-dades_generals',),
            'fields': [
                ('zone', 'campaign',),
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
            instance.zone = instance.poi.zone
            instance.campaign = instance.poi.campaign
            instance.save()
        formset.save_m2m()


@admin.register(Poi_Locations)
class Poi_LocationsAdmin(TabsMixin, admin.ModelAdmin):
    list_display = ['tag', 'zone', 'campaign']
    list_filter = [
        ('zone__name', DropdownFilter),
        ('campaign__name', DropdownFilter),
    ]
    fieldsets = [
        (None, {
            'classes': ('tab-dades_generals',),
            'fields': [
                'zone',
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
    list_display = ['name', 'filename', 'zone', 'campaign']
    list_filter = [
        ('zone__name', DropdownFilter),
        ('campaign__name', DropdownFilter),
    ]
    fieldsets = [
        (None, {
            'classes': ('tab-dades_generals',),
            'fields': [
                'zone',
                'campaign',
                'name',
                ('folder', 'filename',),
                'is_local',
                'is_downloadable',
                'format',
                'tag',
                'config',
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


@admin.register(Animation)
class AnimationAdmin(TabsMixin, admin.ModelAdmin):
    list_display = ['name', 'zone', 'campaign']
    list_filter = [
        ('zone__name', DropdownFilter),
        ('campaign__name', DropdownFilter),
    ]
    fieldsets = [
        (None, {
            'classes': ('tab-dades_generals',),
            'fields': [
                'name',
                'zone',
                'campaign',
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
