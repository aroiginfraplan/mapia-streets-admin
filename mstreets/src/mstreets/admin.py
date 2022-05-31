from django.contrib import admin
from django.forms import BaseModelFormSet

from django_vue_tabs.admin import TabsMixin

from mstreets.models import Animation, PC, Campaign, Config, Metadata, Poi, Poi_Locations, Poi_Resource, Zone


@admin.register(Config)
class ConfigAdmin(admin.ModelAdmin):
    list_display = ['variable', 'value']


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
    tabs = (
        ("Dades generals", ('tab-dades_generals', )),
        ("Geometria", ('tab-geom',)),
    )


@admin.register(Metadata)
class MetadataAdmin(admin.ModelAdmin):
    pass


@admin.register(Campaign)
class CampaignAdmin(TabsMixin, admin.ModelAdmin):
    list_display = ['name', 'zone', 'folder_pano', 'folder_img', 'folder_pc']
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


# class Poi_ResourceInlineFormset(BaseModelFormSet):
#     def save_new_objects(self, commit=True):
#         saved_instances = super(Poi_ResourceInlineFormset, self).save_new_objects(commit)
#         if commit:
#             for index, saved_instance in enumerate(saved_instances):
#                 resource = saved_instance
#                 poi = Poi.objects.get(pk=resource.poi_id)
#                 print(poi)
#                 resource.poi = poi
#                 resource.zone = poi.zone
#                 resource.campaign = poi.campaing
#                 saved_instance.save()
#                 saved_instances[index] = saved_instance
#         return saved_instances


class Poi_ResourceInlineMixin(admin.StackedInline):
    model = Poi_Resource
    # formset = Poi_ResourceInlineFormset
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
    list_display = ['filename', 'folder', 'zone', 'campaign']
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


@admin.register(Poi_Locations)
class Poi_LocationsAdmin(TabsMixin, admin.ModelAdmin):
    list_display = ['zone', 'campaign', 'tag']
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
